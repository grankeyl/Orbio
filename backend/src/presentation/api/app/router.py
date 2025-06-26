from fastapi import APIRouter
from pydantic import BaseModel  # ⬅ обязательно
from src.entrypoint.config import Config

app_router = APIRouter(prefix="/app", tags=["App"])


class AppVariablesDTO(BaseModel):
    wallet: str


@app_router.get("/variables", response_model=AppVariablesDTO)
async def get_app_variables() -> AppVariablesDTO:
    """Get app variables"""

    config = Config()
    return AppVariablesDTO(wallet=config.tonapi.DEPOSIT_ADDRESS)