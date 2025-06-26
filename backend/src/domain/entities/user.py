from datetime import datetime

from pydantic import BaseModel

from src.domain.entities.market import OrderDM
from src.domain.entities.wallet import WithdrawRequestDM


class CreateUserDM(BaseModel):
    id: int
    photo_url: str | None = None
    username: str | None
    first_name: str | None
    deposit_comment: str
    language_code: str | None


class UserDM(BaseModel):
    id: int
    photo_url: str | None = None
    username: str | None
    first_name: str | None
    deposit_comment: str
    balance: float
    commission: float
    is_banned: bool = False
    custom_referral_percent: int | None = None
    created_at: datetime


class UpdateUserBalanceDM(BaseModel):
    id: int | None = None
    deposit_comment: str | None = None
    amount: float


class FullUserInfoDM(UserDM):
    orders: list[OrderDM]
    withdraw_requests: list[WithdrawRequestDM]
    total_withdrawn: float
    referrals_count: int
    trading_volume: float
    active_gifts_count: int
