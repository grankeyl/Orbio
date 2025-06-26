from src.application.dto.admin import AdminPanelDTO, AdminUserListDTO, AdminUserListItemDTO
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.user import UserReader
from src.application.interfaces.market import OrderReader
from src.entrypoint.config import Config


class GetAdminPanelDataInteractor(Interactor[None, AdminPanelDTO]):
    def __init__(
        self,
        user_gateway: UserReader,
        market_gateway: OrderReader,
        config: Config,
    ) -> None:
        self._user_gateway = user_gateway
        self._market_gateway = market_gateway
        self._config = config

    async def __call__(self) -> AdminPanelDTO:
        count_users = await self._user_gateway.get_count_users()
        total_users_balance = await self._user_gateway.get_sum_users_balance()
        
        # Assuming NEST_GIFTER_ID is in config.bot or a dedicated admin config section
        nest_gifter_id = getattr(self._config.bot, 'NEST_GIFTER_ID', None)
        nest_gifter_balance = 0.0
        if nest_gifter_id:
            nest_gifter_user = await self._user_gateway.get_by_id(nest_gifter_id)
            if nest_gifter_user:
                nest_gifter_balance = nest_gifter_user.balance
        else:
            # Log or handle the missing NEST_GIFTER_ID case
            print("Warning: NEST_GIFTER_ID not configured for admin panel data.")

        total_gifts, completed_gifts, active_gifts = await self._market_gateway.get_count_gifts()
        trading_volume = await self._market_gateway.get_total_trading_volume()

        return AdminPanelDTO(
            count_users=count_users,
            count_all_gifts=total_gifts,
            count_completed_gifts=completed_gifts,
            count_active_gifts=active_gifts,
            trading_volume=trading_volume,
            total_users_balance=total_users_balance,
            nest_gifter_balance=nest_gifter_balance,
        )


class GetAllUsersInteractor(Interactor[dict, AdminUserListDTO]):
    def __init__(
        self,
        user_gateway: UserReader,
    ) -> None:
        self._user_gateway = user_gateway

    async def __call__(self, pagination: dict) -> AdminUserListDTO:
        limit = pagination.get('limit')
        offset = pagination.get('offset')

        users_list_dm, total_count = await self._user_gateway.get_all_users(limit=limit, offset=offset)

        # Convert UserDM to AdminUserListItemDTO, fetching referrals count for each
        admin_users_list = []
        for user_dm in users_list_dm:
            # Get referrals count for each user
            referrals_count = await self._user_gateway.get_count_referrals(user_dm.id)
            
            admin_users_list.append(
                AdminUserListItemDTO(
                    id=user_dm.id,
                    username=user_dm.username,
                    first_name=user_dm.first_name,
                    balance=user_dm.balance,
                    is_banned=user_dm.is_banned,
                    created_at=user_dm.created_at,
                    referrals_count=referrals_count
                )
            )

        return AdminUserListDTO(users=admin_users_list, total_count=total_count) 