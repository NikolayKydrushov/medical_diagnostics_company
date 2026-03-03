from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Главная страница
    path('', views.HomePageView.as_view(), name='home'),

    # Страница "О компании"
    path('about/', views.AboutPageView.as_view(), name='about'),
]
