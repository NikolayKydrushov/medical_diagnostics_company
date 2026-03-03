from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    # Страница контактов с формой обратной связи
    path('', views.ContactView.as_view(), name='contact'),

    # Страница "Спасибо" после отправки формы
    path('thank-you/', views.ContactThankYouView.as_view(), name='thank_you'),
]
