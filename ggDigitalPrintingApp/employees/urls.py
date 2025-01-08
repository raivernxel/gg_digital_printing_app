from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
     path('', views.insert_employees, name='employees'),
     path('employee-log', views.employee_log, name='employee-log'),
]
