from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('add-expenses/', views.add_expenses, name='add-expenses'),
    path('monthly-fees/', views.monthly_fees, name='monthly-fees')
]
