from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.application.dto.user_dto import CreateUserCommand, LoginCommand
from src.application.exceptions import EntityAlreadyExistsError
from src.application.use_cases import create_user, get_access_token
from src.domain.exceptions.user_exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserDomainError,
    UserNotFoundError,
)
from src.interfaces.http.dependencies import UserRepositoryDependency
from src.interfaces.http.schemas.user_schemas import (
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup(request: UserRegisterRequest, user_repository: UserRepositoryDependency):
    try:
        command = CreateUserCommand(
            username=request.username,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )
        user = await create_user(user_repository, command)
        return UserResponse.from_entity(user)

    except UserDomainError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post('/login', response_model=TokenResponse)
async def login(form_data: OAuth2Form, user_repository: UserRepositoryDependency):
    """Endpoint para autenticação e obtenção de token"""
    try:
        command = LoginCommand(email=form_data.username, password=form_data.password)
        access_token = await get_access_token(user_repository, command)
        return TokenResponse(access_token=access_token)

    except (InvalidCredentialsError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except InactiveUserError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
            headers={'WWW-Authenticate': 'Bearer'},
        )
