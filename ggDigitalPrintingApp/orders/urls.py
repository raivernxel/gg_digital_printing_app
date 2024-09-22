from django.urls import path
from . import views

urlpatterns = [
    path('insert-products/', views.insert_products),
]