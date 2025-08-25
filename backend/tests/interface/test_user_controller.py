import pytest
from fastapi import status


@pytest.fixture(autouse=True)
def token(client):
    for i in range(4):
        response = client.post('/auth/signup', json={
            "username": f"testuser{i}",
            "email": f"testuser{i}@example.com",
            "password": "Password123",
            "first_name": "Test",
            "last_name": "User"
    })

    response = client.post('/auth/login', data={
        "username": "testuser0@example.com",
        "password": "Password123"
    })
    return response.json()["access_token"]


class TestGetUsers:
    @pytest.mark.asyncio
    async def test_get_users_when_admin(self, client, user_repository, token):
        user = await user_repository.find_by_email("testuser0@example.com")
        user.is_admin = True
        await user_repository.update(user)

        response = client.get('/users', headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json()['users'], list)
        assert len(response.json()['users']) == 4

    def test_get_users_when_normal_user(self, client, token):
        response = client.get('/users', headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'Only admin users can retrieve the user list'
        }


class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_update_user_when_admin(self, client, user_repository, token):
        user = await user_repository.find_by_email("testuser0@example.com")
        user.is_admin = True
        await user_repository.update(user)

        user2 = await user_repository.find_by_email("testuser1@example.com")

        response = client.put(f'/users/{user2.id}', json={
            "username": "anotherusername"
        }, headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": user2.id,
            "username": "anotherusername",
            "email": "testuser1@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_admin": False,
            "is_active": True,
        }

    @pytest.mark.asyncio
    async def test_update_user_when_itself(self, client, user_repository, token):
        user = await user_repository.find_by_email("testuser0@example.com")

        response = client.put(f'/users/{user.id}', json={
            "username": "anotherusername",
            "first_name": "Another",
            "last_name": "User"
        }, headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": user.id,
            "username": "anotherusername",
            "email": "testuser0@example.com",
            "first_name": "Another",
            "last_name": "User",
            "is_admin": False,
            "is_active": True,
        }

    @pytest.mark.asyncio
    async def test_update_user_when_not_exists(self, client, token, user_repository):
        user = await user_repository.find_by_email("testuser0@example.com")
        user.is_admin = True
        await user_repository.update(user)

        response = client.put('/users/999', json={
            "username": "anotherusername",
            "first_name": "Another",
            "last_name": "User"
        }, headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            'detail': 'User not found'
        }

    def test_update_user_when_not_exists(self, client, token):
        response = client.put('/users/999', json={
            "username": "anotherusername",
            "first_name": "Another",
            "last_name": "User"
        }, headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'detail': 'Not enough permissions'
        }

    @pytest.mark.asyncio
    async def test_update_user_when_username_already_exists(self, client, token, user_repository):
        user = await user_repository.find_by_email("testuser0@example.com")

        response = client.put(f'/users/{user.id}', json={
            "username": "testuser2",
            "first_name": "Another",
            "last_name": "User"
        }, headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            'detail': 'User with this email or username already exists'
        }
