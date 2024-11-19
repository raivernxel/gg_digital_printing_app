from django.contrib import admin
from .models import ShareHolders, TransactionHistory

# Register your models here.
admin.site.register(ShareHolders)
admin.site.register(TransactionHistory)
