from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from src.application.dto.mood_dto import GetMoodsCommand, RegisterMoodCommand
from src.application.use_cases.mood import list_moods, register_mood
from src.application.use_cases.users import get_current_user
from src.domain.exceptions.user_exceptions import InsufficientPermissionsError
from src.interfaces.http.dependencies import MoodRepositoryDependency, UserRepositoryDependency
from src.interfaces.http.schemas.mood_schemas import (
    FilterQueryMoods,
    ListMoodsResponse,
    MoodResponse,
    RegisterMoodRequest,
)

router = APIRouter(prefix='/users/{user_id}/moods', tags=['moods'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login', refreshUrl='/auth/refresh_token')
TokenDependency = Annotated[str, Depends(oauth2_scheme)]


@router.get('/', response_model=ListMoodsResponse)
async def get_moods(
    user_id: str,
    token: TokenDependency,
    user_repository: UserRepositoryDependency,
    mood_repository: MoodRepositoryDependency,
    filter_query: Annotated[FilterQueryMoods, Query()],
):
    current_user = await get_current_user(user_repository, token)

    try:
        command = GetMoodsCommand(
            user_id=user_id, offset=filter_query.offset, limit=filter_query.limit
        )

        moods = await list_moods(mood_repository, command, current_user)

        return ListMoodsResponse(moods=[MoodResponse.from_entity(mood) for mood in moods])
    except InsufficientPermissionsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post('/', response_model=MoodResponse, status_code=status.HTTP_201_CREATED)
async def create_mood(
    user_id: str,
    mood: RegisterMoodRequest,
    token: TokenDependency,
    user_repository: UserRepositoryDependency,
    mood_repository: MoodRepositoryDependency,
):
    current_user = await get_current_user(user_repository, token)

    try:
        command = RegisterMoodCommand(
            user_id=user_id,
            registry_type=mood.registry_type,
            visual_scale=mood.visual_scale,
            associated_emotions=mood.associated_emotions,
            triggers=mood.triggers,
            description=mood.description,
        )

        created_mood = await register_mood(mood_repository, command, current_user)

        return MoodResponse.from_entity(created_mood)

    except InsufficientPermissionsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
