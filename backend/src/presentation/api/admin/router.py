from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException, Query, Header, responses
from starlette import status

from src.application.dto.admin import AdminPanelDTO, AdminUserListDTO
from src.application.interactors.admin import GetAdminPanelDataInteractor, GetAllUsersInteractor
from src.application.interfaces.auth import InitDataValidator
from src.application.interfaces.user import UserReader
from src.entrypoint.config import Config


admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# Dependency to validate Telegram Mini App initData and check admin status
@inject
async def verify_admin_auth(
    telegram_gateway: FromDishka[InitDataValidator],
    user_gateway: FromDishka[UserReader],
    config: FromDishka[Config],
    init_data: str | None = Header(None, alias="X-Telegram-Init-Data"),
) -> int:
    """
    Validates Telegram Mini App initData and checks if user is an admin.
    Returns the admin user ID if authentication and authorization succeed.
    """
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Telegram initData header"
        )
    
    try:
        # Validate the initData
        valid_data = telegram_gateway.validate_telegram_user(init_data)
        if not valid_data or not valid_data.user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Invalid initData"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"InitData validation failed: {str(e)}"
        )
    
    # Extract user ID from validated data
    user_id = valid_data.user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="User ID not found in initData"
        )
    
    # Check if user is in the list of authorized admins
    admin_ids = getattr(config.bot, 'moderators_chat_id', [])
    if user_id not in admin_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to access admin panel"
        )
    # print(user_id)
    # Verify user exists in database and is not banned
    # user = await user_gateway.get_by_id(user_id)
    # if not user or user.is_banned:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin user not found or is banned"
    #     )
    
    return user_id

@admin_router.get("/panel-data", response_model=AdminPanelDTO)
@inject
async def get_admin_panel_data(
    interactor: FromDishka[GetAdminPanelDataInteractor],
    admin_user_id: int = Depends(verify_admin_auth)
) -> AdminPanelDTO:
    print(admin_user_id)
    """Retrieve aggregated data for the admin panel."""
    try:
        data = await interactor()
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin panel data"
        )

@admin_router.get("/users", response_model=AdminUserListDTO)
@inject
async def get_all_users(
    interactor: FromDishka[GetAllUsersInteractor],
    admin_user_id: int = Depends(verify_admin_auth),
    limit: int = Query(default=50, ge=1, le=200, description="Number of users to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination")
) -> AdminUserListDTO:
    """Retrieve a paginated list of all users for the admin panel."""
    try:
        pagination = {"limit": limit, "offset": offset}
        data = await interactor(pagination)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user list"
        )


# Redirect root to admin panel
@admin_router.get("/ciuerynwi7yr4")
async def redirect_to_admin_panel():
    return responses.RedirectResponse(url="/static/admin/ciuerynwi7yr4.html")
