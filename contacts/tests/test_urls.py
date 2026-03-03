import pytest
from django.urls import resolve, reverse

from contacts import views


class TestContactsUrls:
    """
    Тесты для URL-ов приложения contacts.
    """

    def test_contact_url(self):
        """Тест URL страницы контактов."""
        url = reverse("contacts:contact")
        assert url == "/contacts/"

        resolver = resolve("/contacts/")
        assert resolver.func.view_class == views.ContactView
        assert resolver.view_name == "contacts:contact"
        assert resolver.app_name == "contacts"

    def test_thank_you_url(self):
        """Тест URL страницы благодарности."""
        url = reverse("contacts:thank_you")
        assert url == "/contacts/thank-you/"

        resolver = resolve("/contacts/thank-you/")
        assert resolver.func.view_class == views.ContactThankYouView
        assert resolver.view_name == "contacts:thank_you"

    def test_app_name(self):
        """Тест что app_name установлен правильно."""
        from django.urls import get_resolver

        resolver = get_resolver()
        assert "contacts" in resolver.app_dict

    def test_reverse_names(self):
        """Тест обратного резолвинга имен."""
        assert reverse("contacts:contact") == "/contacts/"
        assert reverse("contacts:thank_you") == "/contacts/thank-you/"

    def test_url_patterns_count(self):
        """Тест количества URL-ов."""
        from contacts.urls import urlpatterns

        assert len(urlpatterns) == 2
