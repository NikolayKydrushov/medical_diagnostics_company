from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class ContactInfo(models.Model):
    """
    Модель контактной информации компании.
    Реализована как Singleton (может быть только одна запись).
    """

    address = models.CharField(max_length=300, verbose_name=_("Адрес"))
    phone = models.CharField(max_length=20, verbose_name=_("Телефон"))
    email = models.EmailField(verbose_name=_("Email"))
    map_url = models.URLField(
        verbose_name=_("Ссылка на карту"),
        blank=True,
        help_text=_("Ссылка на Яндекс.Карты или Google Maps"),
    )
    work_hours = models.CharField(
        max_length=200,
        verbose_name=_("Режим работы"),
        default="Пн-Пт: 9:00-20:00, Сб: 10:00-18:00, Вс: выходной",
    )
    vk_url = models.URLField(verbose_name=_("ВКонтакте"), blank=True)
    telegram_url = models.URLField(verbose_name=_("Telegram"), blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        verbose_name = _("Контактная информация")
        verbose_name_plural = _("Контактная информация")

    def __str__(self):
        return "Контактная информация компании"

    def clean(self):
        """Проверка на единственность записи."""
        if not self.pk and ContactInfo.objects.exists():
            raise ValidationError(
                "Можно создать только одну запись контактной информации"
            )

    def save(self, *args, **kwargs):
        """Переопределяем save для гарантии единственной записи."""
        self.clean()
        super().save(*args, **kwargs)


class FeedbackMessage(models.Model):
    """
    Модель сообщений обратной связи от посетителей.
    """

    name = models.CharField(max_length=100, verbose_name=_("Имя"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Телефон"),
        blank=True,
        help_text=_("Для обратной связи"),
    )
    message = models.TextField(verbose_name=_("Сообщение"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Дата отправки")
    )
    is_processed = models.BooleanField(
        default=False,
        verbose_name=_("Обработано"),
        help_text=_("Отмечено как обработанное"),
    )
    processed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Дата обработки")
    )
    processed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Обработал"),
        related_name="processed_messages",
    )

    class Meta:
        verbose_name = _("Сообщение обратной связи")
        verbose_name_plural = _("Сообщения обратной связи")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Сообщение от {self.name} ({self.created_at.strftime('%d.%m.%Y')})"
