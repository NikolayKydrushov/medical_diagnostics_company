from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # Регистрация
    path("register/", views.RegisterView.as_view(), name="register"),
    path("register/done/", views.RegisterDoneView.as_view(), name="register_done"),
    # Вход и выход
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    # Профиль пользователя
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
]
