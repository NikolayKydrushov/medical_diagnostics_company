import pytest
from django.urls import resolve, reverse

from appointments import views


class TestAppointmentsUrls:
    """
    Тесты для URL-ов приложения appointments.
    """

    def test_dashboard_url(self):
        """Тест URL личного кабинета."""
        url = reverse("appointments:dashboard")
        assert url == "/appointments/dashboard/"

        resolver = resolve("/appointments/dashboard/")
        assert resolver.func.view_class == views.DashboardView
        assert resolver.view_name == "appointments:dashboard"

    def test_appointment_create_url(self):
        """Тест URL создания записи."""
        url = reverse("appointments:appointment_create")
        assert url == "/appointments/create/"

        resolver = resolve("/appointments/create/")
        assert resolver.func.view_class == views.AppointmentCreateView
        assert resolver.view_name == "appointments:appointment_create"

    def test_appointment_create_with_service_url(self):
        """Тест URL создания записи с услугой."""
        slug = "test-service"
        url = reverse("appointments:appointment_create_with_service", args=[slug])
        assert url == f"/appointments/create/{slug}/"

        resolver = resolve(f"/appointments/create/{slug}/")
        assert resolver.func.view_class == views.AppointmentCreateView
        assert resolver.kwargs["service_slug"] == slug

    def test_appointment_history_url(self):
        """Тест URL истории записей."""
        url = reverse("appointments:appointment_history")
        assert url == "/appointments/history/"

        resolver = resolve("/appointments/history/")
        assert resolver.func.view_class == views.AppointmentHistoryView
        assert resolver.view_name == "appointments:appointment_history"

    def test_appointment_detail_url(self):
        """Тест URL детальной страницы записи."""
        url = reverse("appointments:appointment_detail", args=[1])
        assert url == "/appointments/1/"

        resolver = resolve("/appointments/1/")
        assert resolver.func.view_class == views.AppointmentDetailView
        # Исправление: сравниваем число с числом, преобразуем строку в int
        assert int(resolver.kwargs["pk"]) == 1

    def test_appointment_cancel_url(self):
        """Тест URL отмены записи."""
        url = reverse("appointments:appointment_cancel", args=[1])
        assert url == "/appointments/1/cancel/"

        resolver = resolve("/appointments/1/cancel/")
        assert resolver.func.view_class == views.AppointmentCancelView
        # Исправление: сравниваем число с числом
        assert int(resolver.kwargs["pk"]) == 1

    def test_result_detail_url(self):
        """Тест URL просмотра результатов."""
        url = reverse("appointments:result_detail", args=[1])
        assert url == "/appointments/result/1/"

        resolver = resolve("/appointments/result/1/")
        assert resolver.func.view_class == views.ResultDetailView
        # Исправление: сравниваем число с числом
        assert int(resolver.kwargs["pk"]) == 1

    def test_app_name(self):
        """Тест что app_name установлен правильно."""
        from django.urls import get_resolver

        resolver = get_resolver()
        assert "appointments" in resolver.app_dict

    def test_url_patterns_count(self):
        """Тест количества URL-ов."""
        from appointments.urls import urlpatterns

        assert len(urlpatterns) == 7
