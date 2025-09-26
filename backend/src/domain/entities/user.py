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


class UserSettingsDM(BaseModel):
    withdraw_gift_type: str = ""
    withdraw_gift_text: str = ""
    withdraw_money_type: str = ""
    withdraw_money_text: str = ""


class UserDM(BaseModel):
    id: int
    photo_url: str | None = None
    username: str | None
    first_name: str | None
    deposit_comment: str
    balance: float
    commission: float
    custom_referral_percent: int | None = None
    wallet_address: str | None = None
    created_at: datetime
    role: str
    is_freezed: bool = False
    is_banned: bool = False
    settings: UserSettingsDM


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
