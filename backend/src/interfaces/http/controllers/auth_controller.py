from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.application.dto.user_dto import CreateUserCommand, LoginCommand
from src.application.exceptions import EntityAlreadyExistsError
from src.domain.exceptions.user_exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserDomainError,
    UserNotFoundError,
)
from src.interfaces.http.dependencies import CreateUserDependency, LoginDependency
from src.interfaces.http.schemas.user_schemas import (
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(request: UserRegisterRequest, use_case: CreateUserDependency):
    try:
        command = CreateUserCommand(
            username=request.username,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )
        user = await use_case.execute(command)
        return UserResponse.from_entity(user)

    except UserDomainError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post('/login', response_model=TokenResponse)
async def login(form_data: OAuth2Form, use_case: LoginDependency):
    """Endpoint para autenticação e obtenção de token"""
    try:
        command = LoginCommand(email=form_data.username, password=form_data.password)
        access_token = await use_case.execute(command)
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


@router.post('/refresh_token', response_model=TokenResponse)
async def refresh_access_token(
    # current_user: User = Depends(),  # Será implementado no dependency injection
    # token_service será injetado
):
    """Endpoint para renovar token de acesso"""
    # Implementar quando necessário
    # new_access_token = token_service.create_access_token(data={'sub': current_user.email})
    # return TokenResponse(access_token=new_access_token)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail='Refresh token not implemented yet'
    )
