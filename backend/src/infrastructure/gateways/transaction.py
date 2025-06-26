from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.transaction import Lt


class TransactionGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_last_lt(self) -> int:
        stmt = select(Lt.last_lt).order_by(Lt.last_lt.desc())
        result = await self._session.execute(stmt)
        if row := result.first():
            return row[0]
        return 0

    async def set_new_lt(self, lt: int) -> None:
        lt_instance = Lt(last_lt=lt)
        await self._session.merge(lt_instance)
