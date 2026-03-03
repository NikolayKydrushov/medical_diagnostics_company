import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from contacts.models import ContactInfo, FeedbackMessage


@pytest.mark.django_db
class TestContactView:
    """
    Тесты для страницы контактов.
    """

    def test_contact_view_get(self, client):
        """Тест GET запроса к странице контактов."""
        url = reverse("contacts:contact")
        response = client.get(url)

        assert response.status_code == 200
        assert "contacts/contact.html" in [t.name for t in response.templates]
        assert "form" in response.context
        assert "contact_info" in response.context

    def test_contact_view_with_contact_info(self, client):
        """Тест с существующей контактной информацией."""
        contact = ContactInfo.objects.create(
            address="г. Москва, ул. Тестовая, д. 1",
            phone="+7 (495) 123-45-67",
            email="info@test.ru",
        )

        url = reverse("contacts:contact")
        response = client.get(url)

        assert response.context["contact_info"] == contact

    def test_contact_view_post_valid(self, client):
        """Тест POST запроса с валидными данными."""
        url = reverse("contacts:contact")
        data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "phone": "+7 (999) 123-45-67",
            "message": "Тестовое сообщение",
        }
        response = client.post(url, data)

        # Должен быть редирект на страницу благодарности
        assert response.status_code == 302
        assert response.url == reverse("contacts:thank_you")

        # Проверяем что сообщение создалось
        assert FeedbackMessage.objects.count() == 1
        message = FeedbackMessage.objects.first()
        assert message.name == "Иван Петров"
        assert message.email == "ivan@example.com"

        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Спасибо за обращение" in str(messages[0])

    def test_contact_view_post_invalid(self, client):
        """Тест POST запроса с невалидными данными."""
        url = reverse("contacts:contact")
        data = {
            "name": "",  # Пустое имя
            "email": "invalid-email",
            "message": "",  # Пустое сообщение
        }
        response = client.post(url, data)

        # Должен остаться на той же странице
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

        # Проверяем что сообщение не создалось
        assert FeedbackMessage.objects.count() == 0

        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "исправьте ошибки" in str(messages[0])

    def test_contact_view_post_without_phone(self, client):
        """Тест POST запроса без телефона."""
        url = reverse("contacts:contact")
        data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "message": "Тестовое сообщение",
            # phone не указан
        }
        response = client.post(url, data)

        assert response.status_code == 302
        assert response.url == reverse("contacts:thank_you")

        message = FeedbackMessage.objects.first()
        assert message.phone == ""


@pytest.mark.django_db
class TestContactThankYouView:
    """
    Тесты для страницы благодарности.
    """

    def test_thank_you_view_get(self, client):
        """Тест GET запроса к странице благодарности."""
        url = reverse("contacts:thank_you")
        response = client.get(url)

        assert response.status_code == 200
        assert "contacts/thank_you.html" in [t.name for t in response.templates]
        assert "contact_info" in response.context

    def test_thank_you_view_with_contact_info(self, client):
        """Тест с контактной информацией."""
        contact = ContactInfo.objects.create(
            address="г. Москва, ул. Тестовая, д. 1",
            phone="+7 (495) 123-45-67",
            email="info@test.ru",
        )

        url = reverse("contacts:thank_you")
        response = client.get(url)

        assert response.context["contact_info"] == contact

    def test_thank_you_view_without_contact_info(self, client):
        """Тест без контактной информации."""
        url = reverse("contacts:thank_you")
        response = client.get(url)

        assert response.context["contact_info"] is None
