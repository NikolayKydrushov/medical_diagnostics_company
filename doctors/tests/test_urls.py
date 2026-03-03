import pytest
from django.urls import resolve, reverse

from doctors import views


class TestDoctorsUrls:
    """
    Тесты для URL-ов приложения doctors.
    """

    def test_doctor_list_url(self):
        """Тест URL списка врачей."""
        url = reverse("doctors:doctor_list")
        assert url == "/doctors/"

        resolver = resolve("/doctors/")
        assert resolver.func.view_class == views.DoctorListView
        assert resolver.view_name == "doctors:doctor_list"
        assert resolver.app_name == "doctors"

    def test_doctor_detail_url(self):
        """Тест URL детальной страницы врача."""
        slug = "ivanov-ivan"
        url = reverse("doctors:doctor_detail", args=[slug])
        assert url == f"/doctors/{slug}/"

        resolver = resolve(f"/doctors/{slug}/")
        assert resolver.func.view_class == views.DoctorDetailView
        assert resolver.view_name == "doctors:doctor_detail"
        assert resolver.kwargs["slug"] == slug

    def test_doctor_detail_with_different_slug(self):
        """Тест URL с разными slug."""
        test_slugs = ["ivanov-ivan", "petrov-petr", "sidorov-1"]

        for slug in test_slugs:
            url = reverse("doctors:doctor_detail", args=[slug])
            assert url == f"/doctors/{slug}/"

            resolver = resolve(f"/doctors/{slug}/")
            assert resolver.kwargs["slug"] == slug

    def test_app_name(self):
        """Тест что app_name установлен правильно."""
        from django.urls import get_resolver

        resolver = get_resolver()
        assert "doctors" in resolver.app_dict

    def test_reverse_names(self):
        """Тест обратного резолвинга имен."""
        assert reverse("doctors:doctor_list") == "/doctors/"
        assert reverse("doctors:doctor_detail", args=["test"]) == "/doctors/test/"

    def test_url_patterns_count(self):
        """Тест количества URL-ов."""
        from doctors.urls import urlpatterns

        assert len(urlpatterns) == 2
