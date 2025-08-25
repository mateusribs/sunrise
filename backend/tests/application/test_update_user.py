import pytest

from src.application.dto import UpdateUserCommand
from src.application.exceptions import EntityAlreadyExistsError
from src.application.use_cases import UpdateUser
from src.domain.exceptions import (
    InsufficientPermissionsError,
)


@pytest.mark.asyncio
async def test_update_user_when_is_admin(user_repository, user, other_user):
    user_command = UpdateUserCommand(
        user_id=user.id, username='newusername', first_name='New', last_name='Name'
    )

    current_user = user_repository._model_to_entity(other_user)
    current_user.is_admin = True

    update_user = UpdateUser(user_repository)

    await update_user.execute(user_command, current_user)

    updated_user = await user_repository.find_by_email(user.email)

    assert updated_user.username == user_command.username
    assert updated_user.first_name == user_command.first_name
    assert updated_user.last_name == user_command.last_name


@pytest.mark.asyncio
async def test_update_user_when_is_same_user(user_repository, user):
    user_command = UpdateUserCommand(
        user_id=user.id, username='newusername', first_name='New', last_name='Name'
    )

    current_user = user_repository._model_to_entity(user)
    current_user.is_admin = True

    update_user = UpdateUser(user_repository)

    await update_user.execute(user_command, current_user)

    updated_user = await user_repository.find_by_email(user.email)

    assert updated_user.username == user_command.username
    assert updated_user.first_name == user_command.first_name
    assert updated_user.last_name == user_command.last_name


@pytest.mark.asyncio
async def test_update_different_id(user_repository, user):
    user_command = UpdateUserCommand(user_id='nonexistent-id', username='newusername')

    user_domain = user_repository._model_to_entity(user)

    update_user = UpdateUser(user_repository)

    with pytest.raises(InsufficientPermissionsError):
        await update_user.execute(user_command, user_domain)


@pytest.mark.asyncio
async def test_update_username_already_exists(user_repository, user, other_user):
    user_domain = user_repository._model_to_entity(user)

    user_command = UpdateUserCommand(user_id=user_domain.id, username=other_user.username)

    update_user = UpdateUser(user_repository)

    with pytest.raises(EntityAlreadyExistsError):
        await update_user.execute(user_command, user_domain)
