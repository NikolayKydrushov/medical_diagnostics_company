import pytest

from contacts.forms import ContactForm
from contacts.models import FeedbackMessage


@pytest.mark.django_db
class TestContactForm:
    """
    Тесты для формы обратной связи.
    """

    def test_valid_contact_form(self):
        """Тест валидной формы."""
        form_data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "phone": "+7 (999) 123-45-67",
            "message": "Тестовое сообщение",
        }
        form = ContactForm(data=form_data)
        assert form.is_valid()

    def test_contact_form_required_fields(self):
        """Тест обязательных полей."""
        form = ContactForm(data={})
        assert not form.is_valid()
        assert "name" in form.errors
        assert "email" in form.errors
        assert "message" in form.errors
        # phone необязателен, поэтому его нет в ошибках

    def test_contact_form_email_validation(self):
        """Тест валидации email."""
        # Неверный формат email
        form_data = {
            "name": "Иван Петров",
            "email": "invalid-email",
            "message": "Тестовое сообщение",
        }
        form = ContactForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_contact_form_phone_validation_valid(self):
        """Тест валидации телефона - корректный номер."""
        form_data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "phone": "+7 (999) 123-45-67",
            "message": "Тестовое сообщение",
        }
        form = ContactForm(data=form_data)
        assert form.is_valid()

        # Проверяем что телефон очистился от форматирования
        cleaned_data = form.clean()
        assert cleaned_data["phone"] == "+79991234567"

    def test_contact_form_phone_validation_invalid(self):
        """Тест валидации телефона - слишком короткий номер."""
        form_data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "phone": "123",
            "message": "Тестовое сообщение",
        }
        form = ContactForm(data=form_data)
        assert not form.is_valid()
        assert "phone" in form.errors

    def test_contact_form_phone_optional(self):
        """Тест что телефон необязателен."""
        form_data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "message": "Тестовое сообщение",
            # phone не указан
        }
        form = ContactForm(data=form_data)
        assert form.is_valid()

    def test_contact_form_save(self):
        """Тест сохранения формы."""
        form_data = {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "phone": "+7 (999) 123-45-67",
            "message": "Тестовое сообщение",
        }
        form = ContactForm(data=form_data)
        assert form.is_valid()

        message = form.save()
        assert message.id is not None
        assert message.name == "Иван Петров"
        assert message.email == "ivan@example.com"
        assert message.phone == "+79991234567"
        assert message.message == "Тестовое сообщение"
        assert message.is_processed is False

    def test_contact_form_widgets(self):
        """Тест наличия виджетов."""
        form = ContactForm()

        # Проверяем классы виджетов
        assert "form-control" in form.fields["name"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["email"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["phone"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["message"].widget.attrs.get("class", "")

        # Проверяем placeholder-ы
        assert "Введите ваше имя" in form.fields["name"].widget.attrs.get(
            "placeholder", ""
        )
        assert "example@mail.ru" in form.fields["email"].widget.attrs.get(
            "placeholder", ""
        )
        assert "+7 (999) 123-45-67" in form.fields["phone"].widget.attrs.get(
            "placeholder", ""
        )
        assert "Введите ваше сообщение" in form.fields["message"].widget.attrs.get(
            "placeholder", ""
        )

    def test_contact_form_labels(self):
        """Тест меток полей."""
        form = ContactForm()

        assert form.fields["name"].label == "Ваше имя"
        assert form.fields["email"].label == "Email"
        assert form.fields["phone"].label == "Телефон"
        assert form.fields["message"].label == "Сообщение"
