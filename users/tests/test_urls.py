import pytest
from django.urls import resolve, reverse

from .. import views


class TestUsersUrls:
    """
    Тесты для URL-ов приложения users.
    """

    def test_register_url(self):
        """Тест URL регистрации."""
        url = reverse("users:register")
        assert url == "/users/register/"

        resolver = resolve("/users/register/")
        assert resolver.func.view_class == views.RegisterView
        assert resolver.view_name == "users:register"

    def test_register_done_url(self):
        """Тест URL успешной регистрации."""
        url = reverse("users:register_done")
        assert url == "/users/register/done/"

        resolver = resolve("/users/register/done/")
        assert resolver.func.view_class == views.RegisterDoneView
        assert resolver.view_name == "users:register_done"

    def test_login_url(self):
        """Тест URL входа."""
        url = reverse("users:login")
        assert url == "/users/login/"

        resolver = resolve("/users/login/")
        assert resolver.func.view_class == views.CustomLoginView
        assert resolver.view_name == "users:login"

    def test_logout_url(self):
        """Тест URL выхода."""
        url = reverse("users:logout")
        assert url == "/users/logout/"

        resolver = resolve("/users/logout/")
        assert resolver.func.view_class == views.CustomLogoutView
        assert resolver.view_name == "users:logout"

    def test_profile_url(self):
        """Тест URL профиля."""
        url = reverse("users:profile")
        assert url == "/users/profile/"

        resolver = resolve("/users/profile/")
        assert resolver.func.view_class == views.ProfileView
        assert resolver.view_name == "users:profile"

    def test_profile_edit_url(self):
        """Тест URL редактирования профиля."""
        url = reverse("users:profile_edit")
        assert url == "/users/profile/edit/"

        resolver = resolve("/users/profile/edit/")
        assert resolver.func.view_class == views.ProfileEditView
        assert resolver.view_name == "users:profile_edit"

    def test_app_name(self):
        """Тест что app_name установлен правильно."""
        from django.urls import get_resolver

        resolver = get_resolver()
        assert "users" in resolver.app_dict
