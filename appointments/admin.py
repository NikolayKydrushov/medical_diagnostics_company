from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Appointment, DiagnosticResult

# Register your models here.

class DiagnosticResultInline(admin.StackedInline):
    """Инлайн для результатов диагностики."""
    model = DiagnosticResult
    verbose_name = _("Результат диагностики")
    verbose_name_plural = _("Результаты диагностики")
    extra = 0
    fields = ('result_file', 'doctor_comment', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Админка для управления записями на прием.
    """
    list_display = (
        'id', 'user_link', 'service', 'doctor',
        'datetime_display', 'status_colored', 'created_at'
    )
    list_filter = ('status', 'date', 'service', 'doctor')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_per_page = 30
    date_hierarchy = 'date'

    fieldsets = (
        (None, {
            'fields': ('user', 'service', 'doctor')
        }),
        (_('Время приема'), {
            'fields': ('date', 'time'),
            'classes': ('wide',),
        }),
        (_('Статус и комментарии'), {
            'fields': ('status', 'patient_comment', 'admin_comment'),
            'classes': ('wide',),
        }),
        (_('Служебная информация'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
    inlines = [DiagnosticResultInline]

    def user_link(self, obj):
        """Ссылка на пользователя в админке."""
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)

    user_link.short_description = _('Пациент')
    user_link.admin_order_field = 'user'

    def datetime_display(self, obj):
        """Форматированное отображение даты и времени."""
        return f"{obj.date.strftime('%d.%m.%Y')} {obj.time.strftime('%H:%M')}"

    datetime_display.short_description = _('Дата и время')
    datetime_display.admin_order_field = ('date', 'time')

    def status_colored(self, obj):
        """Цветной статус для наглядности."""
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'completed': 'blue',
            'cancelled': 'red',
            'no_show': 'gray',
        }
        status_names = dict(Appointment.Status.choices)
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            status_names.get(obj.status, obj.status)
        )

    status_colored.short_description = _('Статус')
    status_colored.admin_order_field = 'status'

    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']

    def mark_as_confirmed(self, request, queryset):
        """Подтвердить выбранные записи."""
        queryset.update(status=Appointment.Status.CONFIRMED)
        self.message_user(request, f"Подтверждено {queryset.count()} записей")

    mark_as_confirmed.short_description = _("Подтвердить выбранные записи")

    def mark_as_completed(self, request, queryset):
        """Отметить как завершенные."""
        queryset.update(status=Appointment.Status.COMPLETED)
        self.message_user(request, f"{queryset.count()} записей отмечены как завершенные")

    mark_as_completed.short_description = _("Отметить как завершенные")

    def mark_as_cancelled(self, request, queryset):
        """Отменить выбранные записи."""
        queryset.update(status=Appointment.Status.CANCELLED)
        self.message_user(request, f"Отменено {queryset.count()} записей")

    mark_as_cancelled.short_description = _("Отменить выбранные записи")


@admin.register(DiagnosticResult)
class DiagnosticResultAdmin(admin.ModelAdmin):
    """
    Админка для результатов диагностики.
    """
    list_display = ('id', 'appointment_link', 'file_link', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('appointment__user__username', 'doctor_comment')
    readonly_fields = ('uploaded_at',)

    fieldsets = (
        (None, {
            'fields': ('appointment', 'result_file')
        }),
        (_('Комментарий'), {
            'fields': ('doctor_comment',),
            'classes': ('wide',),
        }),
        (_('Служебная информация'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',),
        }),
    )

    def appointment_link(self, obj):
        """Ссылка на запись."""
        url = reverse('admin:appointments_appointment_change', args=[obj.appointment.pk])
        return format_html('<a href="{}">Запись #{}</a>', url, obj.appointment.pk)

    appointment_link.short_description = _('Запись')

    def file_link(self, obj):
        """Ссылка на файл с результатами."""
        if obj.result_file:
            return format_html(
                '<a href="{}" target="_blank">📄 Скачать файл</a>',
                obj.result_file.url
            )
        return format_html('<span style="color: gray;">Нет файла</span>')

    file_link.short_description = _('Файл')
