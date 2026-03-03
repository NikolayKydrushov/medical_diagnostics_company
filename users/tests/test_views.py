import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, RequestFactory
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestRegisterView:
    """
    Тесты для представления регистрации.
    """

    def test_register_view_get(self, client):
        """Тест GET запроса к странице регистрации."""
        url = reverse("users:register")
        response = client.get(url)

        assert response.status_code == 200
        assert "users/register.html" in [t.name for t in response.templates]
        assert "form" in response.context

    def test_register_view_post_success(self, client):
        """Тест успешной регистрации."""
        url = reverse("users:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "first_name": "Новый",
            "last_name": "Пользователь",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        response = client.post(url, data)

        # Должен быть редирект на страницу входа
        assert response.status_code == 302
        assert response.url == reverse("users:login")

        # Проверяем что пользователь создан
        assert User.objects.filter(username="newuser").exists()

        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert "успешно" in str(messages[0])

    def test_register_view_post_invalid(self, client):
        """Тест регистрации с невалидными данными."""
        url = reverse("users:register")
        data = {
            "username": "",  # Пустой username
            "email": "invalid-email",
            "first_name": "",
            "last_name": "",
            "password1": "123",
            "password2": "456",
        }
        response = client.post(url, data)

        assert response.status_code == 200  # Остаемся на той же странице
        assert "form" in response.context
        assert response.context["form"].errors  # Должны быть ошибки

        # Пользователь не создан
        assert not User.objects.exists()

    def test_authenticated_user_redirect(self, client):
        """Тест что авторизованный пользователь перенаправляется на главную."""
        # Создаем и логиним пользователя
        user = User.objects.create_user(username="testuser", password="testpass123")
        client.login(username="testuser", password="testpass123")

        url = reverse("users:register")
        response = client.get(url)

        # Должен быть редирект на главную
        assert response.status_code == 302
        assert response.url == reverse("pages:home")


@pytest.mark.django_db
class TestRegisterDoneView:
    """
    Тесты для страницы успешной регистрации.
    """

    def test_register_done_view_get(self, client):
        """Тест GET запроса к странице успешной регистрации."""
        url = reverse("users:register_done")
        response = client.get(url)

        assert response.status_code == 200
        assert "users/register_done.html" in [t.name for t in response.templates]

    def test_authenticated_user_redirect(self, client):
        """Тест что авторизованный пользователь перенаправляется."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        client.login(username="testuser", password="testpass123")

        url = reverse("users:register_done")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("pages:home")


@pytest.mark.django_db
class TestCustomLoginView:
    """
    Тесты для представления входа.
    """

    def test_login_view_get(self, client):
        """Тест GET запроса к странице входа."""
        url = reverse("users:login")
        response = client.get(url)

        assert response.status_code == 200
        assert "users/login.html" in [t.name for t in response.templates]
        assert "form" in response.context

    def test_login_view_post_success(self, client):
        """Тест успешного входа."""
        # Создаем пользователя
        User.objects.create_user(username="testuser", password="testpass123")

        url = reverse("users:login")
        data = {
            "username": "testuser",
            "password": "testpass123",
        }
        response = client.post(url, data)

        # Должен быть редирект в личный кабинет
        assert response.status_code == 302
        assert response.url == reverse("appointments:dashboard")

        # Проверяем что пользователь действительно залогинен
        assert "_auth_user_id" in client.session

    def test_login_view_post_invalid(self, client):
        """Тест входа с неверными данными."""
        url = reverse("users:login")
        data = {
            "username": "wronguser",
            "password": "wrongpass",
        }
        response = client.post(url, data)

        assert response.status_code == 200  # Остаемся на странице входа
        assert "form" in response.context

        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert "Неверное имя пользователя" in str(messages[0])

    def test_login_with_next_parameter(self, client):
        """Тест редиректа на next параметр после входа."""
        User.objects.create_user(username="testuser", password="testpass123")

        # Исправляем URL
        target_url = reverse("appointments:appointment_create")

        url = reverse("users:login") + f"?next={target_url}"
        data = {
            "username": "testuser",
            "password": "testpass123",
        }
        response = client.post(url, data)

        assert response.status_code == 302
        assert response.url == target_url

    def test_authenticated_user_redirect(self, client):
        """Тест что авторизованный пользователь перенаправляется."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        client.login(username="testuser", password="testpass123")

        url = reverse("users:login")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("pages:home")


@pytest.mark.django_db
class TestCustomLogoutView:
    """
    Тесты для представления выхода.
    """

    def test_logout_view_get(self, client):
        """Тест GET запроса к logout."""
        # Сначала логинимся
        user = User.objects.create_user(username="testuser", password="testpass123")
        client.login(username="testuser", password="testpass123")

        # Проверяем что залогинены
        assert "_auth_user_id" in client.session

        url = reverse("users:logout")
        response = client.get(url)

        # Должен быть редирект на главную
        assert response.status_code == 302
        assert response.url == reverse("pages:home")

        # Проверяем что разлогинены
        assert "_auth_user_id" not in client.session

        # Проверяем сообщение
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert "вышли из системы" in str(messages[0])

    def test_logout_view_post(self, client):
        """Тест POST запроса к logout."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        client.login(username="testuser", password="testpass123")

        url = reverse("users:logout")
        response = client.post(url)

        assert response.status_code == 302
        assert response.url == reverse("pages:home")
        assert "_auth_user_id" not in client.session


@pytest.mark.django_db
class TestProfileView:
    """
    Тесты для просмотра профиля.
    """

    def test_profile_view_authenticated(self, client):
        """Тест доступа к профилю для авторизованного пользователя."""
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="Тест",
            last_name="Пользователь",
        )

        # Исправляем: используем force_login и сохраняем сессию
        client.force_login(user)

        url = reverse("users:profile")
        response = client.get(url)

        assert response.status_code == 200
        assert "users/profile.html" in [t.name for t in response.templates]

    def test_profile_view_unauthenticated(self, client):
        """Тест что неавторизованный пользователь перенаправляется на вход."""
        url = reverse("users:profile")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url.startswith(reverse("users:login"))

    def test_profile_context_data(self, client):
        """Тест контекстных данных профиля."""
        user = User.objects.create_user(username="testuser", password="testpass123")

        # Исправляем: используем force_login
        client.force_login(user)

        url = reverse("users:profile")
        response = client.get(url)

        assert response.status_code == 200
        assert "total_appointments" in response.context
        assert "upcoming_appointments" in response.context
        assert "recent_appointments" in response.context


@pytest.mark.django_db
class TestProfileEditView:
    """
    Тесты для редактирования профиля.
    """

    def test_profile_edit_view_authenticated(self, client):
        """Тест доступа к редактированию для авторизованного пользователя."""
        user = User.objects.create_user(
            username="testuser",
            email="old@example.com",
            first_name="Старое",
            last_name="Имя",
            password="testpass123",
        )

        client.force_login(user)

        url = reverse("users:profile_edit")
        response = client.get(url)

        assert response.status_code == 200
        assert "users/profile_edit.html" in [t.name for t in response.templates]

    def test_profile_edit_view_unauthenticated(self, client):
        """Тест что неавторизованный пользователь перенаправляется."""
        url = reverse("users:profile_edit")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url.startswith(reverse("users:login"))

    def test_profile_edit_success(self, client):
        """Тест успешного редактирования профиля."""
        user = User.objects.create_user(
            username="testuser",
            email="old@example.com",
            first_name="Старое",
            last_name="Имя",
            password="testpass123",
        )

        # Используем force_login
        client.force_login(user)

        url = reverse("users:profile_edit")
        data = {
            "username": "testuser",
            "email": "new@example.com",
            "first_name": "Новое",
            "last_name": "Имя",
            "phone": "+7 (999) 111-22-33",
        }
        response = client.post(url, data)

        # Должен быть редирект на профиль
        assert response.status_code == 302
        assert response.url == reverse("users:profile")

        # Проверяем что данные обновились
        user.refresh_from_db()
        assert user.email == "new@example.com"
        assert user.first_name == "Новое"
        assert user.phone == "+7 (999) 111-22-33"

    def test_profile_edit_invalid_data(self, client):
        """Тест редактирования с невалидными данными."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client.force_login(user)

        url = reverse("users:profile_edit")
        data = {
            "username": "",  # Пустой username
            "email": "invalid-email",
            "first_name": "",
            "last_name": "",
        }
        response = client.post(url, data)

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

        # Данные не изменились
        user.refresh_from_db()
        assert user.email == "test@example.com"

    def test_profile_edit_username_unique(self, client):
        """Тест уникальности username при редактировании."""
        # Создаем двух пользователей
        User.objects.create_user(
            username="existing", email="existing@example.com", password="pass123"
        )

        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client.force_login(user)

        url = reverse("users:profile_edit")
        data = {
            "username": "existing",  # Уже занято
            "email": "test@example.com",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }
        response = client.post(url, data)

        assert response.status_code == 200
        assert "username" in response.context["form"].errors
