from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("qeydiyyat/", views.RegisterView.as_view(), name="register"),
    path(
        "giris/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("cixis/", auth_views.LogoutView.as_view(), name="logout"),
    path("hesabim/", views.DashboardView.as_view(), name="dashboard"),
    path("profil/", views.ProfileView.as_view(), name="profile"),
]
