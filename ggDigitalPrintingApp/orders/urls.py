from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.orders),
    path('add-order/', views.add_orders, name='add_order'),
    path('trello-update/', views.trello_update, name='trello-update'),
    path('ajax/load-var-names/', views.load_var_names, name='load-var-names'),
    path('ajax/get-prod-price/', views.get_prod_price, name='get-prod-price'),
]
