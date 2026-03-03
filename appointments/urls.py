from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    # Личный кабинет
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    # Запись на прием
    path("create/", views.AppointmentCreateView.as_view(), name="appointment_create"),
    path(
        "create/<slug:service_slug>/",
        views.AppointmentCreateView.as_view(),
        name="appointment_create_with_service",
    ),
    # История записей
    path(
        "history/", views.AppointmentHistoryView.as_view(), name="appointment_history"
    ),
    # Детали записи
    path("<int:pk>/", views.AppointmentDetailView.as_view(), name="appointment_detail"),
    # Отмена записи
    path(
        "<int:pk>/cancel/",
        views.AppointmentCancelView.as_view(),
        name="appointment_cancel",
    ),
    # Просмотр результатов диагностики
    path("result/<int:pk>/", views.ResultDetailView.as_view(), name="result_detail"),
]
