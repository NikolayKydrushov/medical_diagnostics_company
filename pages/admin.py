from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import AboutPageContent, HomePageContent

# Register your models here.


@admin.register(HomePageContent)
class HomePageContentAdmin(admin.ModelAdmin):
    """
    Админка для контента главной страницы.
    Singleton - только одна запись.
    """

    fieldsets = (
        (
            _("Hero секция"),
            {
                "fields": ("hero_title", "hero_subtitle", "hero_image"),
            },
        ),
        (
            _("О компании"),
            {
                "fields": ("about_title", "about_text", "about_image"),
                "classes": ("wide",),
            },
        ),
        (
            _("Преимущества"),
            {
                "fields": ("advantages",),
                "description": _(
                    'Формат: [{"title": "Преимущество", "description": "Описание"}]'
                ),
                "classes": ("wide",),
            },
        ),
        (
            _("Статистика"),
            {
                "fields": ("patients_count", "doctors_count", "experience_years"),
            },
        ),
        (
            _("SEO"),
            {
                "fields": ("meta_title", "meta_description"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        """Запрещаем добавление новой записи, если одна уже существует."""
        return not HomePageContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление единственной записи."""
        return False


@admin.register(AboutPageContent)
class AboutPageContentAdmin(admin.ModelAdmin):
    """
    Админка для контента страницы "О компании".
    Singleton - только одна запись.
    """

    fieldsets = (
        (
            None,
            {
                "fields": ("title",),
            },
        ),
        (
            _("История"),
            {
                "fields": ("history_title", "history_text", "history_image"),
                "classes": ("wide",),
            },
        ),
        (
            _("Миссия"),
            {
                "fields": ("mission_title", "mission_text"),
            },
        ),
        (
            _("Ценности"),
            {
                "fields": ("values",),
                "description": _(
                    'Формат: [{"title": "Ценность", "description": "Описание"}]'
                ),
                "classes": ("wide",),
            },
        ),
        (
            _("Оборудование"),
            {
                "fields": ("equipment_title", "equipment_description"),
            },
        ),
        (
            _("SEO"),
            {
                "fields": ("meta_title", "meta_description"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        """Запрещаем добавление новой записи, если одна уже существует."""
        return not AboutPageContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление единственной записи."""
        return False
