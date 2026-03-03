from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Список всех услуг
    path('', views.ServiceListView.as_view(), name='service_list'),

    # Детальная страница услуги (по slug)
    path('<slug:slug>/', views.ServiceDetailView.as_view(), name='service_detail'),
]
