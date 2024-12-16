from django.contrib import admin
from .models import *

class NonDeletedAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.all_objects


@admin.register(Role)
class RoleAdmin(NonDeletedAdmin):
    list_display = ('role', 'is_deleted')
    search_fields = ('role',)
    list_filter = ('is_deleted',)


@admin.register(User)
class UserAdmin(NonDeletedAdmin):
    list_display = ('login', 'role', 'phone', 'is_deleted')
    search_fields = ('login', 'phone')
    list_filter = ('role', 'is_deleted')
    remove_fieldsets = (
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )


@admin.register(Log)
class LogAdmin(NonDeletedAdmin):
    list_display = ('user', 'action', 'description', 'is_deleted')
    search_fields = ('action', 'description')
    list_filter = ('is_deleted',)


@admin.register(Provider)
class ProviderAdmin(NonDeletedAdmin):
    list_display = ('user', 'rating', 'product_type', 'is_deleted')
    search_fields = ('product_type', 'user__login')
    list_filter = ('is_deleted',)


@admin.register(Product)
class ProductAdmin(NonDeletedAdmin):
    list_display = ('title', 'provider', 'weight', 'price', 'is_deleted')
    search_fields = ('title', 'provider__user__login')
    list_filter = ('is_deleted',)


@admin.register(Stock)
class StockAdmin(NonDeletedAdmin):
    list_display = ('product', 'line', 'cell', 'quantity', 'is_deleted')
    search_fields = ('product__title',)
    list_filter = ('is_deleted',)


@admin.register(Order)
class OrderAdmin(NonDeletedAdmin):
    list_display = ('user', 'cost', 'address', 'status', 'tracking_number', 'departure_date', 'delivery_date', 'is_deleted')
    search_fields = ('user__login', 'tracking_number', 'address')
    list_filter = ('status', 'is_deleted')


@admin.register(ProductOrder)
class ProductOrderAdmin(NonDeletedAdmin):
    list_display = ('product', 'order', 'quantity', 'is_deleted')
    search_fields = ('product__title', 'order__user__login')
    list_filter = ('is_deleted',)


@admin.register(DeliveryTime)
class DeliveryTimeAdmin(NonDeletedAdmin):
    list_display = ('provider', 'product', 'delivery_time', 'quantity', 'is_deleted')
    search_fields = ('provider__user__login', 'product__title')
    list_filter = ('is_deleted',)