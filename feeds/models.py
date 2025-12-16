from django.db import models
from django.contrib.auth.models import User

class Zone(models.Model):
    name = models.CharField(max_length=100)
    target_weight = models.IntegerField(default=300)  # kg needed for discount
    discount_percentage = models.IntegerField(default=15)
    
    def __str__(self):
        return self.name
    
    def current_weight(self):
        """Calculate total weight of pending orders in this zone"""
        return sum([order.total_weight() for order in self.orders.filter(status='PENDING')])
    
    def discount_active(self):
        """Check if zone has reached target weight"""
        return self.current_weight() >= self.target_weight


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"


class Product(models.Model):
    FEED_TYPES = [
        ('DAIRY', 'Dairy Feeds'),
        ('POULTRY', 'Poultry Feeds'),
        ('PIG', 'Pig Feeds'),
    ]
    
    name = models.CharField(max_length=200)
    feed_type = models.CharField(max_length=20, choices=FEED_TYPES)
    weight = models.IntegerField(help_text="Weight in KG")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    stock = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} ({self.weight}kg)"
    
    def get_price_for_zone(self, zone):
        """Calculate price with zone discount if applicable"""
        if zone and zone.discount_active():
            discount = (zone.discount_percentage / 100) * self.base_price
            return self.base_price - discount
        return self.base_price


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid'),
        ('DISPATCHED', 'Dispatched'),
        ('DELIVERED', 'Delivered'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
    def total_weight(self):
        """Calculate total weight of all items in order"""
        return sum([item.product.weight * item.quantity for item in self.items.all()])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"