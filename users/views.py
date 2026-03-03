from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import User
from .forms import UserRegistrationForm, UserProfileForm, UserLoginForm
from appointments.models import Appointment

# Create your views here.

class RegisterView(SuccessMessageMixin, CreateView):
    """
    Регистрация нового пользователя.
    Доступно всем (в том числе неавторизованным).
    """
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Регистрация прошла успешно! Теперь вы можете войти.'

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляем авторизованных пользователей на главную."""
        if request.user.is_authenticated:
            return redirect('pages:home')
        return super().dispatch(request, *args, **kwargs)


class RegisterDoneView(TemplateView):
    """
    Страница после успешной регистрации.
    Доступно всем.
    """
    template_name = 'users/register_done.html'

    def dispatch(self, request, *args, **kwargs):
        """Если пользователь уже авторизован, перенаправляем на главную."""
        if request.user.is_authenticated:
            return redirect('pages:home')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """
    Авторизация пользователя.
    Доступно всем.
    """
    template_name = 'users/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = False

    def get_success_url(self):
        """После успешного входа перенаправляем в личный кабинет."""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('appointments:dashboard')

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляем авторизованных пользователей на главную."""
        if request.user.is_authenticated:
            return redirect('pages:home')
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        """При неверных данных показываем сообщение."""
        messages.error(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    Выход пользователя.
    """
    next_page = reverse_lazy('pages:home')
    http_method_names = ['get', 'post']  # Разрешаем GET и POST

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        """
        Переопределяем dispatch для добавления сообщения и правильного редиректа.
        """
        if request.user.is_authenticated:
            messages.success(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Обрабатываем GET запросы к logout."""
        from django.contrib.auth import logout
        logout(request)
        return redirect(self.next_page)


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Просмотр профиля пользователя.
    Только для авторизованных пользователей.
    """
    template_name = 'users/profile.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем последние записи пользователя
        context['recent_appointments'] = Appointment.objects.filter(
            user=self.request.user
        ).select_related('service', 'doctor').order_by('-date', '-time')[:5]

        # Статистика
        context['total_appointments'] = Appointment.objects.filter(
            user=self.request.user
        ).count()

        context['upcoming_appointments'] = Appointment.objects.filter(
            user=self.request.user,
            status__in=['pending', 'confirmed']
        ).count()

        return context


class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Редактирование профиля пользователя.
    Только для авторизованных пользователей.
    """
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_message = 'Профиль успешно обновлен!'
    login_url = 'users:login'

    def get_object(self, queryset=None):
        """Возвращаем текущего пользователя."""
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('users:profile')
