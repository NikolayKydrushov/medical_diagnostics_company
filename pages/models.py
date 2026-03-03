from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Create your models here.

class HomePageContent(models.Model):
    """
    Контент главной страницы. Singleton модель.
    """
    # Hero секция
    hero_title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок главного баннера"),
        default="Медицинский диагностический центр"
    )
    hero_subtitle = models.TextField(
        max_length=500,
        verbose_name=_("Подзаголовок"),
        default="Современное оборудование и опытные врачи"
    )
    hero_image = models.ImageField(
        upload_to='pages/home/',
        verbose_name=_("Фоновое изображение"),
        blank=True,
        null=True
    )

    # О компании (кратко)
    about_title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок раздела 'О компании'"),
        default="О нашем центре"
    )
    about_text = models.TextField(
        verbose_name=_("Текст о компании"),
        help_text=_("Краткое описание для главной страницы")
    )
    about_image = models.ImageField(
        upload_to='pages/home/',
        verbose_name=_("Изображение"),
        blank=True,
        null=True
    )

    # Преимущества (можно хранить как JSON)
    advantages = models.JSONField(
        verbose_name=_("Преимущества"),
        default=list,
        help_text=_('Список преимуществ в формате [{"title": "...", "description": "..."}]')
    )

    # Статистика
    patients_count = models.PositiveIntegerField(
        verbose_name=_("Количество пациентов"),
        default=0,
        help_text=_("Для отображения статистики")
    )
    doctors_count = models.PositiveIntegerField(
        verbose_name=_("Количество врачей"),
        default=0
    )
    experience_years = models.PositiveIntegerField(
        verbose_name=_("Лет на рынке"),
        default=0
    )

    # SEO
    meta_title = models.CharField(
        max_length=200,
        verbose_name=_("Meta Title"),
        blank=True
    )
    meta_description = models.TextField(
        max_length=500,
        verbose_name=_("Meta Description"),
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Контент главной страницы")
        verbose_name_plural = _("Контент главной страницы")

    def __str__(self):
        return "Главная страница"

    def clean(self):
        if not self.pk and HomePageContent.objects.exists():
            raise ValidationError("Можно создать только одну запись контента главной страницы")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class AboutPageContent(models.Model):
    """
    Контент страницы "О компании". Singleton модель.
    """
    title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок страницы"),
        default="О компании"
    )

    # История
    history_title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок раздела истории"),
        default="Наша история"
    )
    history_text = models.TextField(
        verbose_name=_("Текст истории компании")
    )
    history_image = models.ImageField(
        upload_to='pages/about/',
        verbose_name=_("Изображение к истории"),
        blank=True,
        null=True
    )

    # Миссия
    mission_title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок миссии"),
        default="Наша миссия"
    )
    mission_text = models.TextField(
        verbose_name=_("Текст миссии")
    )

    # Ценности
    values_title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок ценностей"),
        default="Наши ценности"
    )
    values = models.JSONField(
        verbose_name=_("Ценности"),
        default=list,
        help_text=_('Список ценностей в формате [{"title": "...", "description": "..."}]')
    )

    # Оборудование
    equipment_title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок раздела оборудования"),
        default="Наше оборудование"
    )
    equipment_description = models.TextField(
        verbose_name=_("Описание оборудования"),
        blank=True
    )

    # SEO
    meta_title = models.CharField(
        max_length=200,
        verbose_name=_("Meta Title"),
        blank=True
    )
    meta_description = models.TextField(
        max_length=500,
        verbose_name=_("Meta Description"),
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Контент страницы 'О компании'")
        verbose_name_plural = _("Контент страницы 'О компании'")

    def __str__(self):
        return "Страница 'О компании'"

    def clean(self):
        if not self.pk and AboutPageContent.objects.exists():
            raise ValidationError("Можно создать только одну запись контента страницы 'О компании'")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
