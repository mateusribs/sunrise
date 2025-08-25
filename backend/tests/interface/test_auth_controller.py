import pytest
from fastapi import status


class TestSignup:
    def test_signup_valid_payload(self, client):
        response = client.post(
            '/auth/signup',
            json={
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'Password123',
                'first_name': 'Test',
                'last_name': 'User',
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': response.json()['id'],  # Dynamic ID, just check it exists
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'is_admin': False,
        }

    def test_signup_invalid_domain_error(self, client):
        response = client.post(
            '/auth/signup',
            json={
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'invalid-password',
                'first_name': 'Test',
                'last_name': 'User',
            },
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {'detail': 'Password must contain at least one digit'}

    def test_signup_user_already_exists_error(self, client):
        client.post(
            '/auth/signup',
            json={
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'Password123',
                'first_name': 'Test',
                'last_name': 'User',
            },
        )

        response_2 = client.post(
            '/auth/signup',
            json={
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'Password123',
                'first_name': 'Test',
                'last_name': 'User',
            },
        )

        assert response_2.status_code == status.HTTP_409_CONFLICT
        assert response_2.json() == {'detail': 'User with this email or username already exists'}


class TestLogin:
    @pytest.fixture(autouse=True)
    def user_request(self, client):
        client.post(
            '/auth/signup',
            json={
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'Password123',
                'first_name': 'Test',
                'last_name': 'User',
            },
        )

    def test_login_valid_credentials(self, client):
        response = client.post(
            '/auth/login', data={'username': 'testuser@example.com', 'password': 'Password123'}
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.json()

    def test_login_invalid_credential_error(self, client):
        response = client.post(
            '/auth/login', data={'username': 'testuser@example.com', 'password': 'wrong-password'}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Incorrect username or password'}

    @pytest.mark.asyncio
    async def test_login_inactive_user_error(self, client, user_repository):
        user = await user_repository.find_by_email('testuser@example.com')
        user.is_active = False
        await user_repository.update(user)

        response = client.post(
            '/auth/login', data={'username': 'testuser@example.com', 'password': 'Password123'}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'User account is inactive'}
