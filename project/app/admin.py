from django.contrib import admin
from .models import Destination, Package, Customer, Booking, Review

# Register your models here
admin.site.register(Destination)
admin.site.register(Package)
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(Review)
