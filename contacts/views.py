from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .forms import ContactForm
from .models import ContactInfo, FeedbackMessage

# Create your views here.

class ContactView(FormView):
    """
    Представление для страницы контактов с формой обратной связи.
    """
    template_name = 'contacts/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contacts:thank_you')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем контактную информацию
        try:
            context['contact_info'] = ContactInfo.objects.first()
        except ContactInfo.DoesNotExist:
            context['contact_info'] = None

        return context

    def form_valid(self, form):
        """
        Сохраняем сообщение в базу данных и отправляем уведомление.
        """
        # Сохраняем сообщение
        message = form.save()

        # Добавляем сообщение об успехе
        messages.success(
            self.request,
            'Спасибо за обращение! Мы свяжемся с вами в ближайшее время.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Если форма невалидна, показываем ошибки.
        """
        messages.error(
            self.request,
            'Пожалуйста, исправьте ошибки в форме.'
        )
        return super().form_invalid(form)


class ContactThankYouView(TemplateView):
    """
    Страница благодарности после отправки формы.
    """
    template_name = 'contacts/thank_you.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_info'] = ContactInfo.objects.first()
        return context

