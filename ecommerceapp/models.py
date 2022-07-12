from django.db import models

# Create your models here.


class Product(models.Model):
    product_title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now='true')
    product_image = models.ImageField(null='true', blank='true')

    def __str__(self):
        return self.product_title


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique='true')
    phone_number = models.CharField(max_length=11)
    birthday = models.DateField(null='true')
    joined = models.DateField(auto_now_add='true')


class Order(models.Model):
    ORDER_STATUS_PENDING = 'P'
    ORDER_STATUS_FAILED = 'F'
    ORDER_STATUS_COMPLETE = 'C'

    ORDER_STATUS_CHOICES = [
        (ORDER_STATUS_PENDING, 'pending'),
        (ORDER_STATUS_FAILED, 'failed'),
        (ORDER_STATUS_COMPLETE, 'complete'),
    ]
    Time_of_order = models.DateTimeField(auto_now_add='true')
    payment_status = models.CharField(max_length=1, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_PENDING)
