from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('insert-products/', views.insert_products),
    path('add-order/', views.add_orders, name='add-order')
]
