import pytest
import pytest_asyncio

from src.domain.entities.mood import Mood


@pytest.fixture
def token(client):
    for i in range(4):
        response = client.post(
            '/auth/signup',
            json={
                'username': f'testuser{i}',
                'email': f'testuser{i}@example.com',
                'password': 'Password123',
                'first_name': 'Test',
                'last_name': 'User',
            },
        )

    response = client.post(
        '/auth/login', data={'username': 'testuser0@example.com', 'password': 'Password123'}
    )
    return response.json()['access_token']


@pytest_asyncio.fixture
async def create_moods_for_user(user_repository, mood_repository):
    user = await user_repository.find_by_email('testuser0@example.com')
    for i in range(2, 15):
        await mood_repository.save(
            Mood(
                user_id=user.id,
                registry_type='daily',
                visual_scale=(i % 5) + 1,
                associated_emotions=[{'name': 'joy', 'intensity': (i % 10) + 1}],
                triggers=[{'name': f'trigger{i}'}],
                description=f'Mood entry {i}',
            )
        )


@pytest_asyncio.fixture
async def create_moods_for_another_user(user_repository, mood_repository):
    user = await user_repository.find_by_email('testuser1@example.com')
    for i in range(2, 15):
        await mood_repository.save(
            Mood(
                user_id=user.id,
                registry_type='daily',
                visual_scale=(i % 5) + 1,
                associated_emotions=[{'name': 'joy', 'intensity': (i % 10) + 1}],
                triggers=[{'name': f'trigger{i}'}],
                description=f'Mood entry {i}',
            )
        )


class TestCreateMood:
    @pytest.mark.asyncio
    async def test_create_mood_as_owner(self, client, token, user_repository):
        user = await user_repository.find_by_email('testuser0@example.com')
        response = client.post(
            f'/users/{user.id}/moods',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'registry_type': 'daily',
                'visual_scale': 5,
                'associated_emotions': [{'name': 'joy', 'intensity': 8}],
                'triggers': [{'name': 'sunshine'}],
                'description': 'Feeling great!',
            },
        )
        assert response.status_code == 201
        assert 'id' in response.json()

    @pytest.mark.asyncio
    async def test_create_mood_as_admin(self, client, user_repository, token):
        user = await user_repository.find_by_email('testuser0@example.com')
        user.is_admin = True
        await user_repository.update(user)

        user_1 = await user_repository.find_by_email('testuser1@example.com')
        response = client.post(
            f'/users/{user_1.id}/moods',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'registry_type': 'daily',
                'visual_scale': 5,
                'associated_emotions': [{'name': 'joy', 'intensity': 8}],
                'triggers': [{'name': 'sunshine'}],
                'description': 'Feeling great!',
            },
        )
        assert response.status_code == 201
        assert 'id' in response.json()

    @pytest.mark.asyncio
    async def test_create_mood_unauthorized(self, client, user_repository, token):
        user_1 = await user_repository.find_by_email('testuser1@example.com')
        response = client.post(
            f'/users/{user_1.id}/moods',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'registry_type': 'daily',
                'visual_scale': 5,
                'associated_emotions': [{'name': 'joy', 'intensity': 8}],
                'triggers': [{'name': 'sunshine'}],
                'description': 'Feeling great!',
            },
        )
        assert response.status_code == 403
        assert response.json()['detail'] == 'Not enough permissions'

    @pytest.mark.parametrize(
        'triggers',
        [
            ([{'name': 'sunshine', 'extra_field': 'not allowed'}]),  # Extra field
            ([{'intensity': 5}]),  # Missing required field 'name'
        ],
    )
    @pytest.mark.asyncio
    async def test_create_mood_invalid_data(self, client, token, user_repository, triggers):
        user = await user_repository.find_by_email('testuser0@example.com')
        response = client.post(
            f'/users/{user.id}/moods',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'registry_type': 'daily',
                'visual_scale': 5,
                'associated_emotions': [{'name': 'joy', 'intensity': 8}],
                'triggers': triggers,
                'description': 'Feeling great!',
            },
        )
        assert response.status_code == 400


class TestListMoods:
    @pytest.mark.asyncio
    async def test_list_moods_as_owner(self, client, token, user_repository, create_moods_for_user):
        user = await user_repository.find_by_email('testuser0@example.com')
        response = client.get(
            f'/users/{user.id}/moods',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200
        assert len(response.json()['moods']) == 10  # Default limit is 10

    @pytest.mark.asyncio
    async def test_list_moods_as_admin(
        self, client, user_repository, token, create_moods_for_another_user
    ):
        user = await user_repository.find_by_email('testuser0@example.com')
        user.is_admin = True
        await user_repository.update(user)

        user_1 = await user_repository.find_by_email('testuser1@example.com')
        response = client.get(
            f'/users/{user_1.id}/moods',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200
        assert len(response.json()['moods']) == 10  # Default limit is 10

    @pytest.mark.asyncio
    async def test_list_moods_unauthorized(
        self, client, user_repository, token, create_moods_for_another_user
    ):
        user_1 = await user_repository.find_by_email('testuser1@example.com')
        response = client.get(
            f'/users/{user_1.id}/moods',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 403
        assert response.json()['detail'] == 'Not enough permissions'

    @pytest.mark.asyncio
    async def test_list_moods_pagination(
        self, client, token, user_repository, create_moods_for_user
    ):
        user = await user_repository.find_by_email('testuser0@example.com')
        response = client.get(
            f'/users/{user.id}/moods',
            params={'limit': 5},
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == 200
        assert len(response.json()['moods']) == 5
