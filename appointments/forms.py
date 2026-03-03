from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from doctors.models import Doctor
from services.models import Service

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    """
    Форма для создания записи на прием.
    """

    class Meta:
        model = Appointment
        fields = ["service", "doctor", "date", "time", "patient_comment"]
        widgets = {
            "service": forms.Select(attrs={"class": "form-control"}),
            "doctor": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "min": timezone.now().date().isoformat(),
                }
            ),
            "time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "patient_comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Укажите дополнительные пожелания или симптомы",
                }
            ),
        }
        labels = {
            "service": _("Услуга"),
            "doctor": _("Врач"),
            "date": _("Дата приема"),
            "time": _("Время приема"),
            "patient_comment": _("Комментарий"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Фильтруем только активные услуги
        self.fields["service"].queryset = Service.objects.filter(is_active=True)

        # Если услуга выбрана, фильтруем врачей
        if "service" in self.data:
            try:
                service_id = int(self.data.get("service"))
                self.fields["doctor"].queryset = Doctor.objects.filter(
                    services__id=service_id, is_active=True
                ).distinct()
            except (ValueError, TypeError):
                self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True)
        elif self.instance.pk and self.instance.service:
            self.fields["doctor"].queryset = self.instance.service.doctors.filter(
                is_active=True
            )
        else:
            self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True)

    def clean_date(self):
        """Проверка, что дата не в прошлом."""
        date = self.cleaned_data.get("date")
        if date and date < timezone.now().date():
            raise forms.ValidationError("Дата не может быть в прошлом")
        return date

    def clean(self):
        """Проверка, что выбранный врач оказывает выбранную услугу."""
        cleaned_data = super().clean()
        service = cleaned_data.get("service")
        doctor = cleaned_data.get("doctor")

        if service and doctor:
            if not doctor.services.filter(id=service.id).exists():
                raise forms.ValidationError("Выбранный врач не оказывает эту услугу")

        return cleaned_data


class AppointmentCancelForm(forms.ModelForm):
    """
    Форма для подтверждения отмены записи.
    """

    confirm = forms.BooleanField(
        required=True,
        label=_("Я подтверждаю отмену записи"),
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Appointment
        fields = []  # Нет полей для редактирования

    def clean_confirm(self):
        confirm = self.cleaned_data.get("confirm")
        if not confirm:
            raise forms.ValidationError("Необходимо подтвердить отмену")
        return confirm
