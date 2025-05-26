from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import TransactionRecord, Wallet

admin.site.register(TransactionRecord)
admin.site.register(Wallet)
