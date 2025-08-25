import pytest

from src.application.dto import GetUsersCommand
from src.application.use_cases import GetUsers
from src.domain.exceptions import InactiveUserError, InsufficientPermissionsError


@pytest.mark.asyncio
async def test_get_users(user_repository, user, other_user):
    get_users_command = GetUsersCommand(offset=0, limit=10, is_active=True, is_admin=True)

    get_users = GetUsers(user_repository)
    users = await get_users.execute(get_users_command)
    user_domain, other_user_domain = user_repository._model_to_entity(user), user_repository._model_to_entity(other_user)

    assert len(users) == 2
    assert users == [user_domain, other_user_domain]


@pytest.mark.asyncio
async def test_get_users_with_offset(user_repository, user, other_user):
    get_users_command = GetUsersCommand(offset=1, limit=10, is_active=True, is_admin=True)

    get_users = GetUsers(user_repository)
    users = await get_users.execute(get_users_command)
    other_user_domain = user_repository._model_to_entity(other_user)

    assert len(users) == 1
    assert users == [other_user_domain]


@pytest.mark.asyncio
async def test_get_users_when_user_is_not_admin(user_repository, user, other_user):
    get_users_command = GetUsersCommand(offset=0, limit=10, is_active=True, is_admin=False)

    get_users = GetUsers(user_repository)

    with pytest.raises(InsufficientPermissionsError, match="Only admin users can retrieve the user list"):
        users = await get_users.execute(get_users_command)


@pytest.mark.asyncio
async def test_get_users_when_user_is_inactive(user_repository, user, other_user):
    get_users_commnand = GetUsersCommand(offset=0, limit=10, is_active=False, is_admin=True)

    get_users = GetUsers(user_repository)

    with pytest.raises(InactiveUserError, match="Inactive users cannot perform this action"):
        users = await get_users.execute(get_users_commnand)
