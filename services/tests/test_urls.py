import pytest
from django.urls import resolve, reverse

from services import views


class TestServicesUrls:
    """
    Тесты для URL-ов приложения services.
    """

    def test_service_list_url(self):
        """Тест URL списка услуг."""
        url = reverse("services:service_list")
        assert url == "/services/"

        resolver = resolve("/services/")
        assert resolver.func.view_class == views.ServiceListView
        assert resolver.view_name == "services:service_list"
        assert resolver.app_name == "services"

    def test_service_detail_url(self):
        """Тест URL детальной страницы услуги."""
        slug = "test-service"
        url = reverse("services:service_detail", args=[slug])
        assert url == f"/services/{slug}/"

        resolver = resolve(f"/services/{slug}/")
        assert resolver.func.view_class == views.ServiceDetailView
        assert resolver.view_name == "services:service_detail"
        assert resolver.kwargs["slug"] == slug

    def test_service_detail_with_different_slug(self):
        """Тест URL с разными slug."""
        test_slugs = ["mrt", "uzi", "rentgen", "kompyuternaya-tomografiya"]

        for slug in test_slugs:
            url = reverse("services:service_detail", args=[slug])
            assert url == f"/services/{slug}/"

            resolver = resolve(f"/services/{slug}/")
            assert resolver.kwargs["slug"] == slug

    def test_app_name(self):
        """Тест что app_name установлен правильно."""
        from django.urls import get_resolver

        resolver = get_resolver()
        assert "services" in resolver.app_dict

    def test_reverse_names(self):
        """Тест обратного резолвинга имен."""
        assert reverse("services:service_list") == "/services/"
        assert reverse("services:service_detail", args=["test"]) == "/services/test/"

    def test_url_patterns_count(self):
        """Тест количества URL-ов."""
        from services.urls import urlpatterns

        assert len(urlpatterns) == 2
