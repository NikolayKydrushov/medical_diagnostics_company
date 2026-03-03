from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомная админка для модели User.
    Расширяет стандартную UserAdmin дополнительными полями.
    """
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'phone', 'get_favorite_services_count', 'is_active', 'date_joined'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    # Добавляем новые поля в форму редактирования
    fieldsets = UserAdmin.fieldsets + (
        (_('Дополнительная информация'), {
            'fields': ('phone', 'birth_date', 'avatar', 'passport_data', 'insurance_policy')
        }),
        (_('Избранное'), {
            'fields': ('favorite_services',),
            'classes': ('wide',),
        }),
    )

    # Добавляем поля в форму создания
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Дополнительная информация'), {
            'fields': ('phone', 'birth_date', 'avatar', 'passport_data', 'insurance_policy')
        }),
    )

    # Настройка отображения связанных полей
    filter_horizontal = ('favorite_services', 'groups', 'user_permissions')

    def get_favorite_services_count(self, obj):
        """Возвращает количество избранных услуг."""
        return obj.favorite_services.count()

    get_favorite_services_count.short_description = _('Избранных услуг')
    get_favorite_services_count.admin_order_field = 'favorite_services__count'

    # Действия для массовой обработки
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        """Активировать выбранных пользователей."""
        queryset.update(is_active=True)
        self.message_user(request, f"Активировано {queryset.count()} пользователей")

    activate_users.short_description = _("Активировать выбранных пользователей")

    def deactivate_users(self, request, queryset):
        """Деактивировать выбранных пользователей."""
        queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {queryset.count()} пользователей")

    deactivate_users.short_description = _("Деактивировать выбранных пользователей")
