from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Appointment, DiagnosticResult
from services.models import Service
from doctors.models import Doctor
from .forms import AppointmentForm, AppointmentCancelForm

# Create your views here.

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Личный кабинет пользователя.
    """
    template_name = 'appointments/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Предстоящие записи (ожидающие и подтвержденные)
        context['upcoming_appointments'] = Appointment.objects.filter(
            user=user,
            status__in=['pending', 'confirmed']
        ).select_related('service', 'doctor').order_by('date', 'time')

        # Последние 5 завершенных записей
        context['recent_completed'] = Appointment.objects.filter(
            user=user,
            status='completed'
        ).select_related('service', 'doctor').order_by('-date', '-time')[:5]

        # Статистика
        context['total_count'] = Appointment.objects.filter(user=user).count()
        context['completed_count'] = Appointment.objects.filter(
            user=user, status='completed'
        ).count()
        context['cancelled_count'] = Appointment.objects.filter(
            user=user, status='cancelled'
        ).count()

        return context


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """
    Создание новой записи на прием.
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointments:dashboard')

    def get_initial(self):
        """Предзаполняем форму, если передан slug услуги."""
        initial = super().get_initial()
        service_slug = self.kwargs.get('service_slug')

        if service_slug:
            try:
                service = Service.objects.get(slug=service_slug, is_active=True)
                initial['service'] = service

                # Предлагаем врачей для этой услуги
                doctors = Doctor.objects.filter(
                    services=service,
                    is_active=True
                )
                if doctors.exists():
                    initial['doctor'] = doctors.first()

            except Service.DoesNotExist:
                pass

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Если выбрана услуга, показываем доступных врачей
        if 'service' in self.request.GET:
            try:
                service = Service.objects.get(id=self.request.GET.get('service'))
                context['available_doctors'] = Doctor.objects.filter(
                    services=service,
                    is_active=True
                )
            except (Service.DoesNotExist, ValueError):
                pass

        return context

    def form_valid(self, form):
        """При успешной валидации устанавливаем пользователя."""
        form.instance.user = self.request.user

        # Проверяем, нет ли уже записи на это время
        existing = Appointment.objects.filter(
            doctor=form.instance.doctor,
            date=form.instance.date,
            time=form.instance.time,
            status__in=['pending', 'confirmed']
        ).exists()

        if existing:
            messages.error(
                self.request,
                'Это время уже занято. Пожалуйста, выберите другое время.'
            )
            return self.form_invalid(form)

        messages.success(
            self.request,
            'Запись успешно создана! Ожидайте подтверждения администратора.'
        )

        return super().form_valid(form)


class AppointmentHistoryView(LoginRequiredMixin, ListView):
    """
    История записей пользователя.
    """
    model = Appointment
    template_name = 'appointments/appointment_history.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        """Возвращает все записи пользователя с сортировкой."""
        return Appointment.objects.filter(
            user=self.request.user
        ).select_related(
            'service', 'doctor'
        ).order_by('-date', '-time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Фильтр по статусу, если передан
        status_filter = self.request.GET.get('status')
        if status_filter:
            context['appointments'] = context['appointments'].filter(status=status_filter)
            context['current_status'] = status_filter

        context['status_choices'] = Appointment.Status.choices

        return context


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """
    Детальная информация о записи.
    """
    model = Appointment
    template_name = 'appointments/appointment_detail.html'
    context_object_name = 'appointment'

    def get_queryset(self):
        """Только записи текущего пользователя."""
        return Appointment.objects.filter(
            user=self.request.user
        ).select_related('service', 'doctor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Проверяем, можно ли отменить запись
        context['can_cancel'] = self.object.can_cancel

        # Получаем результаты диагностики, если есть
        try:
            context['diagnostic_result'] = self.object.diagnostic_result
        except DiagnosticResult.DoesNotExist:
            context['diagnostic_result'] = None

        return context


class AppointmentCancelView(LoginRequiredMixin, UpdateView):
    """
    Отмена записи.
    """
    model = Appointment
    form_class = AppointmentCancelForm
    template_name = 'appointments/appointment_cancel.html'
    success_url = reverse_lazy('appointments:dashboard')

    def get_queryset(self):
        """Только записи, которые можно отменить."""
        return Appointment.objects.filter(
            user=self.request.user,
            status__in=['pending', 'confirmed']
        )

    def form_valid(self, form):
        """При отмене меняем статус."""
        form.instance.status = Appointment.Status.CANCELLED
        messages.success(self.request, 'Запись успешно отменена.')
        return super().form_valid(form)


class ResultDetailView(LoginRequiredMixin, DetailView):
    """
    Просмотр результатов диагностики.
    """
    model = DiagnosticResult
    template_name = 'appointments/result_detail.html'
    context_object_name = 'result'

    def get_queryset(self):
        """Только результаты текущего пользователя."""
        return DiagnosticResult.objects.filter(
            appointment__user=self.request.user
        ).select_related('appointment', 'appointment__service')
