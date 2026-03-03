from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Service(models.Model):
    """
    Модель медицинской услуги.
    """

    name = models.CharField(
        max_length=200, verbose_name=_("Название услуги"), db_index=True
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        verbose_name=_("URL-идентификатор"),
        help_text=_("Уникальный идентификатор для URL, генерируется из названия"),
    )
    short_description = models.TextField(
        max_length=300,
        verbose_name=_("Краткое описание"),
        help_text=_("Отображается в списке услуг"),
    )
    full_description = models.TextField(
        verbose_name=_("Полное описание"),
        blank=True,
        help_text=_("Детальное описание на странице услуги"),
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Цена"),
        help_text=_("Стоимость услуги в рублях"),
    )
    image = models.ImageField(
        upload_to="services/",
        verbose_name=_("Изображение"),
        blank=True,
        null=True,
        help_text=_("Иллюстрация для услуги"),
    )
    duration = models.PositiveIntegerField(
        verbose_name=_("Длительность (минут)"),
        default=30,
        help_text=_("Среднее время приема в минутах"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активна"),
        help_text=_("Отображать ли услугу на сайте"),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Порядок сортировки"),
        help_text=_("Чем меньше число, тем выше в списке"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        verbose_name = _("Услуга")
        verbose_name_plural = _("Услуги")
        ordering = ["order", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "order"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Автоматическое создание slug из названия."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Возвращает URL детальной страницы услуги."""
        return reverse("services:service_detail", args=[self.slug])

    def get_price_formatted(self):
        """Возвращает отформатированную цену."""
        return f"{self.price:.2f} ₽"
