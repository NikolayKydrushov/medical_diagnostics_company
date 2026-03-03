from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Doctor(models.Model):
    """
    Модель врача.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("ФИО врача"),
        db_index=True
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        verbose_name=_("URL-идентификатор"),
        blank=True
    )
    specialty = models.CharField(
        max_length=100,
        verbose_name=_("Специализация"),
        help_text=_("Например: кардиолог, невролог")
    )
    photo = models.ImageField(
        upload_to='doctors/',
        verbose_name=_("Фото"),
        blank=True,
        null=True
    )
    bio = models.TextField(
        verbose_name=_("Биография"),
        help_text=_("Образование, опыт, достижения")
    )
    experience_years = models.PositiveIntegerField(
        verbose_name=_("Стаж работы (лет)"),
        default=0
    )
    services = models.ManyToManyField(
        'services.Service',
        verbose_name=_("Услуги"),
        related_name='doctors',
        blank=True,
        help_text=_("Какие услуги оказывает врач")
    )
    email = models.EmailField(
        verbose_name=_("Email"),
        blank=True
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Телефон"),
        blank=True
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Порядок сортировки")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
        help_text=_("Отображать ли врача на сайте")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата добавления")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Врач")
        verbose_name_plural = _("Врачи")
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['specialty']),
        ]

    def __str__(self):
        return f"{self.name} - {self.specialty}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('doctors:doctor_detail', args=[self.slug])

    def get_experience_display(self):
        """Возвращает строку с опытом работы."""
        if self.experience_years == 0:
            return "Стаж не указан"
        elif self.experience_years == 1:
            return "1 год"
        elif 2 <= self.experience_years <= 4:
            return f"{self.experience_years} года"
        else:
            return f"{self.experience_years} лет"
