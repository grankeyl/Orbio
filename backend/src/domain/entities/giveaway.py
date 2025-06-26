from datetime import datetime

from pydantic import BaseModel

from src.application.common.const import GiveawayType
from src.application.dto.base import BaseDTO
from src.domain.entities.market import UserGiftDM


class TelegramChannelDM(BaseModel):
    id: int
    title: str
    username: str
    image_url: str


class CreateGiveawayDM(BaseModel):
    type: GiveawayType
    gifts_ids: list[int]
    channels_usernames: list[str]
    quantity_members: int
    end_time: datetime
    price: float
    is_premium: bool
    participants_ids: list[int] = []
    winners_ids: list[int] = []
    referrers_ids: list[int] = []
    user_id: int


class GiveawayDM(CreateGiveawayDM):
    id: int
    message_ids: list[int] | None


class FullGiveawayDM(GiveawayDM):
    gifts: list[UserGiftDM]
    channels: list[TelegramChannelDM]
    tickets: int
    user_tickets: int


class GiveawayParticipantDM(BaseModel):
    id: int
    photo_url: str
    name: str | None
    chance_win: float
    count_referrals: int
    is_win: bool

class CreateTicketDM(BaseDTO):
    count: int
    giveaway_id: int
    user_id: int

class TicketDM(CreateTicketDM):
    id: int
    created_at: datetime