from django.contrib import admin
from .models import Logistics, SellingPlatform, OrderStatus, OrderFulfillment, OrderInformation, OrderList, OrderMaintenance

# Register your models here.
admin.site.register(Logistics)
admin.site.register(SellingPlatform)
admin.site.register(OrderStatus)
admin.site.register(OrderFulfillment)
admin.site.register(OrderInformation)
admin.site.register(OrderList)
admin.site.register(OrderMaintenance)
