from django.contrib import admin
from .models import (
    Market, Category, Product, Order, OrderItem, 
    SellerAnalytics, SellerWallet, WalletTransaction,
    Shop, NavigationRoute, GeofenceZone, UserLocation, NavigationSession
)

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'latitude', 'longitude', 'created_at']
    list_filter = ['outdoor_navigation_enabled', 'indoor_map_enabled', 'country', 'state']
    search_fields = ['name', 'city', 'address', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['parent']
    search_fields = ['name', 'description']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'category', 'price', 'stock_quantity', 'is_available']
    list_filter = ['is_available', 'category', 'created_at']
    search_fields = ['name', 'description', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'seller', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__username', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_at_time_of_order']
    search_fields = ['order__id', 'product__name']

@admin.register(SellerAnalytics)
class SellerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['seller', 'total_orders', 'completed_orders', 'updated_at']
    search_fields = ['seller__username']
    readonly_fields = ['updated_at']

@admin.register(SellerWallet)
class SellerWalletAdmin(admin.ModelAdmin):
    list_display = ['seller', 'balance', 'updated_at']
    search_fields = ['seller__username']
    readonly_fields = ['updated_at']

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__seller__username', 'description']
    readonly_fields = ['created_at']

# Navigation System Admin
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'market', 'latitude', 'longitude', 'is_active', 'is_verified']
    list_filter = ['is_active', 'is_verified', 'market']
    search_fields = ['name', 'description', 'seller__username', 'market__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(NavigationRoute)
class NavigationRouteAdmin(admin.ModelAdmin):
    list_display = ['start_shop', 'end_shop', 'distance_meters', 'estimated_walk_time_seconds']
    search_fields = ['start_shop__name', 'end_shop__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(GeofenceZone)
class GeofenceZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'market', 'zone_type']
    list_filter = ['zone_type', 'market']
    search_fields = ['name', 'market__name']

@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'market', 'latitude', 'longitude', 'is_indoor', 'timestamp']
    list_filter = ['is_indoor', 'market', 'timestamp']
    search_fields = ['user__username', 'market__name']
    readonly_fields = ['timestamp']

@admin.register(NavigationSession)
class NavigationSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'destination_shop', 'status', 'started_at']
    list_filter = ['status', 'started_at']
    search_fields = ['user__username', 'destination_shop__name']
    readonly_fields = ['started_at', 'completed_at']
