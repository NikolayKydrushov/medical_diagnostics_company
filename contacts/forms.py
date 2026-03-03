from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FeedbackMessage


class ContactForm(forms.ModelForm):
    """
    Форма обратной связи с валидацией.
    """

    class Meta:
        model = FeedbackMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя',
                'autocomplete': 'name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.ru',
                'autocomplete': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67',
                'autocomplete': 'tel'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше сообщение...',
                'rows': 5
            }),
        }
        labels = {
            'name': _('Ваше имя'),
            'email': _('Email'),
            'phone': _('Телефон'),
            'message': _('Сообщение'),
        }

    def clean_phone(self):
        """
        Валидация номера телефона.
        """
        phone = self.cleaned_data.get('phone')
        if phone:
            # Удаляем все символы кроме цифр и плюса
            cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')

            # Проверяем длину (минимум 10 цифр)
            digits = ''.join(c for c in cleaned_phone if c.isdigit())
            if len(digits) < 10:
                raise forms.ValidationError(
                    'Номер телефона должен содержать минимум 10 цифр'
                )

            return cleaned_phone
        return phone

    def clean_email(self):
        """
        Проверяем, что email указан (для обратной связи).
        """
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email обязателен для обратной связи')
        return email
