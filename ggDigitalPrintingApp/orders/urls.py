from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.orders),
    path('add-order/', views.add_orders, name='add-order'),
    path('trello-update/', views.trello_update, name='trello-update'),
    path('ajax/load_var_names/', views.load_var_names, name='load_var_names'),
    path('ajax/get_prod_price/', views.get_prod_price, name='get_prod_price'),
]
