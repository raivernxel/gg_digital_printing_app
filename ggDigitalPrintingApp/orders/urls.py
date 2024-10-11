from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.orders),
    path('add-order/', views.add_orders, name='add-order'),
    path('trello-update/', views.trello_update, name='add-order')
]
