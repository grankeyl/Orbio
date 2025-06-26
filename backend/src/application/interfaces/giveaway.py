from abc import abstractmethod
from typing import Protocol, Optional

from src.domain.entities.giveaway import CreateGiveawayDM, GiveawayDM, TicketDM, CreateTicketDM


class GiveawaySaver(Protocol):
    @abstractmethod
    async def save(self, data: CreateGiveawayDM) -> GiveawayDM: ...

    @abstractmethod
    async def update_giveaway(self, data: dict, **filters) -> GiveawayDM | None: ...


class GiveawayReader(Protocol):
    @abstractmethod
    async def get_one(self, **filters) -> GiveawayDM | None: ...

    @abstractmethod
    async def get_many(self, type: str, user_id: int) -> list[GiveawayDM]: ...

    @abstractmethod
    async def get_tickets_count(self, id: int, user_id: Optional[int] = None) -> int: ...


class GiveawayManager(GiveawaySaver, GiveawayReader):
    @abstractmethod
    async def save_tickets(self, data: CreateTicketDM) -> TicketDM: ...
