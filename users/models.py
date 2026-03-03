from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from appointments.models import Appointment
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    """
    Кастомная модель пользователя, расширяющая стандартную AbstractUser.
    Добавляет дополнительные поля для медицинского центра.
    """
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Телефон"),
        blank=True,
        help_text=_("Номер телефона в формате +7 (XXX) XXX-XX-XX")
    )
    birth_date = models.DateField(
        verbose_name=_("Дата рождения"),
        null=True,
        blank=True
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        verbose_name=_("Аватар"),
        blank=True,
        null=True
    )
    passport_data = models.CharField(
        max_length=255,
        verbose_name=_("Паспортные данные"),
        blank=True,
        help_text=_("Серия и номер паспорта, кем выдан")
    )
    insurance_policy = models.CharField(
        max_length=50,
        verbose_name=_("Полис"),
        blank=True
    )

    # Связь с услугами (избранное)
    favorite_services = models.ManyToManyField(
        'services.Service',
        verbose_name=_("Избранные услуги"),
        blank=True,
        related_name='favorite_by'
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.last_name} {self.first_name}".strip() or self.username

    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        full_name = f"{self.last_name} {self.first_name}".strip()
        return full_name or self.username

    def get_short_name(self):
        """Возвращает сокращенное имя пользователя."""
        return self.first_name or self.username

    def get_upcoming_appointments(self):
        """Возвращает предстоящие записи пользователя."""
        return Appointment.objects.filter(
            user=self,
            date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).order_by('date', 'time')
