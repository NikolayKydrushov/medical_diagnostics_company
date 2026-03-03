import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.fixture
def user():
    """Создает обычного пользователя для тестов."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Тест",
        last_name="Пользователь",
    )


@pytest.fixture
def another_user():
    """Создает другого пользователя для тестов."""
    return User.objects.create_user(
        username="another", email="another@example.com", password="another123"
    )


@pytest.fixture
def admin_user():
    """Создает администратора для тестов."""
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="admin123"
    )


@pytest.fixture
def client():
    """Возвращает клиент для тестирования."""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Возвращает авторизованный клиент."""
    client.force_login(user)
    return client
