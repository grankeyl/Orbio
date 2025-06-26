from pydantic import BaseModel, Field
from datetime import datetime


class AdminPanelDTO(BaseModel):
    count_users: int = Field(..., description="Total number of users")
    count_all_gifts: int = Field(..., description="Total number of gifts ever created")
    count_completed_gifts: int = Field(..., description="Total number of completed (sold) gifts")
    count_active_gifts: int = Field(..., description="Total number of active (listed) gifts")
    trading_volume: float = Field(..., description="Total trading volume in TON")
    total_users_balance: float = Field(..., description="Sum of balances of all users in TON")
    nest_gifter_balance: float = Field(..., description="Balance of the Nest Gifter account in TON")


class AdminUserListItemDTO(BaseModel):
    id: int = Field(..., description="User ID")
    username: str | None = Field(None, description="Telegram username")
    first_name: str | None = Field(None, description="Telegram first name")
    balance: float = Field(..., description="User balance in TON")
    is_banned: bool = Field(..., description="Whether the user is banned")
    created_at: datetime = Field(..., description="Registration timestamp")
    referrals_count: int = Field(..., description="Number of users referred")


class AdminUserListDTO(BaseModel):
    users: list[AdminUserListItemDTO]
    total_count: int = Field(..., description="Total number of users matching filters") 