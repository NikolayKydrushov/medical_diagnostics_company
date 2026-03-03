from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone

# Create your models here.

class Appointment(models.Model):
    """
    Модель записи на прием.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', _('Ожидает подтверждения')
        CONFIRMED = 'confirmed', _('Подтвержден')
        COMPLETED = 'completed', _('Завершен')
        CANCELLED = 'cancelled', _('Отменен')
        NO_SHOW = 'no_show', _('Не явился')

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name=_("Пациент"),
        related_name='appointments'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.PROTECT,
        verbose_name=_("Услуга"),
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.PROTECT,
        verbose_name=_("Врач"),
        related_name='appointments',
        null=True,
        blank=True
    )
    date = models.DateField(
        verbose_name=_("Дата приема"),
        db_index=True
    )
    time = models.TimeField(
        verbose_name=_("Время приема")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Статус"),
        db_index=True
    )
    patient_comment = models.TextField(
        verbose_name=_("Комментарий пациента"),
        blank=True,
        help_text=_("Дополнительная информация к записи")
    )
    admin_comment = models.TextField(
        verbose_name=_("Комментарий администратора"),
        blank=True,
        help_text=_("Внутренние заметки")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания записи")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Запись на прием")
        verbose_name_plural = _("Записи на прием")
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['user', '-date']),
        ]
        # Запрещаем двойную запись на одно время к одному врачу
        unique_together = ['doctor', 'date', 'time']

    def __str__(self):
        return f"{self.user} - {self.service} - {self.date}"

    @property
    def is_past(self):
        """Проверка, прошла ли запись."""
        appointment_datetime = timezone.datetime.combine(self.date, self.time)
        return timezone.make_aware(appointment_datetime) < timezone.now()

    @property
    def can_cancel(self):
        """Может ли пациент отменить запись."""
        if self.status in [self.Status.PENDING, self.Status.CONFIRMED]:
            appointment_datetime = timezone.datetime.combine(self.date, self.time)
            # Можно отменить за 2 часа до приема
            return (timezone.make_aware(appointment_datetime) - timezone.now()).total_seconds() > 7200
        return False


class DiagnosticResult(models.Model):
    """
    Модель результатов диагностики.
    Привязывается к завершенной записи.
    """
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        verbose_name=_("Запись"),
        related_name='diagnostic_result',
        limit_choices_to={'status': Appointment.Status.COMPLETED}
    )
    result_file = models.FileField(
        upload_to='results/%Y/%m/%d/',
        verbose_name=_("Файл с результатами"),
        help_text=_("PDF, изображения или архивы")
    )
    doctor_comment = models.TextField(
        verbose_name=_("Заключение врача"),
        blank=True
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата загрузки")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Результат диагностики")
        verbose_name_plural = _("Результаты диагностики")

    def __str__(self):
        return f"Результаты для {self.appointment}"

    def clean(self):
        """Валидация - результаты можно добавить только к завершенным записям."""
        if self.appointment.status != Appointment.Status.COMPLETED:
            from django.core.exceptions import ValidationError
            raise ValidationError("Результаты можно добавить только к завершенным записям")
