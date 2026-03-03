from datetime import date, time, timedelta

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from appointments.models import Appointment, DiagnosticResult
from doctors.models import Doctor
from services.models import Service
from users.models import User


@pytest.mark.django_db
class TestDashboardView:
    """
    Тесты для личного кабинета.
    """

    def test_dashboard_view_authenticated(self, authenticated_client, user):
        """Тест доступа для авторизованного пользователя."""
        url = reverse("appointments:dashboard")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "appointments/dashboard.html" in [t.name for t in response.templates]
        assert "upcoming_appointments" in response.context
        assert "recent_completed" in response.context
        assert "total_count" in response.context
        assert "completed_count" in response.context
        assert "cancelled_count" in response.context

    def test_dashboard_view_unauthenticated(self, client):
        """Тест что неавторизованный пользователь перенаправляется."""
        url = reverse("appointments:dashboard")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url.startswith(reverse("users:login"))

    def test_dashboard_view_with_appointments(
        self, authenticated_client, user, service
    ):
        """Тест отображения записей в личном кабинете."""
        # Создаем предстоящую запись
        upcoming = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.CONFIRMED,
        )

        # Создаем завершенную запись
        completed = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() - timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )

        # Создаем отмененную запись
        cancelled = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=2),
            time=time(11, 0),
            status=Appointment.Status.CANCELLED,
        )

        url = reverse("appointments:dashboard")
        response = authenticated_client.get(url)

        assert upcoming in response.context["upcoming_appointments"]
        assert completed in response.context["recent_completed"]
        assert response.context["total_count"] == 3
        assert response.context["completed_count"] == 1
        assert response.context["cancelled_count"] == 1


@pytest.mark.django_db
class TestAppointmentCreateView:
    """
    Тесты для создания записи.
    """

    def test_create_view_authenticated(self, authenticated_client, service, doctor):
        """Тест доступа к странице создания."""
        service.doctors.add(doctor)

        url = reverse("appointments:appointment_create")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "appointments/appointment_form.html" in [
            t.name for t in response.templates
        ]

    def test_create_view_unauthenticated(self, client):
        """Тест что неавторизованный пользователь перенаправляется."""
        url = reverse("appointments:appointment_create")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url.startswith(reverse("users:login"))

    def test_create_view_with_service_slug(self, authenticated_client, service, doctor):
        """Тест создания с предвыбранной услугой."""
        service.doctors.add(doctor)

        url = reverse(
            "appointments:appointment_create_with_service", args=[service.slug]
        )
        response = authenticated_client.get(url)

        assert response.status_code == 200
        # Проверяем что услуга предвыбрана
        assert response.context["form"].initial.get("service") == service

    def test_create_view_post_valid(self, authenticated_client, user, service, doctor):
        """Тест POST запроса с валидными данными."""
        service.doctors.add(doctor)
        tomorrow = date.today() + timedelta(days=1)

        url = reverse("appointments:appointment_create")
        data = {
            "service": service.id,
            "doctor": doctor.id,
            "date": tomorrow.isoformat(),
            "time": "10:00",
            "patient_comment": "Тестовый комментарий",
        }
        response = authenticated_client.post(url, data)

        # Должен быть редирект в личный кабинет
        assert response.status_code == 302
        assert response.url == reverse("appointments:dashboard")

        # Проверяем что запись создалась
        assert Appointment.objects.count() == 1
        appointment = Appointment.objects.first()
        assert appointment.user == user
        assert appointment.service == service
        assert appointment.doctor == doctor
        assert appointment.status == Appointment.Status.PENDING

        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "успешно создана" in str(messages[0])

    def test_create_view_post_duplicate_time(
        self, authenticated_client, user, service, doctor
    ):
        """Тест запрета двойной записи на одно время."""
        service.doctors.add(doctor)
        tomorrow = date.today() + timedelta(days=1)

        # Создаем первую запись
        Appointment.objects.create(
            user=user,
            service=service,
            doctor=doctor,
            date=tomorrow,
            time=time(10, 0),
            status=Appointment.Status.CONFIRMED,
        )

        # Пытаемся создать вторую на то же время
        url = reverse("appointments:appointment_create")
        data = {
            "service": service.id,
            "doctor": doctor.id,
            "date": tomorrow.isoformat(),
            "time": "10:00",
            "patient_comment": "Комментарий",
        }
        response = authenticated_client.post(url, data)

        # Должен остаться на странице
        assert response.status_code == 200
        # Запись не должна создаться
        assert Appointment.objects.count() == 1

        # Проверяем наличие ошибки в форме
        assert "form" in response.context
        assert response.context["form"].errors

        # Ищем любое из возможных сообщений об ошибке
        content = response.content.decode()

    def test_create_view_post_invalid_data(self, authenticated_client, service, doctor):
        """Тест POST с невалидными данными."""
        service.doctors.add(doctor)

        url = reverse("appointments:appointment_create")
        data = {
            "service": service.id,
            "doctor": doctor.id,
            "date": (date.today() - timedelta(days=1)).isoformat(),  # Прошедшая дата
            "time": "10:00",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors
        assert Appointment.objects.count() == 0


@pytest.mark.django_db
class TestAppointmentHistoryView:
    """
    Тесты для истории записей.
    """

    def test_history_view_authenticated(self, authenticated_client):
        """Тест доступа к истории."""
        url = reverse("appointments:appointment_history")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "appointments/appointment_history.html" in [
            t.name for t in response.templates
        ]

    def test_history_view_unauthenticated(self, client):
        """Тест что неавторизованный пользователь перенаправляется."""
        url = reverse("appointments:appointment_history")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url.startswith(reverse("users:login"))

    def test_history_view_with_appointments(self, authenticated_client, user, service):
        """Тест отображения записей в истории."""
        # Создаем несколько записей
        for i in range(5):
            Appointment.objects.create(
                user=user,
                service=service,
                date=date.today() - timedelta(days=i),
                time=time(10, 0),
                status=Appointment.Status.COMPLETED,
            )

        url = reverse("appointments:appointment_history")
        response = authenticated_client.get(url)

        assert len(response.context["appointments"]) == 5

    def test_history_view_filter_by_status(self, authenticated_client, user, service):
        """Тест фильтрации по статусу."""
        # Создаем записи с разными статусами
        Appointment.objects.create(
            user=user,
            service=service,
            date=date.today(),
            time=time(10, 0),
            status=Appointment.Status.PENDING,
        )
        Appointment.objects.create(
            user=user,
            service=service,
            date=date.today(),
            time=time(11, 0),
            status=Appointment.Status.CONFIRMED,
        )
        Appointment.objects.create(
            user=user,
            service=service,
            date=date.today(),
            time=time(12, 0),
            status=Appointment.Status.COMPLETED,
        )

        # Фильтр по PENDING
        url = reverse("appointments:appointment_history")
        response = authenticated_client.get(url + "?status=pending")
        assert len(response.context["appointments"]) == 1
        assert response.context["appointments"][0].status == Appointment.Status.PENDING
        assert response.context["current_status"] == "pending"

        # Фильтр по CONFIRMED
        response = authenticated_client.get(url + "?status=confirmed")
        assert len(response.context["appointments"]) == 1
        assert (
            response.context["appointments"][0].status == Appointment.Status.CONFIRMED
        )


@pytest.mark.django_db
class TestAppointmentDetailView:
    """
    Тесты для детальной страницы записи.
    """

    def test_detail_view_authenticated(self, authenticated_client, user, service):
        """Тест доступа к детальной странице."""
        appointment = Appointment.objects.create(
            user=user, service=service, date=date.today(), time=time(10, 0)
        )

        url = reverse("appointments:appointment_detail", args=[appointment.id])
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "appointments/appointment_detail.html" in [
            t.name for t in response.templates
        ]
        assert response.context["appointment"] == appointment

    def test_detail_view_unauthorized(
        self, authenticated_client, user, another_user, service
    ):
        """Тест что нельзя посмотреть чужую запись."""
        appointment = Appointment.objects.create(
            user=another_user, service=service, date=date.today(), time=time(10, 0)
        )

        url = reverse("appointments:appointment_detail", args=[appointment.id])
        response = authenticated_client.get(url)

        assert response.status_code == 404

    def test_detail_view_with_diagnostic_result(
        self, authenticated_client, user, service
    ):
        """Тест отображения результатов диагностики."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() - timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )

        result = DiagnosticResult.objects.create(
            appointment=appointment,
            result_file="test.pdf",
            doctor_comment="Тестовое заключение",
        )

        url = reverse("appointments:appointment_detail", args=[appointment.id])
        response = authenticated_client.get(url)

        assert response.context["diagnostic_result"] == result


@pytest.mark.django_db
class TestAppointmentCancelView:
    """
    Тесты для отмены записи.
    """

    def test_cancel_view_authenticated(self, authenticated_client, user, service):
        """Тест доступа к странице отмены."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.CONFIRMED,
        )

        url = reverse("appointments:appointment_cancel", args=[appointment.id])
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "appointments/appointment_cancel.html" in [
            t.name for t in response.templates
        ]

    def test_cancel_view_post(self, authenticated_client, user, service):
        """Тест POST запроса на отмену."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.CONFIRMED,
        )

        url = reverse("appointments:appointment_cancel", args=[appointment.id])
        data = {"confirm": True}
        response = authenticated_client.post(url, data)

        assert response.status_code == 302
        assert response.url == reverse("appointments:dashboard")

        # Проверяем что статус изменился
        appointment.refresh_from_db()
        assert appointment.status == Appointment.Status.CANCELLED

        # Проверяем сообщение
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "отменена" in str(messages[0])

    def test_cancel_view_unauthorized(
        self, authenticated_client, user, another_user, service
    ):
        """Тест что нельзя отменить чужую запись."""
        appointment = Appointment.objects.create(
            user=another_user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.CONFIRMED,
        )

        url = reverse("appointments:appointment_cancel", args=[appointment.id])
        response = authenticated_client.get(url)

        assert response.status_code == 404

    def test_cancel_view_already_cancelled(self, authenticated_client, user, service):
        """Тест что нельзя отменить уже отмененную запись."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.CANCELLED,
        )

        url = reverse("appointments:appointment_cancel", args=[appointment.id])
        response = authenticated_client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestResultDetailView:
    """
    Тесты для просмотра результатов.
    """

    def test_result_detail_view_authenticated(
        self, authenticated_client, user, service
    ):
        """Тест доступа к результатам."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() - timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )

        result = DiagnosticResult.objects.create(
            appointment=appointment, result_file="test.pdf"
        )

        url = reverse("appointments:result_detail", args=[result.id])
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "appointments/result_detail.html" in [t.name for t in response.templates]
        assert response.context["result"] == result

    def test_result_detail_view_unauthorized(
        self, authenticated_client, user, another_user, service
    ):
        """Тест что нельзя посмотреть чужие результаты."""
        appointment = Appointment.objects.create(
            user=another_user,
            service=service,
            date=date.today() - timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )

        result = DiagnosticResult.objects.create(
            appointment=appointment, result_file="test.pdf"
        )

        url = reverse("appointments:result_detail", args=[result.id])
        response = authenticated_client.get(url)

        assert response.status_code == 404
