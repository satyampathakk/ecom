from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Items)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(Wishlist)
