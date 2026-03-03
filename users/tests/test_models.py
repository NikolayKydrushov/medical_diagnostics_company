from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """
    Тесты для модели User.
    """

    def test_create_user(self):
        """Тест создания обычного пользователя."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Тест",
            last_name="Пользователь",
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Тест"
        assert user.last_name == "Пользователь"
        assert user.check_password("testpass123")
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active

    def test_create_superuser(self):
        """Тест создания суперпользователя."""
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        assert admin_user.username == "admin"
        assert admin_user.email == "admin@example.com"
        assert admin_user.is_staff
        assert admin_user.is_superuser
        assert admin_user.is_active

    def test_user_str_method(self):
        """Тест строкового представления пользователя."""
        # С пользователем с именем и фамилией
        user1 = User.objects.create_user(
            username="user1", first_name="Иван", last_name="Иванов"
        )
        assert str(user1) == "Иванов Иван"

        # С пользователем без имени и фамилии
        user2 = User.objects.create_user(username="user2")
        assert str(user2) == "user2"

    def test_get_full_name(self):
        """Тест метода get_full_name."""
        # С пользователем с именем и фамилией
        user1 = User.objects.create_user(
            username="user1", first_name="Иван", last_name="Иванов"
        )
        assert user1.get_full_name() == "Иванов Иван"

        # С пользователем без имени и фамилии
        user2 = User.objects.create_user(username="user2")
        assert user2.get_full_name() == "user2"

        # С пользователем только с именем
        user3 = User.objects.create_user(username="user3", first_name="Петр")
        assert user3.get_full_name() == "Петр"

    def test_get_short_name(self):
        """Тест метода get_short_name."""
        # С пользователем с именем
        user1 = User.objects.create_user(username="user1", first_name="Иван")
        assert user1.get_short_name() == "Иван"

        # С пользователем без имени
        user2 = User.objects.create_user(username="user2")
        assert user2.get_short_name() == "user2"

    def test_optional_fields(self):
        """Тест необязательных полей."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            phone="+7 (999) 123-45-67",
            birth_date="1990-01-01",
            passport_data="1234 567890",
            insurance_policy="1234567890",
        )

        assert user.phone == "+7 (999) 123-45-67"
        assert user.birth_date == "1990-01-01"
        assert user.passport_data == "1234 567890"
        assert user.insurance_policy == "1234567890"

    def test_email_unique(self):
        """Тест уникальности email через форму."""
        from users.forms import UserRegistrationForm

        # Создаем первого пользователя
        User.objects.create_user(username="user1", email="same@example.com")

        # Пытаемся создать второго через форму
        form_data = {
            "username": "user2",
            "email": "same@example.com",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }

        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors
        assert "уже существует" in str(form.errors["email"])

    def test_username_unique(self):
        """Тест уникальности username."""
        User.objects.create_user(username="sameuser")

        # Попытка создать второго пользователя с тем же username
        with pytest.raises(IntegrityError):
            User.objects.create_user(username="sameuser")

    @pytest.mark.skip(reason="Требуется создание сервисов и записей")
    def test_get_upcoming_appointments(self):
        """Тест метода get_upcoming_appointments."""
        # Этот тест будет реализован после создания appointments
        pass

    def test_user_ordering(self):
        """Тест сортировки пользователей по дате регистрации."""
        from datetime import timedelta

        from django.utils import timezone

        # Создаем пользователей с разными датами регистрации
        user1 = User.objects.create_user(username="user1")
        user1.date_joined = timezone.now() - timedelta(days=5)
        user1.save()

        user2 = User.objects.create_user(username="user2")
        user2.date_joined = timezone.now() - timedelta(days=2)
        user2.save()

        user3 = User.objects.create_user(username="user3")
        user3.date_joined = timezone.now() - timedelta(days=10)
        user3.save()

        # Получаем всех пользователей, отсортированных по дате_присоединения (новые первые)
        users = User.objects.all()
        assert users[0].username == "user2"  # Самый новый
        assert users[1].username == "user1"
        assert users[2].username == "user3"  # Самый старый

    def test_favorite_services_relation(self):
        """Тест связи с избранными услугами."""
        # Создаем пользователя
        user = User.objects.create_user(username="testuser")

        # Создаем реальные услуги (если есть приложение services)
        # Если нет, пропускаем тест
        try:
            from services.models import Service

            service1 = Service.objects.create(
                name="Услуга 1",
                slug="usluga-1",
                short_description="Описание 1",
                price=1000,
                duration=30,
            )
            service2 = Service.objects.create(
                name="Услуга 2",
                slug="usluga-2",
                short_description="Описание 2",
                price=2000,
                duration=45,
            )

            # Добавляем услуги в избранное
            user.favorite_services.add(service1, service2)

            assert user.favorite_services.count() == 2

            # Удаляем услугу
            user.favorite_services.remove(service1)
            assert user.favorite_services.count() == 1

            # Очищаем избранное
            user.favorite_services.clear()
            assert user.favorite_services.count() == 0

        except ImportError:
            pytest.skip("Приложение services не доступно")

    def test_meta_verbose_names(self):
        """Тест verbose names в Meta классе."""
        assert User._meta.verbose_name == "Пользователь"
        assert User._meta.verbose_name_plural == "Пользователи"
        assert User._meta.ordering == ["-date_joined"]

    def test_field_verbose_names(self):
        """Тест verbose names полей."""
        assert User._meta.get_field("phone").verbose_name == "Телефон"
        assert User._meta.get_field("birth_date").verbose_name == "Дата рождения"
        assert User._meta.get_field("avatar").verbose_name == "Аватар"
        assert User._meta.get_field("passport_data").verbose_name == "Паспортные данные"
        assert User._meta.get_field("insurance_policy").verbose_name == "Полис"
        assert (
            User._meta.get_field("favorite_services").verbose_name == "Избранные услуги"
        )

    def test_help_texts(self):
        """Тест help_text полей."""
        assert "Номер телефона" in User._meta.get_field("phone").help_text
        assert (
            "Серия и номер паспорта" in User._meta.get_field("passport_data").help_text
        )
