from sqlalchemy import func, insert, select, asc, desc, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.history import HistoryReader, HistorySaver
from src.domain.entities.history import ActivityDM, CreateHistoryDM, HistoryDM
from src.infrastructure.models.history import History


class HistoryGateway(HistoryReader, HistorySaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, data: CreateHistoryDM) -> HistoryDM:
        stmt = insert(History).values(data.model_dump()).returning(History)
        result = await self._session.execute(stmt)
        return HistoryDM(**result.scalar_one().__dict__)

    async def save_many(self, data: list[CreateHistoryDM]) -> None:
        stmt = insert(History).values([history.model_dump() for history in data])
        await self._session.execute(stmt)

    async def get_many(self, **filters) -> list[HistoryDM]:
        stmt = select(History).filter_by(**filters).order_by(History.created_at.desc())
        result = await self._session.execute(stmt)
        return [HistoryDM(**history.__dict__) for history in result.scalars().all()]

    async def get_activity(self, data: any, limit: int | None = None, offset: int | None = None) -> list[ActivityDM]:
        stmt = select(History)

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        if data.get('collection'):
            stmt = stmt.where(History.gift.in_(data.get('collection')))

        if data.get('sort_by') == 'latest':
            stmt = stmt.order_by(History.created_at.desc())
        elif data.get('sort_by') == 'price_low_to_high':
            stmt = stmt.order_by(asc(History.price))
        elif data.get('sort_by') == 'price_high_to_low':
            stmt = stmt.order_by(desc(History.price))
        elif data.get('sort_by') == 'random':
            stmt = stmt.order_by(func.random())
        else:
            stmt = stmt.order_by(History.created_at.desc())

        if data.get('number'):
            number = data.get('number')
            stmt = stmt.filter(cast(History.gift_number, String).like(f"%{number}%"))

        result = await self._session.execute(stmt)
        return [ActivityDM(**history.__dict__) for history in result.scalars().all()]
