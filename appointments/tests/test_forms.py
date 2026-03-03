from datetime import date, time, timedelta

import pytest
from django.utils import timezone

from appointments.forms import AppointmentCancelForm, AppointmentForm
from appointments.models import Appointment
from doctors.models import Doctor
from services.models import Service


@pytest.mark.django_db
class TestAppointmentForm:
    """
    Тесты для формы создания записи.
    """

    def test_valid_appointment_form(self, service, doctor):
        """Тест валидной формы."""
        service.doctors.add(doctor)
        tomorrow = date.today() + timedelta(days=1)

        form_data = {
            "service": service.id,
            "doctor": doctor.id,
            "date": tomorrow.isoformat(),
            "time": "10:00",
            "patient_comment": "Тестовый комментарий",
        }
        form = AppointmentForm(data=form_data)
        assert form.is_valid()

    def test_appointment_form_required_fields(self):
        """Тест обязательных полей."""
        form = AppointmentForm(data={})
        assert not form.is_valid()
        assert "service" in form.errors
        assert len(form.errors) > 0

    def test_appointment_form_date_in_past(self, service, doctor):
        """Тест что нельзя выбрать дату в прошлом."""
        service.doctors.add(doctor)
        yesterday = date.today() - timedelta(days=1)

        form_data = {
            "service": service.id,
            "doctor": doctor.id,
            "date": yesterday.isoformat(),
            "time": "10:00",
        }
        form = AppointmentForm(data=form_data)
        assert not form.is_valid()
        assert "date" in form.errors

    def test_appointment_form_doctor_service_mismatch(
        self, service, doctor, another_doctor
    ):
        """Тест что врач должен оказывать выбранную услугу."""
        # Не добавляем доктора к услуге
        form_data = {
            "service": service.id,
            "doctor": doctor.id,  # Этот врач не оказывает услугу
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "time": "10:00",
        }
        form = AppointmentForm(data=form_data)
        assert not form.is_valid()
        # Проверяем что есть ошибка в поле doctor
        assert "doctor" in form.errors

    def test_appointment_form_doctor_filtering(self, service, doctor, another_doctor):
        """Тест фильтрации врачей по услуге."""
        # Добавляем только одного врача к услуге
        service.doctors.add(doctor)

        form = AppointmentForm(data={"service": service.id})

        # Проверяем что в queryset врачей только те, кто оказывает услугу
        doctor_queryset = form.fields["doctor"].queryset
        assert doctor in doctor_queryset
        assert another_doctor not in doctor_queryset

    def test_appointment_form_widgets(self):
        """Тест наличия виджетов."""
        form = AppointmentForm()

        assert "form-control" in form.fields["service"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["doctor"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["date"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["time"].widget.attrs.get("class", "")
        assert "form-control" in form.fields["patient_comment"].widget.attrs.get(
            "class", ""
        )

        # Проверка атрибута min для даты
        assert "min" in form.fields["date"].widget.attrs
        assert form.fields["date"].widget.attrs["min"] == date.today().isoformat()

    def test_appointment_form_labels(self):
        """Тест меток полей."""
        form = AppointmentForm()

        assert form.fields["service"].label == "Услуга"
        assert form.fields["doctor"].label == "Врач"
        assert form.fields["date"].label == "Дата приема"
        assert form.fields["time"].label == "Время приема"
        assert form.fields["patient_comment"].label == "Комментарий"


@pytest.mark.django_db
class TestAppointmentCancelForm:
    """
    Тесты для формы отмены записи.
    """

    def test_valid_cancel_form(self):
        """Тест валидной формы отмены."""
        form_data = {"confirm": True}
        form = AppointmentCancelForm(data=form_data)
        assert form.is_valid()

    def test_cancel_form_confirm_required(self):
        """Тест что подтверждение обязательно."""
        form_data = {"confirm": False}
        form = AppointmentCancelForm(data=form_data)
        assert not form.is_valid()
        assert "confirm" in form.errors

    def test_cancel_form_no_fields(self):
        """Тест что форма не содержит полей модели."""
        form = AppointmentCancelForm()
        assert form.Meta.fields == []
