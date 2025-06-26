from pydantic import BaseModel
from typing import Optional


class CreateWithdrawRequestDM(BaseModel):
    user_id: int
    amount: float
    wallet: str


class WithdrawRequestDM(CreateWithdrawRequestDM):
    id: int
    is_completed: bool = False
    error_message: Optional[str] = None
    has_error: bool | None = False
