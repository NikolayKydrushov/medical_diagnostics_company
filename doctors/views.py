from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from .models import Doctor

# Create your views here.

class DoctorListView(ListView):
    """
    Представление для списка всех врачей.
    Поддерживает поиск и фильтрацию по специализации.
    """
    model = Doctor
    template_name = 'doctors/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 6

    def get_queryset(self):
        """
        Фильтруем врачей: только активные, с сортировкой.
        Добавляем поиск по имени и специализации.
        """
        queryset = Doctor.objects.filter(
            is_active=True
        ).select_related().order_by('order', 'name')

        # Поиск по GET-параметру 'q'
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(specialty__icontains=query) |
                Q(bio__icontains=query)
            )

        # Фильтр по специализации
        specialty = self.request.GET.get('specialty')
        if specialty:
            queryset = queryset.filter(specialty__icontains=specialty)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем уникальные специализации для фильтра
        specialties = Doctor.objects.filter(
            is_active=True
        ).values_list('specialty', flat=True).distinct()

        context['specialties'] = sorted(set(specialties))
        context['search_query'] = self.request.GET.get('q', '')
        context['current_specialty'] = self.request.GET.get('specialty', '')

        return context


class DoctorDetailView(DetailView):
    """
    Представление для детальной страницы врача.
    """
    model = Doctor
    template_name = 'doctors/doctor_detail.html'
    context_object_name = 'doctor'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """Показываем только активных врачей."""
        return Doctor.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Услуги, которые оказывает врач
        context['services'] = self.object.services.filter(is_active=True)

        # Записи к этому врачу (только для админа, но пока заглушка)
        context['appointments_count'] = self.object.appointments.count()

        return context
