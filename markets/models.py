from django.db import models
from users.models import User
import uuid

class Market(models.Model):
    """Model representing a physical market location"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    
    # GPS coordinates
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Market operating hours
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    # Market image
    image = models.ImageField(upload_to='market_images/', null=True, blank=True)
    
    # Market map data - could be an indoor map file or GeoJSON data
    map_data = models.JSONField(null=True, blank=True)
    map_image = models.FileField(upload_to='market_maps/', null=True, blank=True)
    
    # Geofencing and navigation support
    indoor_map_enabled = models.BooleanField(default=False)
    outdoor_navigation_enabled = models.BooleanField(default=True)
    
    # Boundary coordinates for geofencing (polygon points)
    boundary_coordinates = models.JSONField(null=True, blank=True, help_text="Polygon coordinates for market boundary")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    """Product categories for organization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    
    # For hierarchical categories
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Model for products sold by sellers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Inventory management
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    # Product images
    main_image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    
    # Additional product details
    weight = models.FloatField(null=True, blank=True)
    dimensions = models.CharField(max_length=100, null=True, blank=True)
    
    # Market association
    market = models.ForeignKey(Market, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Store location within market
    store_location_description = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    """Additional product images"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='product_images/')
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return f"Image for {self.product.name}"

class Order(models.Model):
    """Model for customer orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('ready', 'Ready for pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Order notes
    buyer_note = models.TextField(null=True, blank=True)
    seller_note = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.buyer.username}"

class OrderItem(models.Model):
    """Individual items within an order"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_order = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Keep product details in case product is deleted
    product_name = models.CharField(max_length=200)
    product_description = models.TextField()
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
    
    @property
    def subtotal(self):
        return self.quantity * self.price_at_time_of_order

class SellerAnalytics(models.Model):
    """Track seller analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics')
    store_views = models.PositiveIntegerField(default=0)
    product_views = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.seller.username}"

class SellerWallet(models.Model):
    """Seller's wallet for managing earnings"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Banking details for withdrawals
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Wallet for {self.seller.username}"

class WalletTransaction(models.Model):
    """Record of transactions for seller wallets"""
    TRANSACTION_TYPES = [
        ('order_payment', 'Order Payment'),
        ('withdrawal', 'Withdrawal'),
        ('refund', 'Refund'),
        ('adjustment', 'Manual Adjustment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(SellerWallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, null=True, blank=True)  # For linking to orders or external systems
    description = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.wallet.seller.username}"

class Shop(models.Model):
    """Model representing individual shops/stores within markets with geo-pin coordinates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='shops')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')
    
    # Shop details
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    shop_number = models.CharField(max_length=50, null=True, blank=True)
    floor_level = models.CharField(max_length=20, default='Ground Floor')
    
    # Geo-pin coordinates (precise shop location)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)  # For multi-floor markets
    
    # Indoor positioning (for indoor navigation)
    indoor_x = models.FloatField(null=True, blank=True, help_text="X coordinate on indoor map")
    indoor_y = models.FloatField(null=True, blank=True, help_text="Y coordinate on indoor map")
    indoor_floor = models.IntegerField(default=0, help_text="Floor number for multi-story markets")
    
    # Shop dimensions and entrance
    entrance_latitude = models.FloatField(null=True, blank=True)
    entrance_longitude = models.FloatField(null=True, blank=True)
    shop_width = models.FloatField(null=True, blank=True)
    shop_length = models.FloatField(null=True, blank=True)
    
    # Navigation metadata
    is_accessible = models.BooleanField(default=True)
    has_wheelchair_access = models.BooleanField(default=False)
    navigation_landmarks = models.JSONField(null=True, blank=True, help_text="Nearby landmarks for navigation")
    
    # Contact and operating hours
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    operating_hours = models.JSONField(null=True, blank=True)
    
    # Shop image
    image = models.ImageField(upload_to='shop_images/', null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['market', 'shop_number']
    
    def __str__(self):
        return f"{self.name} - {self.market.name}"


class NavigationRoute(models.Model):
    """Model for storing pre-calculated routes between shops and landmarks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='routes')
    
    # Route endpoints
    start_shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='routes_from', null=True, blank=True)
    end_shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='routes_to', null=True, blank=True)
    
    # Alternative: coordinate-based routing
    start_latitude = models.FloatField(null=True, blank=True)
    start_longitude = models.FloatField(null=True, blank=True)
    end_latitude = models.FloatField(null=True, blank=True)
    end_longitude = models.FloatField(null=True, blank=True)
    
    # Route data
    route_coordinates = models.JSONField(help_text="Array of coordinate points for the route")
    indoor_route_coordinates = models.JSONField(null=True, blank=True, help_text="Indoor navigation coordinates")
    
    # Route metadata
    distance_meters = models.FloatField()
    estimated_walk_time_seconds = models.IntegerField()
    is_indoor_route = models.BooleanField(default=False)
    is_accessible_route = models.BooleanField(default=True)
    
    # Route instructions
    turn_by_turn_instructions = models.JSONField(null=True, blank=True)
    landmarks_on_route = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.start_shop and self.end_shop:
            return f"Route: {self.start_shop.name} → {self.end_shop.name}"
        return f"Route in {self.market.name}"


class GeofenceZone(models.Model):
    """Model for defining geofenced areas within markets"""
    ZONE_TYPES = [
        ('entrance', 'Market Entrance'),
        ('parking', 'Parking Area'),
        ('food_court', 'Food Court'),
        ('restroom', 'Restroom'),
        ('section', 'Market Section'),
        ('emergency_exit', 'Emergency Exit'),
        ('loading_dock', 'Loading Dock'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='geofence_zones')
    
    name = models.CharField(max_length=100)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPES)
    description = models.TextField(null=True, blank=True)
    
    # Geofence boundary (polygon)
    boundary_coordinates = models.JSONField(help_text="Polygon coordinates defining the zone boundary")
    
    # Zone center point
    center_latitude = models.FloatField()
    center_longitude = models.FloatField()
    radius_meters = models.FloatField(default=10)
    
    # Zone properties
    is_indoor = models.BooleanField(default=False)
    floor_level = models.IntegerField(default=0)
    is_restricted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.zone_type}) - {self.market.name}"


class UserLocation(models.Model):
    """Model for tracking user locations for navigation assistance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='user_locations', null=True, blank=True)
    
    # Current location
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)
    accuracy_meters = models.FloatField(null=True, blank=True)
    
    # Indoor positioning
    indoor_x = models.FloatField(null=True, blank=True)
    indoor_y = models.FloatField(null=True, blank=True)
    floor_level = models.IntegerField(null=True, blank=True)
    
    # Location context
    is_indoor = models.BooleanField(default=False)
    current_shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    current_zone = models.ForeignKey(GeofenceZone, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    battery_level = models.IntegerField(null=True, blank=True)
    signal_strength = models.IntegerField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} location at {self.timestamp}"


class NavigationSession(models.Model):
    """Model for tracking active navigation sessions"""
    SESSION_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='navigation_sessions')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='navigation_sessions')
    
    # Destination
    destination_shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='navigation_sessions', null=True, blank=True)
    destination_latitude = models.FloatField(null=True, blank=True)
    destination_longitude = models.FloatField(null=True, blank=True)
    destination_name = models.CharField(max_length=200, null=True, blank=True)
    
    # Route information
    selected_route = models.ForeignKey(NavigationRoute, on_delete=models.SET_NULL, null=True, blank=True)
    route_coordinates = models.JSONField(null=True, blank=True)
    
    # Session tracking
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    start_latitude = models.FloatField()
    start_longitude = models.FloatField()
    
    # Progress tracking
    current_step_index = models.IntegerField(default=0)
    distance_remaining_meters = models.FloatField(null=True, blank=True)
    estimated_time_remaining_seconds = models.IntegerField(null=True, blank=True)
    
    # Session metadata
    navigation_mode = models.CharField(max_length=20, default='walking')  # walking, driving, accessibility
    use_indoor_navigation = models.BooleanField(default=False)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Navigation: {self.user.username} → {self.destination_name or self.destination_shop}"
