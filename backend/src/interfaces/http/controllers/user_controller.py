from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

from src.application.dto.user_dto import GetUsersCommand, UpdateUserCommand
from src.application.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from src.application.use_cases.get_current_user import GetCurrentUser
from src.application.use_cases.get_users import GetUsers
from src.application.use_cases.update_user import UpdateUser
from src.domain.exceptions.user_exceptions import InsufficientPermissionsError
from src.interfaces.http.dependencies import get_current_user, get_users, update_user
from src.interfaces.http.schemas.user_schemas import (
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix='/users', tags=['users'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login', refreshUrl='/auth/refresh_token')


@router.get('/', response_model=UserListResponse)
async def get_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    use_case: GetUsers = Depends(get_users),
    token: str = Depends(oauth2_scheme),
    get_current_user: GetCurrentUser = Depends(get_current_user)
):
    try:
        current_user = await get_current_user.execute(token)
        command = GetUsersCommand(offset=offset, limit=limit, is_admin=current_user.is_admin, is_active=current_user.is_active)
        users = await use_case.execute(command)
        return UserListResponse(
            users=[UserResponse.from_entity(user) for user in users]
        )
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.put('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    get_current_user: GetCurrentUser = Depends(get_current_user),
    update_user: UpdateUser = Depends(update_user),
    token: str = Depends(oauth2_scheme)
):
    current_user = await get_current_user.execute(token)
    try:
        command = UpdateUserCommand(
            user_id=user_id,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name
        )
        user = await update_user.execute(command, current_user)
        return UserResponse.from_entity(user)

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InsufficientPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
