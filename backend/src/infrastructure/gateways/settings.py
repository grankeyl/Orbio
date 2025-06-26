from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.settings import Settings

class SettingsGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, data: dict) -> Settings:
        data["id"] = 1
        stmt = (
            pg_insert(Settings)
            .values(**data)
            .on_conflict_do_update(
                index_elements=[Settings.id],
                set_=data
            )
            .returning(Settings)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one()

    async def get_one(self) -> Settings:
        stmt = select(Settings).where(Settings.id == 1)
        result = await self._session.execute(stmt)
        return result.scalar_one()