"""
URL configuration for ggDigitalPrintingApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403, handler404, handler500
from . import views

handler403 = 'ggDigitalPrintingApp.views.custom_403'
handler404 = 'ggDigitalPrintingApp.views.custom_404'
handler500 = 'ggDigitalPrintingApp.views.custom_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='home'),
    path('orders/', include('orders.urls')),
    path('products/', include('products.urls')),
    path('expenses/', include('expenses.urls')),
    path('shareholders/', include('share_holders.urls')),
    path('users/', include('users.urls')),
    path('employees/', include('employees.urls')),
    path("__reload__/", include("django_browser_reload.urls")),

    path('access-denied/', views.access_denied, name='access-denied'),
]
