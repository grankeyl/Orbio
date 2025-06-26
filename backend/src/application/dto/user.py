from src.application.dto.base import BaseDTO


class TokenDTO(BaseDTO):
    token: str


class UserDTO(BaseDTO):
    id: int
    photo_url: str | None = None
    username: str | None
    first_name: str | None
    balance: float
    commission: float
    deposit_comment: str
    referral_link: str
    language_code: str | None = None
    count_referrals: int
    custom_referral_percent: int | None = None

class ReferralDto(BaseDTO):
    id: int
    photo_url: str | None = None
    username: str | None
    first_name: str | None
    language_code: str | None = None

class LoginDTO(BaseDTO):
    init_data: str

class SellGiftDTO(BaseDTO):
    gift_id: int
    price: float

class UnsellGiftDTO(BaseDTO):
    gift_id: int

class WithdrawBalanceDTO(BaseDTO):
    amount: float
    address: str