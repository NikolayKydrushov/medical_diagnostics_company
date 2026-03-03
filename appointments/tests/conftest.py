import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from doctors.models import Doctor
from services.models import Service

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
        username="another",
        email="another@example.com",
        password="another123",
        first_name="Другой",
        last_name="Пользователь",
    )


@pytest.fixture
def service():
    """Создает тестовую услугу."""
    return Service.objects.create(
        name="Тестовая услуга",
        slug="test-service",
        short_description="Описание тестовой услуги",
        full_description="Полное описание",
        price=1000.00,
        duration=30,
        is_active=True,
    )


@pytest.fixture
def another_service():
    """Создает другую тестовую услугу."""
    return Service.objects.create(
        name="Другая услуга",
        slug="another-service",
        short_description="Описание другой услуги",
        full_description="Полное описание",
        price=2000.00,
        duration=45,
        is_active=True,
    )


@pytest.fixture
def doctor():
    """Создает тестового врача."""
    return Doctor.objects.create(
        name="Иванов Иван Иванович",
        slug="ivanov-ivan",
        specialty="Кардиолог",
        bio="Опытный врач-кардиолог",
        experience_years=15,
        email="ivanov@example.com",
        phone="+7 (999) 123-45-67",
        is_active=True,
    )


@pytest.fixture
def another_doctor():
    """Создает другого тестового врача."""
    return Doctor.objects.create(
        name="Петров Петр Петрович",
        slug="petrov-petr",
        specialty="Хирург",
        bio="Опытный хирург",
        experience_years=10,
        email="petrov@example.com",
        phone="+7 (999) 222-33-44",
        is_active=True,
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
