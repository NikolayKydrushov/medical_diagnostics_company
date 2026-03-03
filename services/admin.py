from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Service

# Register your models here.


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Админка для управления медицинскими услугами.
    """

    list_display = (
        "name",
        "price",
        "price_display",
        "duration",
        "preview_image",
        "order",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "short_description", "full_description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("order", "is_active", "price")
    list_per_page = 20

    fieldsets = (
        (None, {"fields": ("name", "slug", "is_active", "order")}),
        (
            _("Описание"),
            {
                "fields": ("short_description", "full_description"),
                "classes": ("wide",),
            },
        ),
        (
            _("Цена и длительность"),
            {
                "fields": ("price", "duration"),
                "description": _("Стоимость услуги и примерное время приема"),
            },
        ),
        (
            _("Медиа"),
            {
                "fields": ("image",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Служебная информация"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at", "preview_image")

    def price_display(self, obj):
        """Отформатированное отображение цены."""
        return f"{obj.price:.2f} ₽"

    price_display.short_description = _("Цена")
    price_display.admin_order_field = "price"

    def preview_image(self, obj):
        """Предпросмотр изображения услуги."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url,
            )
        return "Нет фото"  # Просто возвращаем строку без format_html
        preview_image.short_description = _("Превью")

        # Действия
        actions = ['activate_services', 'deactivate_services']

    def activate_services(self, request, queryset):
        """Активировать выбранные услуги."""
        queryset.update(is_active=True)
        self.message_user(request, f"Активировано {queryset.count()} услуг")

    activate_services.short_description = _("Активировать выбранные услуги")

    def deactivate_services(self, request, queryset):
        """Деактивировать выбранные услуги."""
        queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {queryset.count()} услуг")

    deactivate_services.short_description = _("Деактивировать выбранные услуги")

    def price_display(self, obj):
        """Отформатированное отображение цены."""
        return f"{obj.price:.2f} ₽"

    price_display.short_description = _("Цена (формат)")
    price_display.admin_order_field = "price"
