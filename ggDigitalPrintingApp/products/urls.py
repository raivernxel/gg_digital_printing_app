from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('prices/', views.product_prices, name='prices'),
    path('product_information/', views.insert_product_information)
]