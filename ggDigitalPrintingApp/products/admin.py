from django.contrib import admin
from .models import Products, ProductPrices, ProductInformation, ProductTypes

# Register your models here.
admin.site.register(Products)
admin.site.register(ProductPrices)
admin.site.register(ProductInformation)
admin.site.register(ProductTypes)