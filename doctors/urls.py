from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    # Список всех врачей
    path("", views.DoctorListView.as_view(), name="doctor_list"),
    # Детальная страница врача (по slug)
    path("<slug:slug>/", views.DoctorDetailView.as_view(), name="doctor_detail"),
]
