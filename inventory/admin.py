from django.contrib import admin
from .models import Item, Order, OrderLine

# Register your models here.
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderLine)
