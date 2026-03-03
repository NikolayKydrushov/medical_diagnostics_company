from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from services.models import Service
from doctors.models import Doctor
from contacts.models import ContactInfo
from .models import HomePageContent, AboutPageContent

# Create your views here.

class HomePageView(TemplateView):
    """
    Представление для главной страницы.
    Собирает данные из разных приложений.
    """
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем контент главной страницы (если есть)
        try:
            context['home_content'] = HomePageContent.objects.first()
        except HomePageContent.DoesNotExist:
            context['home_content'] = None

        # Последние 6 активных услуг для отображения на главной
        context['services'] = Service.objects.filter(
            is_active=True
        ).order_by('order', 'name')[:6]

        # Несколько врачей для отображения
        context['doctors'] = Doctor.objects.filter(
            is_active=True
        ).order_by('order', 'name')[:3]

        # Контактная информация для подвала
        context['contact_info'] = ContactInfo.objects.first()

        return context


class AboutPageView(TemplateView):
    """
    Представление для страницы "О компании".
    """
    template_name = 'pages/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем контент страницы "О компании"
        try:
            context['about_content'] = AboutPageContent.objects.first()
        except AboutPageContent.DoesNotExist:
            context['about_content'] = None

        # Все активные врачи для отображения
        context['doctors'] = Doctor.objects.filter(
            is_active=True
        ).order_by('order', 'name')

        return context
