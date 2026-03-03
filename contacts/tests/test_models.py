from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from contacts.models import ContactInfo, FeedbackMessage

User = get_user_model()


@pytest.mark.django_db
class TestContactInfoModel:
    """
    Тесты для модели ContactInfo.
    """

    def test_create_contact_info(self):
        """Тест создания контактной информации."""
        contact = ContactInfo.objects.create(
            address="г. Москва, ул. Тестовая, д. 1",
            phone="+7 (495) 123-45-67",
            email="info@test.ru",
            map_url="https://yandex.ru/maps/123",
            work_hours="Пн-Пт: 9:00-18:00",
            vk_url="https://vk.com/test",
            telegram_url="https://t.me/test",
        )

        assert contact.address == "г. Москва, ул. Тестовая, д. 1"
        assert contact.phone == "+7 (495) 123-45-67"
        assert contact.email == "info@test.ru"
        assert contact.map_url == "https://yandex.ru/maps/123"
        assert contact.work_hours == "Пн-Пт: 9:00-18:00"
        assert contact.vk_url == "https://vk.com/test"
        assert contact.telegram_url == "https://t.me/test"

    def test_contact_info_str_method(self):
        """Тест строкового представления."""
        contact = ContactInfo.objects.create(
            address="г. Москва, ул. Тестовая, д. 1",
            phone="+7 (495) 123-45-67",
            email="info@test.ru",
        )
        assert str(contact) == "Контактная информация компании"

    def test_contact_info_singleton(self):
        """Тест синглтона - нельзя создать вторую запись."""
        ContactInfo.objects.create(
            address="Первый адрес", phone="+7 (495) 111-11-11", email="first@test.ru"
        )

        # Пытаемся создать вторую запись
        with pytest.raises(ValidationError):
            ContactInfo.objects.create(
                address="Второй адрес",
                phone="+7 (495) 222-22-22",
                email="second@test.ru",
            )

    def test_contact_info_default_values(self):
        """Тест значений по умолчанию."""
        contact = ContactInfo.objects.create(
            address="г. Москва, ул. Тестовая, д. 1",
            phone="+7 (495) 123-45-67",
            email="info@test.ru",
        )

        assert contact.work_hours == "Пн-Пт: 9:00-20:00, Сб: 10:00-18:00, Вс: выходной"
        assert contact.map_url == ""
        assert contact.vk_url == ""
        assert contact.telegram_url == ""

    def test_contact_info_updated_at(self):
        """Тест обновления временной метки."""
        contact = ContactInfo.objects.create(
            address="г. Москва, ул. Тестовая, д. 1",
            phone="+7 (495) 123-45-67",
            email="info@test.ru",
        )
        assert contact.updated_at is not None

        old_updated = contact.updated_at
        contact.phone = "+7 (495) 999-99-99"
        contact.save()
        contact.refresh_from_db()
        assert contact.updated_at > old_updated

    def test_contact_info_meta_verbose_names(self):
        """Тест verbose names."""
        assert ContactInfo._meta.verbose_name == "Контактная информация"
        assert ContactInfo._meta.verbose_name_plural == "Контактная информация"

    def test_contact_info_optional_fields(self):
        """Тест необязательных полей."""
        contact = ContactInfo.objects.create(
            address="г. Москва, ул. Тестовая, д. 1",
            phone="+7 (495) 123-45-67",
            email="info@test.ru",
            # map_url, vk_url, telegram_url не указаны
        )

        assert contact.map_url == ""
        assert contact.vk_url == ""
        assert contact.telegram_url == ""


@pytest.mark.django_db
class TestFeedbackMessageModel:
    """
    Тесты для модели FeedbackMessage.
    """

    def test_create_feedback_message(self):
        """Тест создания сообщения обратной связи."""
        message = FeedbackMessage.objects.create(
            name="Иван Петров",
            email="ivan@example.com",
            phone="+7 (999) 123-45-67",
            message="Тестовое сообщение",
        )

        assert message.name == "Иван Петров"
        assert message.email == "ivan@example.com"
        assert message.phone == "+7 (999) 123-45-67"
        assert message.message == "Тестовое сообщение"
        assert message.is_processed is False
        assert message.processed_at is None
        assert message.processed_by is None

    def test_feedback_message_str_method(self):
        """Тест строкового представления."""
        message = FeedbackMessage.objects.create(
            name="Иван Петров", email="ivan@example.com", message="Тестовое сообщение"
        )
        assert str(message).startswith("Сообщение от Иван Петров")

    def test_feedback_message_ordering(self):
        """Тест сортировки по дате создания (новые сверху)."""
        message1 = FeedbackMessage.objects.create(
            name="Пользователь 1", email="user1@example.com", message="Сообщение 1"
        )
        message2 = FeedbackMessage.objects.create(
            name="Пользователь 2", email="user2@example.com", message="Сообщение 2"
        )

        messages = FeedbackMessage.objects.all()
        assert messages[0] == message2  # Новое первое
        assert messages[1] == message1

    def test_feedback_message_processed(self):
        """Тест отметки об обработке."""
        message = FeedbackMessage.objects.create(
            name="Иван Петров", email="ivan@example.com", message="Тестовое сообщение"
        )

        assert message.is_processed is False

        message.is_processed = True
        message.save()
        message.refresh_from_db()
        assert message.is_processed is True

    def test_feedback_message_processed_by(self, django_user_model):
        """Тест привязки к обработавшему пользователю."""
        from django.utils import timezone

        user = django_user_model.objects.create_user(
            username="admin", password="test123"
        )

        message = FeedbackMessage.objects.create(
            name="Иван Петров",
            email="ivan@example.com",
            message="Тестовое сообщение",
            is_processed=True,
            processed_at=timezone.now(),
            processed_by=user,
        )

        assert message.processed_by == user
        assert message.processed_at is not None

    def test_feedback_message_optional_phone(self):
        """Тест что телефон необязателен."""
        message = FeedbackMessage.objects.create(
            name="Иван Петров",
            email="ivan@example.com",
            message="Тестовое сообщение",
            # phone не указан
        )

        assert message.phone == ""

    def test_feedback_message_meta_verbose_names(self):
        """Тест verbose names."""
        assert FeedbackMessage._meta.verbose_name == "Сообщение обратной связи"
        assert FeedbackMessage._meta.verbose_name_plural == "Сообщения обратной связи"
        assert FeedbackMessage._meta.ordering == ["-created_at"]
