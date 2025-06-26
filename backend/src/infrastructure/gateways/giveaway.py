from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import insert, or_, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.giveaway import GiveawayReader, GiveawaySaver
from src.domain.entities.giveaway import CreateGiveawayDM, GiveawayDM, CreateTicketDM
from src.infrastructure.models.giveaway import Giveaway, Ticket


class GiveawayGateway(GiveawaySaver, GiveawayReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, data: CreateGiveawayDM) -> GiveawayDM:
        stmt = insert(Giveaway).values(data.model_dump()).returning(Giveaway)
        result = await self._session.execute(stmt)
        return GiveawayDM(**result.scalar_one().__dict__)

    async def update_giveaway(self, data: dict, **filters) -> GiveawayDM | None:
        stmt = update(Giveaway).values(data).filter_by(**filters).returning(Giveaway)
        result = await self._session.execute(stmt)
        if giveaway := result.scalar_one_or_none():
            return GiveawayDM(**giveaway.__dict__)

    async def get_one(self, **filters) -> GiveawayDM | None:
        stmt = select(Giveaway).filter_by(**filters)
        result = await self._session.execute(stmt)
        if giveaway := result.scalar_one_or_none():
            return GiveawayDM(**giveaway.__dict__)

    async def get_many(self, type: str, user_id: int) -> list[GiveawayDM]:
        conditions = [Giveaway.end_time > datetime.now(tz=timezone.utc)]
        if type == "user":
            conditions.append(
                or_(Giveaway.user_id == user_id, Giveaway.participants_ids.contains([user_id]))
            )

        stmt = select(Giveaway).where(*conditions).order_by(Giveaway.end_time)
        result = await self._session.execute(stmt)
        return [GiveawayDM(**giveaway.__dict__) for giveaway in result.scalars().all()]

    async def get_tickets_count(self, id: int, user_id: Optional[int] = None) -> int:
        conditions = [Ticket.giveaway_id == id]
        if user_id:
            conditions.append(Ticket.user_id == user_id)

        stmt = select(func.sum(Ticket.count)).where(*conditions)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none() or 0

    async def get_ended_giveaways(self) -> list[GiveawayDM]:
        stmt = select(Giveaway).where(
            datetime.now(tz=timezone.utc) > Giveaway.end_time, Giveaway.is_completed == False
        )
        result = await self._session.execute(stmt)
        return [GiveawayDM(**giveaway.__dict__) for giveaway in result.scalars().all()]

    async def save_tickets(self, data: CreateTicketDM) -> None:
        stmt = insert(Ticket).values(data.model_dump())
        await self._session.execute(stmt)