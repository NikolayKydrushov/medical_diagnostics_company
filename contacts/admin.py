from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ContactInfo, FeedbackMessage

# Register your models here.


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """
    Админка для контактной информации.
    Настроена как Singleton - можно редактировать только одну запись.
    """

    list_display = ("address", "phone", "email", "work_hours", "updated_at")

    fieldsets = (
        (None, {"fields": ("address", "phone", "email", "work_hours")}),
        (
            _("Карта"),
            {
                "fields": ("map_url",),
                "classes": ("wide",),
            },
        ),
        (
            _("Социальные сети"),
            {
                "fields": ("vk_url", "telegram_url"),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        """Запрещаем добавление новых записей, если одна уже существует."""
        return not ContactInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление единственной записи."""
        return False


@admin.register(FeedbackMessage)
class FeedbackMessageAdmin(admin.ModelAdmin):
    """
    Админка для сообщений обратной связи.
    """

    list_display = (
        "name",
        "email",
        "phone",
        "short_message",
        "created_at",
        "is_processed",
        "process_button",
    )
    list_filter = ("is_processed", "created_at")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("name", "email", "phone", "message", "created_at")
    list_per_page = 30
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("name", "email", "phone", "created_at")}),
        (
            _("Сообщение"),
            {
                "fields": ("message",),
                "classes": ("wide",),
            },
        ),
        (
            _("Обработка"),
            {
                "fields": ("is_processed", "processed_at", "processed_by"),
                "classes": ("wide",),
            },
        ),
    )

    def short_message(self, obj):
        """Сокращенная версия сообщения."""
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message

    short_message.short_description = _("Сообщение")

    def process_button(self, obj):
        """Кнопка для быстрой отметки об обработке."""
        if not obj.is_processed:
            url = reverse("admin:contacts_feedbackmessage_change", args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background-color: #28a745; '
                'color: white; padding: 3px 10px; border-radius: 3px; '
                'text-decoration: none;">Отметить обработанным</a>',
                url,
            )
        return format_html('<span style="color: green;">✓ Обработано</span>')

    process_button.short_description = _("Действие")

    actions = ["mark_as_processed", "mark_as_unprocessed"]

    def mark_as_processed(self, request, queryset):
        """Отметить сообщения как обработанные."""
        from django.utils import timezone

        queryset.update(
            is_processed=True, processed_at=timezone.now(), processed_by=request.user
        )
        self.message_user(
            request, f"Отмечено {queryset.count()} сообщений как обработанные"
        )

    mark_as_processed.short_description = _("Отметить как обработанные")

    def mark_as_unprocessed(self, request, queryset):
        """Снять отметку об обработке."""
        queryset.update(is_processed=False, processed_at=None, processed_by=None)
        self.message_user(
            request, f"У {queryset.count()} сообщений снята отметка об обработке"
        )

    mark_as_unprocessed.short_description = _("Снять отметку об обработке")
