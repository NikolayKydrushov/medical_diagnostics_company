from datetime import date, datetime, time, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from appointments.models import Appointment, DiagnosticResult
from doctors.models import Doctor
from services.models import Service
from users.models import User


@pytest.mark.django_db
class TestAppointmentModel:
    """
    Тесты для модели Appointment.
    """

    def test_create_appointment(self, user, service, doctor):
        """Тест создания записи на прием."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            doctor=doctor,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
            patient_comment="Тестовый комментарий",
        )

        assert appointment.user == user
        assert appointment.service == service
        assert appointment.doctor == doctor
        assert appointment.date == date.today() + timedelta(days=1)
        assert appointment.time == time(10, 0)
        assert appointment.status == Appointment.Status.PENDING
        assert appointment.patient_comment == "Тестовый комментарий"
        assert appointment.admin_comment == ""

    def test_appointment_str_method(self, user, service):
        """Тест строкового представления."""
        appointment = Appointment.objects.create(
            user=user, service=service, date=date.today(), time=time(10, 0)
        )
        expected = f"{user} - {service} - {date.today()}"
        assert str(appointment) == expected

    def test_appointment_unique_together(self, user, service, doctor):
        """Тест уникальности комбинации врач-дата-время."""
        appointment_date = date.today() + timedelta(days=1)
        appointment_time = time(10, 0)

        Appointment.objects.create(
            user=user,
            service=service,
            doctor=doctor,
            date=appointment_date,
            time=appointment_time,
        )

        # Пытаемся создать вторую запись на то же время
        with pytest.raises(IntegrityError):
            Appointment.objects.create(
                user=user,
                service=service,
                doctor=doctor,
                date=appointment_date,
                time=appointment_time,
            )

    def test_appointment_is_past_property(self, user, service):
        """Тест свойства is_past."""
        # Запись на прошлую дату
        past_appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() - timedelta(days=1),
            time=time(10, 0),
        )
        assert past_appointment.is_past is True

        # Запись на будущую дату
        future_appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
        )
        assert future_appointment.is_past is False

    def test_appointment_can_cancel_property(self, user, service):
        """Тест свойства can_cancel."""
        # Запись со статусом PENDING
        appointment1 = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.PENDING,
        )
        assert appointment1.can_cancel is True

        # Запись со статусом CONFIRMED
        appointment2 = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.CONFIRMED,
        )
        assert appointment2.can_cancel is True

        # Запись со статусом COMPLETED
        appointment3 = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() - timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )
        assert appointment3.can_cancel is False

        # Запись со статусом CANCELLED
        appointment4 = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.CANCELLED,
        )
        assert appointment4.can_cancel is False

    def test_appointment_can_cancel_time_limit(self, user, service):
        """Тест что нельзя отменить запись менее чем за 2 часа."""
        # Запись через 3 часа
        future_time = (timezone.now() + timedelta(hours=3)).time()
        if future_time < datetime.now().time():
            future_date = datetime.now().date() + timedelta(days=1)
        else:
            future_date = datetime.now().date()

        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=future_date,
            time=future_time,
            status=Appointment.Status.CONFIRMED,
        )
        assert appointment.can_cancel is True

        # Запись через 1 час
        one_hour_later = (timezone.now() + timedelta(hours=1)).time()

        # Если время перевалило за полночь, то дата должна быть завтра
        if one_hour_later < timezone.now().time():
            appointment_date = timezone.now().date() + timedelta(days=1)
        else:
            appointment_date = timezone.now().date()

        appointment2 = Appointment.objects.create(
            user=user,
            service=service,
            date=appointment_date,
            time=one_hour_later,
            status=Appointment.Status.CONFIRMED,
        )
        assert appointment2.can_cancel is False

    def test_appointment_ordering(self, user, service):
        """Тест сортировки записей."""
        app1 = Appointment.objects.create(
            user=user, service=service, date=date.today(), time=time(9, 0)
        )
        app2 = Appointment.objects.create(
            user=user, service=service, date=date.today(), time=time(10, 0)
        )
        app3 = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today() + timedelta(days=1),
            time=time(9, 0),
        )

        appointments = Appointment.objects.all()
        # Должны сортироваться по убыванию даты и времени
        assert appointments[0] == app3  # Завтра
        assert appointments[1] == app2  # Сегодня 10:00
        assert appointments[2] == app1  # Сегодня 9:00

    def test_appointment_status_choices(self, user, service):
        """Тест выбора статуса."""
        appointment = Appointment.objects.create(
            user=user, service=service, date=date.today(), time=time(10, 0)
        )

        assert appointment.status == Appointment.Status.PENDING

        appointment.status = Appointment.Status.CONFIRMED
        appointment.save()
        assert appointment.status == Appointment.Status.CONFIRMED

        appointment.status = Appointment.Status.COMPLETED
        appointment.save()
        assert appointment.status == Appointment.Status.COMPLETED

        appointment.status = Appointment.Status.CANCELLED
        appointment.save()
        assert appointment.status == Appointment.Status.CANCELLED

        appointment.status = Appointment.Status.NO_SHOW
        appointment.save()
        assert appointment.status == Appointment.Status.NO_SHOW

    def test_appointment_meta_verbose_names(self):
        """Тест verbose names в Meta классе."""
        assert Appointment._meta.verbose_name == "Запись на прием"
        assert Appointment._meta.verbose_name_plural == "Записи на прием"


@pytest.mark.django_db
class TestDiagnosticResultModel:
    """
    Тесты для модели DiagnosticResult.
    """

    def test_create_diagnostic_result(self, user, service, doctor):
        """Тест создания результата диагностики."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            doctor=doctor,
            date=date.today() - timedelta(days=1),
            time=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )

        result = DiagnosticResult.objects.create(
            appointment=appointment,
            result_file="results/test/file.pdf",
            doctor_comment="Все показатели в норме",
        )

        assert result.appointment == appointment
        assert result.result_file == "results/test/file.pdf"
        assert result.doctor_comment == "Все показатели в норме"

    def test_diagnostic_result_str_method(self, user, service):
        """Тест строкового представления."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today(),
            time=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )

        result = DiagnosticResult.objects.create(
            appointment=appointment, result_file="test.pdf"
        )

        assert str(result) == f"Результаты для {appointment}"

    def test_diagnostic_result_one_to_one(self, user, service):
        """Тест связи один-к-одному."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today(),
            time=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )

        DiagnosticResult.objects.create(appointment=appointment, result_file="test.pdf")

        # Пытаемся создать второй результат для той же записи
        with pytest.raises(IntegrityError):
            DiagnosticResult.objects.create(
                appointment=appointment, result_file="test2.pdf"
            )

    def test_diagnostic_result_clean_method(self, user, service):
        """Тест валидации - результат только для завершенных записей."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today(),
            time=time(10, 0),
            status=Appointment.Status.PENDING,
        )

        result = DiagnosticResult(appointment=appointment, result_file="test.pdf")

        with pytest.raises(ValidationError):
            result.clean()

    def test_diagnostic_result_timestamps(self, user, service):
        """Тест временных меток."""
        appointment = Appointment.objects.create(
            user=user,
            service=service,
            date=date.today(),
            time=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )

        result = DiagnosticResult.objects.create(
            appointment=appointment, result_file="test.pdf"
        )

        assert result.uploaded_at is not None
        assert result.updated_at is not None

        old_updated = result.updated_at
        result.doctor_comment = "Новый комментарий"
        result.save()
        result.refresh_from_db()
        assert result.updated_at > old_updated

    def test_diagnostic_result_meta_verbose_names(self):
        """Тест verbose names."""
        assert DiagnosticResult._meta.verbose_name == "Результат диагностики"
        assert DiagnosticResult._meta.verbose_name_plural == "Результаты диагностики"
