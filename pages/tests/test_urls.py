import pytest
from django.urls import resolve, reverse

from pages import views


class TestPagesUrls:
    """
    Тесты для URL-ов приложения pages.
    """

    def test_home_url(self):
        """Тест URL главной страницы."""
        url = reverse("pages:home")
        assert url == "/"

        resolver = resolve("/")
        assert resolver.func.view_class == views.HomePageView
        assert resolver.view_name == "pages:home"

    def test_about_url(self):
        """Тест URL страницы 'О компании'."""
        url = reverse("pages:about")
        assert url == "/about/"

        resolver = resolve("/about/")
        assert resolver.func.view_class == views.AboutPageView
        assert resolver.view_name == "pages:about"

    def test_app_name(self):
        """Тест что app_name установлен правильно."""
        from django.urls import get_resolver

        resolver = get_resolver()
        assert "pages" in resolver.app_dict

    def test_reverse_names(self):
        """Тест обратного резолвинга имен."""
        assert reverse("pages:home") == "/"
        assert reverse("pages:about") == "/about/"

    def test_url_patterns_count(self):
        """Тест количества URL-ов."""
        from pages.urls import urlpatterns

        assert len(urlpatterns) == 2
