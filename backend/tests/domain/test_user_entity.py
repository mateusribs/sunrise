import pytest

from src.domain.entities import User
from src.domain.exceptions import InvalidPasswordError, InvalidUsernameError


def test_create_user():
    user = User(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
    )

    assert user


def test_user_username_empty():
    with pytest.raises(InvalidUsernameError, match='Username cannot be empty'):
        User(
            username='',
            email='testuser@example.com',
            password='Password123',
        )


def test_user_password_minimum_length():
    with pytest.raises(InvalidPasswordError, match='Password must be at least 8 characters long'):
        User(
            username='testuser',
            email='testuser@example.com',
            password='short',
        )


def test_user_password_no_uppercase():
    with pytest.raises(
        InvalidPasswordError, match='Password must contain at least one uppercase letter'
    ):
        User(
            username='testuser',
            email='testuser@example.com',
            password='nouppercase123',
        )


def test_user_password_no_lowercase():
    with pytest.raises(
        InvalidPasswordError, match='Password must contain at least one lowercase letter'
    ):
        User(
            username='testuser',
            email='testuser@example.com',
            password='NOLOWERCASE123',
        )


def test_user_password_no_digit():
    with pytest.raises(InvalidPasswordError, match='Password must contain at least one digit'):
        User(username='testuser', email='testuser@example.com', password='No_digitts')


def test_user_full_name():
    user = User(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
        first_name='Test',
        last_name='User',
    )

    assert user.full_name == 'Test User'


def test_update_username():
    user = User(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
    )

    user.update_username('newusername')

    assert user.username == 'newusername'


def test_fail_update_username_empty():
    user = User(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
    )

    with pytest.raises(InvalidUsernameError, match='Username cannot be empty'):
        user.update_username('')


def test_update_profile():
    user = User(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
    )

    user.update_profile(first_name='NewFirst', last_name='NewLast')

    assert user.first_name == 'NewFirst'
    assert user.last_name == 'NewLast'


def test_deactivate_user():
    user = User(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
    )

    user.deactivate()

    assert user.is_active is False


def test_activate_user():
    user = User(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
    )

    user.activate()

    assert user.is_active is True


def test_make_admin():
    user = User(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
    )

    user.make_admin()

    assert user.is_admin is True


def test_remove_admin():
    user = User(
        username='testuser',
        email='testuser@example.com',
        password='Password123',
    )

    user.remove_admin()

    assert user.is_admin is False
