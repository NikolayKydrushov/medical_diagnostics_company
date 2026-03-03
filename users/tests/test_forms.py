import pytest
from django import forms

from ..forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from ..models import User


@pytest.mark.django_db
class TestUserRegistrationForm:
    """
    Тесты для формы регистрации пользователя.
    """

    def test_valid_registration_form(self):
        """Тест валидной формы регистрации."""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Тест",
            "last_name": "Пользователь",
            "phone": "+7 (999) 123-45-67",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        form = UserRegistrationForm(data=form_data)
        assert form.is_valid()

    def test_blank_data(self):
        """Тест пустой формы."""
        form = UserRegistrationForm(data={})
        assert not form.is_valid()
        assert len(form.errors) == 6  # Все поля обязательны кроме phone

    def test_username_required(self):
        """Тест обязательности username."""
        form_data = {
            "username": "",
            "email": "test@example.com",
            "first_name": "Тест",
            "last_name": "Пользователь",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "username" in form.errors

    def test_email_required(self):
        """Тест обязательности email."""
        form_data = {
            "username": "testuser",
            "email": "",
            "first_name": "Тест",
            "last_name": "Пользователь",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_invalid_email(self):
        """Тест невалидного email."""
        form_data = {
            "username": "testuser",
            "email": "invalid-email",
            "first_name": "Тест",
            "last_name": "Пользователь",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_unique_email(self):
        """Тест уникальности email."""
        # Создаем пользователя
        User.objects.create_user(
            username="existing", email="existing@example.com", password="pass123"
        )

        # Пытаемся зарегистрироваться с тем же email
        form_data = {
            "username": "newuser",
            "email": "existing@example.com",
            "first_name": "Новый",
            "last_name": "Пользователь",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors
        assert "уже существует" in str(form.errors["email"])

    def test_password_mismatch(self):
        """Тест несовпадения паролей."""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Тест",
            "last_name": "Пользователь",
            "password1": "Pass123!",
            "password2": "DifferentPass123!",
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_password_too_short(self):
        """Тест слишком короткого пароля."""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Тест",
            "last_name": "Пользователь",
            "password1": "short",
            "password2": "short",
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors or "password1" in form.errors

    def test_phone_optional(self):
        """Тест необязательности телефона."""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Тест",
            "last_name": "Пользователь",
            "phone": "",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        form = UserRegistrationForm(data=form_data)
        assert form.is_valid()

    def test_first_name_required(self):
        """Тест обязательности имени."""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "",
            "last_name": "Пользователь",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "first_name" in form.errors

    def test_last_name_required(self):
        """Тест обязательности фамилии."""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Тест",
            "last_name": "",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert "last_name" in form.errors

    def test_form_widgets(self):
        """Тест наличия виджетов."""
        form = UserRegistrationForm()

        # Проверяем классы виджетов
        assert "form-control" in form.fields["username"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["email"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["first_name"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["last_name"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["phone"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["password1"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["password2"].widget.attrs.get("class", "")

    def test_form_placeholders(self):
        """Тест наличия placeholder-ов."""
        form = UserRegistrationForm()

        assert "example@mail.ru" in form.fields["email"].widget.attrs.get(
            "placeholder", ""
        )
        assert "+7 (999) 123-45-67" in form.fields["phone"].widget.attrs.get(
            "placeholder", ""
        )
        assert "Иван" in form.fields["first_name"].widget.attrs.get("placeholder", "")
        assert "Петров" in form.fields["last_name"].widget.attrs.get("placeholder", "")
        assert "ivan_petrov" in form.fields["username"].widget.attrs.get(
            "placeholder", ""
        )


@pytest.mark.django_db
class TestUserProfileForm:
    """
    Тесты для формы редактирования профиля.
    """

    def test_valid_profile_form(self):
        """Тест валидной формы профиля."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="Тест",
            last_name="Пользователь",
        )

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "НовоеИмя",
            "last_name": "НоваяФамилия",
            "phone": "+7 (111) 222-33-44",
            "birth_date": "1990-01-01",
        }
        form = UserProfileForm(data=form_data, instance=user)
        assert form.is_valid()

        # Сохраняем и проверяем изменения
        updated_user = form.save()
        assert updated_user.first_name == "НовоеИмя"
        assert updated_user.last_name == "НоваяФамилия"
        assert updated_user.phone == "+7 (111) 222-33-44"
        assert str(updated_user.birth_date) == "1990-01-01"

    def test_username_unique_validation(self):
        """Тест валидации уникальности username."""
        # Создаем первого пользователя
        User.objects.create_user(username="user1", email="user1@example.com")

        # Создаем второго пользователя
        user2 = User.objects.create_user(username="user2", email="user2@example.com")

        # Пытаемся изменить username второго на уже существующий
        form_data = {
            "username": "user1",  # Уже занято
            "email": "user2@example.com",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }
        form = UserProfileForm(data=form_data, instance=user2)
        assert not form.is_valid()
        assert "username" in form.errors

    def test_email_unique_validation(self):
        """Тест валидации уникальности email."""
        # Создаем первого пользователя
        User.objects.create_user(username="user1", email="same@example.com")

        # Создаем второго пользователя
        user2 = User.objects.create_user(username="user2", email="user2@example.com")

        # Пытаемся изменить email второго на уже существующий
        form_data = {
            "username": "user2",
            "email": "same@example.com",  # Уже занято
            "first_name": "Имя",
            "last_name": "Фамилия",
        }
        form = UserProfileForm(data=form_data, instance=user2)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_same_email_allowed_for_same_user(self):
        """Тест что свой же email разрешен."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        form_data = {
            "username": "testuser",
            "email": "test@example.com",  # Тот же email
            "first_name": "Имя",
            "last_name": "Фамилия",
        }
        form = UserProfileForm(data=form_data, instance=user)
        assert form.is_valid()

    def test_no_password_field(self):
        """Тест что поле пароля отсутствует в форме."""
        form = UserProfileForm()
        assert "password" not in form.fields

    def test_optional_fields(self):
        """Тест необязательных полей."""
        user = User.objects.create_user(username="testuser", email="test@example.com")

        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "phone": "",  # Пустой телефон
            "birth_date": "",  # Пустая дата
        }
        form = UserProfileForm(data=form_data, instance=user)
        assert form.is_valid()


class TestUserLoginForm:
    """
    Тесты для формы входа.
    """

    def test_login_form_fields(self):
        """Тест наличия полей в форме входа."""
        form = UserLoginForm()

        assert "username" in form.fields
        assert "password" in form.fields

    def test_login_form_widgets(self):
        """Тест виджетов формы входа."""
        form = UserLoginForm()

        assert "form-control" in form.fields["username"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["password"].widget.attrs.get("class", "")

        assert "Имя пользователя" in form.fields["username"].widget.attrs.get(
            "placeholder", ""
        )
        assert "Пароль" in form.fields["password"].widget.attrs.get("placeholder", "")

    @pytest.mark.django_db
    def test_login_form_validation(self):
        """Тест валидации формы входа (без проверки аутентификации)."""
        User.objects.create_user(username="testuser", password="testpass123")

        form = UserLoginForm(data={"username": "testuser", "password": "testpass123"})
        # Форма может быть невалидной из-за отсутствия пользователя в БД,
        # но поля должны пройти базовую валидацию
        assert form.is_valid()
