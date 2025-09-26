from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.user import UserReader, UserSaver
from src.domain.entities.user import CreateUserDM, UpdateUserBalanceDM, UserDM, UserSettingsDM
from src.infrastructure.models.user import User, UserReferral


class UserGateway(UserReader, UserSaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> UserDM | None:
        stmt = select(User).filter_by(id=user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return UserDM(**user.__dict__)

    async def get_settings(self, user_id: int) -> UserSettingsDM:
        stmt = select(User).filter_by(id=user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user and user.settings:
            return UserSettingsDM(**user.settings)
        return UserSettingsDM()  # ✅ дефолт


    async def update_settings(self, user_id: int, settings: UserSettingsDM) -> UserSettingsDM | None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(settings=settings.model_dump())  # ✅ dict -> JSON
            .returning(User)
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user and user.settings:
            return UserSettingsDM(**user.settings)  # ✅ dict -> модель
        return None
    
    async def update_query(self, user_id: int, **query) -> UserDM | None:
        stmt = select(User).filter_by(id=user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        for key, value in query.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await self._session.commit()
        await self._session.refresh(user)

        return UserDM(**user.__dict__)
    
    async def get_by_username(self, username: str) -> UserDM | None:
        stmt = select(User).filter_by(username=username)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return UserDM(**user.__dict__)

    async def get_all(self) -> list[UserDM]:
        stmt = select(User)
        result = await self._session.execute(stmt)
        return [UserDM(**user.__dict__) for user in result.scalars().all()]

    async def get_sum_users_balance(self) -> float:
        stmt = select(func.sum(User.balance))
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def save(self, user: CreateUserDM) -> UserDM:
        stmt = insert(User).values(user.model_dump()).returning(User)
        result = await self._session.execute(stmt)
        new_user = result.scalar_one()
        return UserDM(**new_user.__dict__)

    async def update_user(self, data: dict, **filters) -> UserDM | None:
        stmt = update(User).values(data).filter_by(**filters).returning(User)
        result = await self._session.execute(stmt)
        new_user = result.scalar_one_or_none()
        if new_user:
            return UserDM(**new_user.__dict__)

    async def get_by_comment(self, comment: str) -> UserDM | None:
        stmt = select(User).filter_by(deposit_comment=comment)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return UserDM(**user.__dict__)

    async def update_balance(self, data: UpdateUserBalanceDM) -> UserDM | None:
        filter_by = {"deposit_comment": data.deposit_comment}
        if data.id:
            filter_by = {"id": data.id}
        stmt = (
            update(User)
            .filter_by(**filter_by)
            .values(balance=User.balance + data.amount)
            .returning(User)
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return UserDM(**user.__dict__)

    async def add_referral(self, referrer_id: int, referral: UserDM) -> bool:
        stmt = (
            insert(UserReferral)
            .values(referrer_id=referrer_id, referral_id=referral.id)
            .returning(UserReferral)
        )
        try:
            result = await self._session.execute(stmt)
        except IntegrityError:
            return False

        return not result.scalar_one().referrer.is_banned

    async def update_referrer(self, referrer_id: int, referral: UserDM) -> None:
        stmt = update(UserReferral).values(referrer_id=referrer_id).filter_by(referral_id=referral.id)
        await self._session.execute(stmt)

    async def update_referrer_balance(self, referrer_id: int, amount: float) -> None:
        stmt = (
            update(User)
            .values(balance=User.balance + amount, commission=User.commission + amount)
            .filter_by(id=referrer_id)
        )
        await self._session.execute(stmt)

    async def get_referrer(self, user_id: int) -> UserDM | None:
        stmt = select(UserReferral).filter_by(referral_id=user_id)
        result = await self._session.execute(stmt)
        user_referral = result.scalar_one_or_none()
        return UserDM(**user_referral.referrer.__dict__) if user_referral else None

    async def get_count_referrals(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(UserReferral).filter_by(referrer_id=user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_referrals(self, user_id: int, limit: int | None = None, offset: int | None = None) -> tuple[list[UserDM], int]:
        referral_ids_stmt = select(UserReferral.referral_id).filter_by(referrer_id=user_id)
        referral_ids_result = await self._session.execute(referral_ids_stmt)
        referral_ids = [row[0] for row in referral_ids_result.all()]

        if not referral_ids:
            return [], 0

        stmt = select(User).where(User.id.in_(referral_ids)).order_by(User.id.desc())
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        users_result = await self._session.execute(stmt)
        users_list = [UserDM(**user.__dict__) for user in users_result.scalars().all()]

        return users_list

    async def get_count_users(self) -> int:
        stmt = select(func.count()).select_from(User)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def set_custom_referral_percent(self, user_id: int, percent: int) -> UserDM | None:
        stmt = (
            update(User)
            .values(custom_referral_percent=percent)
            .filter_by(id=user_id)
            .returning(User)
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return UserDM(**user.__dict__)

    async def get_all_users(
        self, limit: int | None = None, offset: int | None = None
    ) -> tuple[list[UserDM], int]:
        """Fetch a paginated list of all users and the total count."""
        # Query for the list of users with pagination
        stmt_users = select(User).order_by(User.id)
        if limit:
            stmt_users = stmt_users.limit(limit)
        if offset:
            stmt_users = stmt_users.offset(offset)
        
        result_users = await self._session.execute(stmt_users)
        users_list = [UserDM(**user.__dict__) for user in result_users.scalars().all()]

        # Query for the total count of users
        stmt_count = select(func.count(User.id))
        result_count = await self._session.execute(stmt_count)
        total_count = result_count.scalar_one()

        return users_list, total_count
