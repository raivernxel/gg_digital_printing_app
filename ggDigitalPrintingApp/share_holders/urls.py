from django.urls import path
from . import views

app_name = 'shareholders'

urlpatterns = [
    path('user-income/', views.user_income, name='user-income'),
]
