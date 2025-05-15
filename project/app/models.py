from django.db import models
# Create your models here.
from django.contrib.auth.models import User




class Package(models.Model):
    title = models.CharField(max_length=200)
    duration_days = models.IntegerField()
    description = models.TextField()
    included = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='packages/')
    image2 = models.ImageField(upload_to='packages/',null=False,default='')
    image3 = models.ImageField(upload_to='packages/',null=False,default='')


    def __str__(self):
        return f"{self.title} "
    
class Vehicle(models.Model):
    name=models.CharField(max_length=200)
    price=models.IntegerField()
    package=models.ForeignKey(Package,on_delete=models.CASCADE)
    Description = models.TextField()
    image = models.ImageField(upload_to='vehicles/')


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.username


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    travel_package = models.ForeignKey(Package, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    number_of_people = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ])
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking by {self.customer.user.username} for {self.travel_package.title}"



class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    travel_package = models.ForeignKey(Package, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - {self.rating}⭐"
