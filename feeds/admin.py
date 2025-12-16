from django.contrib import admin
from .models import Zone, UserProfile, Product, Order, OrderItem

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_weight', 'discount_percentage', 'current_weight', 'discount_active']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'zone']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'feed_type', 'weight', 'base_price', 'stock']
    list_filter = ['feed_type']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'zone', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'zone']
    inlines = [OrderItemInline]