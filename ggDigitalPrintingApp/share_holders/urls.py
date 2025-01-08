from django.urls import path
from . import views

app_name = 'shareholders'

urlpatterns = [
    path('user-income/', views.user_income, name='user-income'),
    path('revenue/', views.revenue, name='revenue'),
    path('cash-out/', views.cash_out, name='cash-out'),
    path('add-tran-hist/', views.add_tran_hist, name='add-tran-hist')
]
