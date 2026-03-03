from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Doctor

# Register your models here.

class DoctorServiceInline(admin.TabularInline):
    """Инлайн для отображения услуг врача."""
    model = Doctor.services.through
    verbose_name = _("Услуга")
    verbose_name_plural = _("Услуги")
    extra = 1
    autocomplete_fields = ('service',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """
    Админка для управления врачами.
    """
    list_display = (
        'name', 'specialty', 'experience_years',
        'preview_photo', 'order', 'is_active'
    )
    list_filter = ('specialty', 'is_active', 'services')
    search_fields = ('name', 'specialty', 'bio')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active', 'experience_years')
    list_per_page = 20
    filter_horizontal = ('services',)

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'specialty', 'is_active', 'order')
        }),
        (_('Личная информация'), {
            'fields': ('photo', 'bio', 'experience_years', 'email', 'phone'),
            'classes': ('wide',),
        }),
        (_('Услуги'), {
            'fields': ('services',),
            'description': _('Какие услуги оказывает данный врач'),
            'classes': ('wide',),
        }),
        (_('Служебная информация'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'preview_photo')

    def preview_photo(self, obj):
        """Предпросмотр фото врача."""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%;" />',
                obj.photo.url
            )
        return format_html('<span style="color: gray;">Нет фото</span>')

    preview_photo.short_description = _('Фото')

    def get_services_count(self, obj):
        """Количество услуг врача."""
        return obj.services.count()

    get_services_count.short_description = _('Услуг')
    get_services_count.admin_order_field = 'services__count'

    actions = ['activate_doctors', 'deactivate_doctors']

    def activate_doctors(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Активировано {queryset.count()} врачей")

    activate_doctors.short_description = _("Активировать выбранных врачей")

    def deactivate_doctors(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {queryset.count()} врачей")

    deactivate_doctors.short_description = _("Деактивировать выбранных врачей")
