from rest_framework import serializers
from .models import (
    Market, Shop, NavigationRoute, GeofenceZone, 
    UserLocation, NavigationSession, Category, Product, 
    ProductImage, Order, OrderItem, SellerAnalytics, 
    SellerWallet, WalletTransaction
)
from users.models import User


# Navigation-specific serializers
class ShopSerializer(serializers.ModelSerializer):
    """Serializer for Shop model with geo-pin data"""
    distance_meters = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'description', 'shop_number', 'floor_level',
            'latitude', 'longitude', 'altitude', 'indoor_x', 'indoor_y', 'indoor_floor',
            'entrance_latitude', 'entrance_longitude', 'shop_width', 'shop_length',
            'is_accessible', 'has_wheelchair_access', 'navigation_landmarks',
            'phone_number', 'operating_hours', 'image', 'is_active', 'is_verified',
            'market', 'seller', 'distance_meters', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'distance_meters']


class ShopDetailSerializer(ShopSerializer):
    """Detailed serializer for Shop with related data"""
    market_name = serializers.CharField(source='market.name', read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    
    class Meta(ShopSerializer.Meta):
        fields = ShopSerializer.Meta.fields + ['market_name', 'seller_name']


class NavigationRouteSerializer(serializers.ModelSerializer):
    """Serializer for NavigationRoute model"""
    start_shop_name = serializers.CharField(source='start_shop.name', read_only=True)
    end_shop_name = serializers.CharField(source='end_shop.name', read_only=True)
    
    class Meta:
        model = NavigationRoute
        fields = [
            'id', 'market', 'start_shop', 'end_shop', 'start_shop_name', 'end_shop_name',
            'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude',
            'route_coordinates', 'indoor_route_coordinates', 'distance_meters',
            'estimated_walk_time_seconds', 'is_indoor_route', 'is_accessible_route',
            'turn_by_turn_instructions', 'landmarks_on_route', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GeofenceZoneSerializer(serializers.ModelSerializer):
    """Serializer for GeofenceZone model"""
    
    class Meta:
        model = GeofenceZone
        fields = [
            'id', 'market', 'name', 'zone_type', 'description',
            'boundary_coordinates', 'center_latitude', 'center_longitude', 'radius_meters',
            'is_indoor', 'floor_level', 'is_restricted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserLocationSerializer(serializers.ModelSerializer):
    """Serializer for UserLocation model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    market_name = serializers.CharField(source='market.name', read_only=True)
    shop_name = serializers.CharField(source='current_shop.name', read_only=True)
    zone_name = serializers.CharField(source='current_zone.name', read_only=True)
    
    class Meta:
        model = UserLocation
        fields = [
            'id', 'user', 'user_name', 'market', 'market_name',
            'latitude', 'longitude', 'altitude', 'accuracy_meters',
            'indoor_x', 'indoor_y', 'floor_level', 'is_indoor',
            'current_shop', 'shop_name', 'current_zone', 'zone_name',
            'battery_level', 'signal_strength', 'timestamp'
        ]
        read_only_fields = ['id', 'user_name', 'market_name', 'shop_name', 'zone_name', 'timestamp']


class NavigationSessionSerializer(serializers.ModelSerializer):
    """Serializer for NavigationSession model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    market_name = serializers.CharField(source='market.name', read_only=True)
    destination_shop_name = serializers.CharField(source='destination_shop.name', read_only=True)
    
    class Meta:
        model = NavigationSession
        fields = [
            'id', 'user', 'user_name', 'market', 'market_name',
            'destination_shop', 'destination_shop_name', 'destination_latitude', 'destination_longitude',
            'destination_name', 'selected_route', 'route_coordinates', 'status',
            'start_latitude', 'start_longitude', 'current_step_index',
            'distance_remaining_meters', 'estimated_time_remaining_seconds',
            'navigation_mode', 'use_indoor_navigation', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user_name', 'market_name', 'destination_shop_name', 'started_at']


class RouteCalculationSerializer(serializers.Serializer):
    """Serializer for route calculation requests"""
    start_latitude = serializers.FloatField()
    start_longitude = serializers.FloatField()
    destination_shop_id = serializers.UUIDField(required=False)
    destination_latitude = serializers.FloatField(required=False)
    destination_longitude = serializers.FloatField(required=False)
    navigation_mode = serializers.ChoiceField(choices=['walking', 'driving', 'accessibility'], default='walking')
    use_indoor_navigation = serializers.BooleanField(default=False)
    
    def validate(self, data):
        if not data.get('destination_shop_id') and not (data.get('destination_latitude') and data.get('destination_longitude')):
            raise serializers.ValidationError("Either destination_shop_id or destination coordinates must be provided")
        return data


class LocationUpdateSerializer(serializers.Serializer):
    """Serializer for user location updates"""
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    altitude = serializers.FloatField(required=False)
    accuracy_meters = serializers.FloatField(required=False)
    indoor_x = serializers.FloatField(required=False)
    indoor_y = serializers.FloatField(required=False)
    floor_level = serializers.IntegerField(required=False)
    battery_level = serializers.IntegerField(required=False, min_value=0, max_value=100)
    signal_strength = serializers.IntegerField(required=False, min_value=0, max_value=100)
    market_id = serializers.UUIDField(required=False)


class NearbyShopsSerializer(serializers.Serializer):
    """Serializer for nearby shops requests"""
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    radius_meters = serializers.IntegerField(default=100, min_value=1, max_value=1000)
    market_id = serializers.UUIDField()


class NavigationStatusSerializer(serializers.Serializer):
    """Serializer for navigation status updates"""
    session_id = serializers.UUIDField()
    current_latitude = serializers.FloatField()
    current_longitude = serializers.FloatField()
    current_step_index = serializers.IntegerField(default=0)
    status = serializers.ChoiceField(choices=['active', 'completed', 'cancelled', 'paused'], default='active')


# Update existing Market serializers
class MarketSerializer(serializers.ModelSerializer):
    """Serializer for Market model with geo-navigation features"""
    shops_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Market
        fields = [
            'id', 'name', 'description', 'address', 'city', 'state', 'country',
            'latitude', 'longitude', 'opening_time', 'closing_time', 'image',
            'map_data', 'map_image', 'indoor_map_enabled', 'outdoor_navigation_enabled',
            'boundary_coordinates', 'shops_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shops_count', 'created_at', 'updated_at']


class MarketDetailSerializer(MarketSerializer):
    """Detailed serializer for Market with shops and zones"""
    shops = ShopSerializer(many=True, read_only=True)
    geofence_zones = GeofenceZoneSerializer(many=True, read_only=True)
    
    class Meta(MarketSerializer.Meta):
        fields = MarketSerializer.Meta.fields + ['shops', 'geofence_zones']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    class Meta:
        model = Category
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'display_order']


class ProductSerializer(serializers.ModelSerializer):
    """Basic product serializer"""
    additional_images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock_quantity',
            'is_available', 'main_image', 'category', 'seller',
            'market', 'store_location_description', 'created_at',
            'additional_images'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer"""
    additional_images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock_quantity',
            'is_available', 'main_image', 'category', 'seller',
            'market', 'store_location_description', 'weight',
            'dimensions', 'created_at', 'updated_at', 'additional_images'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'quantity', 'price_at_time_of_order',
            'product_name', 'product_description', 'subtotal'
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'seller', 'status', 'total_amount',
            'buyer_note', 'seller_note', 'created_at', 'updated_at',
            'items'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    items = serializers.ListField(write_only=True)
    
    class Meta:
        model = Order
        fields = ['buyer', 'seller', 'buyer_note', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        total_amount = 0
        
        # Create the order
        order = Order.objects.create(
            buyer=validated_data['buyer'],
            seller=validated_data['seller'],
            buyer_note=validated_data.get('buyer_note', ''),
            total_amount=0  # Will update this after calculating
        )
        
        # Create order items
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product'])
            price = product.price
            quantity = item_data['quantity']
            subtotal = price * quantity
            total_amount += subtotal
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_time_of_order=price,
                product_name=product.name,
                product_description=product.description
            )
        
        # Update the total amount
        order.total_amount = total_amount
        order.save()
        
        return order


class SellerAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for seller analytics"""
    class Meta:
        model = SellerAnalytics
        fields = '__all__'


class SellerWalletSerializer(serializers.ModelSerializer):
    """Serializer for seller wallet"""
    class Meta:
        model = SellerWallet
        fields = [
            'id', 'seller', 'balance', 'total_earnings',
            'bank_name', 'account_name', 'account_number'
        ]


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for wallet transactions"""
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'wallet', 'amount', 'transaction_type',
            'status', 'reference', 'description',
            'created_at', 'updated_at'
        ]


class WithdrawRequestSerializer(serializers.Serializer):
    """Serializer for requesting withdrawals"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
            
        # Get seller wallet balance
        user = self.context['request'].user
        try:
            wallet = SellerWallet.objects.get(seller=user)
            if value > wallet.balance:
                raise serializers.ValidationError(f"Insufficient balance. Available: {wallet.balance}")
        except SellerWallet.DoesNotExist:
            raise serializers.ValidationError("Wallet not found for this seller.")
            
        return value
