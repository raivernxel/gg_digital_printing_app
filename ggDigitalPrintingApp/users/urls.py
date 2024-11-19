# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name='login'),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/login.html"), name="logout"),
]
