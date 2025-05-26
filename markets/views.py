from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import (
    Market, Shop, NavigationRoute, GeofenceZone, UserLocation, NavigationSession,
    Category, Product, ProductImage, Order, OrderItem, SellerAnalytics, 
    SellerWallet, WalletTransaction
)
from .serializers import (
    MarketSerializer, MarketDetailSerializer, ShopSerializer, ShopDetailSerializer,
    NavigationRouteSerializer, GeofenceZoneSerializer, UserLocationSerializer,
    NavigationSessionSerializer, RouteCalculationSerializer, LocationUpdateSerializer,
    NearbyShopsSerializer, NavigationStatusSerializer, CategorySerializer,
    ProductSerializer, ProductDetailSerializer, ProductImageSerializer,
    OrderSerializer, OrderCreateSerializer, OrderItemSerializer,
    SellerAnalyticsSerializer, SellerWalletSerializer, WalletTransactionSerializer,
    WithdrawRequestSerializer
)
from .navigation_utils import NavigationService, ExternalNavigationService, IndoorNavigationService
from users.models import User
from django.utils import timezone


class IsSellerPermission(permissions.BasePermission):
    """Permission to check if user is a seller"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.ROLE_SELLER


class IsBuyerPermission(permissions.BasePermission):
    """Permission to check if user is a buyer"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.ROLE_USER


class IsAdminPermission(permissions.BasePermission):
    """Permission to check if user is an admin"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.ROLE_ADMIN


class MarketViewSet(viewsets.ModelViewSet):
    """API endpoints for markets"""
    queryset = Market.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'address', 'city', 'state']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MarketDetailSerializer
        return MarketSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'sellers', 'map']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def sellers(self, request, pk=None):
        """Get sellers in a specific market"""
        market = self.get_object()
        sellers = User.objects.filter(
            role=User.ROLE_SELLER,
            products__market=market
        ).distinct()
        from users.serializers import UserDetailSerializer
        serializer = UserDetailSerializer(sellers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def map(self, request, pk=None):
        """Get indoor map or GPS layout for a market"""
        market = self.get_object()
        map_data = {
            "market_id": market.id,
            "name": market.name,
            "map_data": market.map_data,
            "map_image": request.build_absolute_uri(market.map_image.url) if market.map_image else None,
        }
        return Response(map_data)
    
    @action(detail=False, methods=['get'])
    def pin_search(self, request):
        """Determine market location from coordinates"""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        if not (lat and lng):
            return Response(
                {"error": "Both 'lat' and 'lng' parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response(
                {"error": "Invalid coordinate format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simple proximity search - in a real app, you'd want to use GeoDjango
        # or a more sophisticated spatial search algorithm
        # This is a very basic approximation
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            # Convert decimal degrees to radians
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            # Haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # Radius of earth in kilometers
            return c * r * 1000  # Convert to meters
        
        # Find closest market
        closest_market = None
        min_distance = float('inf')
        
        for market in Market.objects.all():
            distance = haversine(lng, lat, market.longitude, market.latitude)
            if distance < min_distance:
                min_distance = distance
                closest_market = market
        
        # If no market is found or closest is more than 5km away
        if not closest_market or min_distance > 5000:
            return Response({"message": "No markets found near this location"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(closest_market)
        data = serializer.data
        data['distance'] = round(min_distance)  # Distance in meters
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def shops(self, request, pk=None):
        """Get all shops in a market with their geo-pin coordinates"""
        market = self.get_object()
        shops = market.shops.filter(is_active=True, is_verified=True)
        
        # Add distance calculation if user location provided
        user_lat = request.query_params.get('user_latitude')
        user_lon = request.query_params.get('user_longitude')
        
        if user_lat and user_lon:
            try:
                user_lat = float(user_lat)
                user_lon = float(user_lon)
                
                shops_with_distance = []
                for shop in shops:
                    distance = NavigationService.calculate_distance(
                        user_lat, user_lon, shop.latitude, shop.longitude
                    )
                    shop.distance_meters = distance
                    shops_with_distance.append(shop)
                
                # Sort by distance
                shops_with_distance.sort(key=lambda x: x.distance_meters)
                shops = shops_with_distance
            except (ValueError, TypeError):
                pass  # Invalid coordinates, continue without distance
        
        serializer = ShopSerializer(shops, many=True)
        return Response({
            'market': MarketSerializer(market).data,
            'shops': serializer.data,
            'count': len(shops)
        })
    
    @action(detail=True, methods=['get'])
    def navigation_info(self, request, pk=None):
        """Get navigation information for a market"""
        market = self.get_object()
        
        navigation_info = {
            'market': MarketDetailSerializer(market).data,
            'indoor_navigation_enabled': market.indoor_map_enabled,
            'outdoor_navigation_enabled': market.outdoor_navigation_enabled,
            'has_boundary_data': bool(market.boundary_coordinates),
            'has_map_data': bool(market.map_data),
            'shops_count': market.shops.filter(is_active=True).count(),
            'geofence_zones_count': market.geofence_zones.count(),
            'entrance_zones': list(market.geofence_zones.filter(zone_type='entrance').values(
                'id', 'name', 'center_latitude', 'center_longitude'
            )),
            'parking_zones': list(market.geofence_zones.filter(zone_type='parking').values(
                'id', 'name', 'center_latitude', 'center_longitude'
            ))
        }
        
        return Response(navigation_info)
    
    @action(detail=True, methods=['post'])
    def check_indoor_location(self, request, pk=None):
        """Check if coordinates are inside the market (indoor)"""
        market = self.get_object()
        data = request.data
        
        if 'latitude' not in data or 'longitude' not in data:
            return Response({
                'error': 'latitude and longitude are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
            
            is_indoor = NavigationService.is_indoor_location(
                latitude, longitude, str(market.id)
            )
            
            # Detect current zone
            current_zone = NavigationService.detect_user_zone(
                latitude, longitude, str(market.id)
            )
            
            response_data = {
                'is_indoor': is_indoor,
                'market_id': str(market.id),
                'market_name': market.name,
                'current_zone': GeofenceZoneSerializer(current_zone).data if current_zone else None,
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                }
            }
            
            return Response(response_data)
            
        except (ValueError, TypeError) as e:
            return Response({
                'error': f'Invalid coordinates: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        

class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoints for categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'products']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products in a category"""
        category = self.get_object()
        products = Product.objects.filter(
            Q(category=category) | Q(category__parent=category),
            is_available=True
        )
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoints for products"""
    queryset = Product.objects.filter(is_available=True)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'seller__username', 'market__name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsSellerPermission()]
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class SellerDashboardViewSet(viewsets.ViewSet):
    """API endpoints for seller dashboard"""
    permission_classes = [IsSellerPermission]
    
    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        """Get or update seller profile/storefront"""
        user = request.user
        
        if request.method == 'GET':
            from users.serializers import UserDetailSerializer
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            from users.serializers import UserSerializer
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def verify_docs(self, request):
        """Upload verification documents"""
        user = request.user
        
        # Handle file uploads for verification
        verification_docs = {}
        
        if 'id_document' in request.FILES:
            # In a real app, you'd save this to S3/Cloudinary
            id_doc = request.FILES['id_document']
            # Placeholder for file storage logic
            verification_docs['id_document'] = str(id_doc)
            
        if 'cac_document' in request.FILES:
            cac_doc = request.FILES['cac_document']
            verification_docs['cac_document'] = str(cac_doc)
            
        if 'store_photos' in request.FILES.getlist('store_photos'):
            store_photos = request.FILES.getlist('store_photos')
            verification_docs['store_photos'] = [str(photo) for photo in store_photos]
        
        # Update user verification documents
        if verification_docs:
            user.verification_documents = verification_docs
            user.verification_status = 'pending'
            user.save()
            
            return Response({"message": "Verification documents submitted successfully"})
        
        return Response(
            {"error": "No verification documents provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def products(self, request):
        """Get seller's products"""
        products = Product.objects.filter(seller=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def orders(self, request):
        """Get seller's orders"""
        status_filter = request.query_params.get('status', None)
        
        orders = Order.objects.filter(seller=request.user)
        if status_filter:
            orders = orders.filter(status=status_filter)
            
        orders = orders.order_by('-created_at')
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'])
    def update_order(self, request, pk=None):
        """Update order status"""
        order = get_object_or_404(Order, pk=pk, seller=request.user)
        new_status = request.data.get('status', None)
        
        if not new_status:
            return Response(
                {"error": "Status field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if new_status not in [s[0] for s in Order.STATUS_CHOICES]:
            return Response(
                {"error": "Invalid status value"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        
        if 'seller_note' in request.data:
            order.seller_note = request.data['seller_note']
            
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get seller analytics"""
        user = request.user
        
        # Try to get existing analytics or create new ones
        analytics, created = SellerAnalytics.objects.get_or_create(seller=user)
        
        # In a real app, you'd want to calculate these values dynamically
        # based on actual views, orders, etc.
        
        serializer = SellerAnalyticsSerializer(analytics)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def earnings(self, request):
        """Get seller earnings"""
        user = request.user
        
        # Try to get wallet or create new one
        wallet, created = SellerWallet.objects.get_or_create(seller=user)
        
        data = {
            "total_earnings": wallet.total_earnings,
            "available_balance": wallet.balance
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def wallet(self, request):
        """Get seller wallet details and transactions"""
        user = request.user
        
        # Get or create wallet
        wallet, created = SellerWallet.objects.get_or_create(seller=user)
        
        # Get recent transactions
        transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:10]
        
        wallet_serializer = SellerWalletSerializer(wallet)
        transaction_serializer = WalletTransactionSerializer(transactions, many=True)
        
        data = {
            "wallet": wallet_serializer.data,
            "recent_transactions": transaction_serializer.data
        }
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """Request a withdrawal from seller wallet"""
        serializer = WithdrawRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        amount = serializer.validated_data['amount']
        user = request.user
        
        try:
            wallet = SellerWallet.objects.get(seller=user)
            
            # Ensure bank details are set
            if not wallet.bank_name or not wallet.account_number:
                return Response(
                    {"error": "Bank account details are not complete. Please update your profile."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Create withdrawal transaction
            transaction = WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='withdrawal',
                status='pending',
                description=f"Withdrawal request of {amount}"
            )
            
            # In a real app, you'd process this asynchronously
            # For now, we'll just update the wallet balance immediately
            wallet.balance -= amount
            wallet.save()
            
            return Response({
                "message": "Withdrawal request successful",
                "transaction_id": transaction.id
            })
            
        except SellerWallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found for this seller"},
                status=status.HTTP_404_NOT_FOUND
            )


class UserOrderViewSet(viewsets.ModelViewSet):
    """API endpoints for user orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)


class HomeViewSet(viewsets.ViewSet):
    """API endpoints for home page data"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def highlights(self, request):
        """Get highlights for home page"""
        # Get featured sellers (those with most products)
        featured_sellers = User.objects.filter(role=User.ROLE_SELLER, is_verified=True)\
                                .annotate(product_count=Count('products'))\
                                .order_by('-product_count')[:5]
        
        # Get featured products (most recently added)
        featured_products = Product.objects.filter(is_available=True)\
                                  .order_by('-created_at')[:10]
        
        # Serialize the data
        from users.serializers import UserDetailSerializer
        seller_serializer = UserDetailSerializer(featured_sellers, many=True)
        product_serializer = ProductSerializer(featured_products, many=True)
        
        data = {
            "featured_sellers": seller_serializer.data,
            "featured_products": product_serializer.data,
            "categories": CategorySerializer(Category.objects.filter(parent=None)[:8], many=True).data,
            "markets": MarketSerializer(Market.objects.all()[:5], many=True).data
        }
        
        return Response(data)


class AdminSellerViewSet(viewsets.ViewSet):
    """API endpoints for admin to manage sellers"""
    permission_classes = [IsAdminPermission]
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get list of sellers awaiting approval"""
        pending_sellers = User.objects.filter(
            role=User.ROLE_SELLER,
            verification_status='pending'
        )
        
        from users.serializers import UserDetailSerializer
        serializer = UserDetailSerializer(pending_sellers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a seller profile"""
        seller = get_object_or_404(
            User,
            pk=pk,
            role=User.ROLE_SELLER,
            verification_status='pending'
        )
        
        seller.verification_status = 'verified'
        seller.is_verified = True
        seller.save()
        
        return Response({"message": f"Seller {seller.username} has been approved"})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject seller with feedback"""
        seller = get_object_or_404(
            User,
            pk=pk,
            role=User.ROLE_SELLER,
            verification_status='pending'
        )
        
        reason = request.data.get('reason', 'No reason provided')
        
        seller.verification_status = 'rejected'
        seller.rejection_reason = reason
        seller.save()
        
        return Response({"message": f"Seller {seller.username} has been rejected"})


class ShopViewSet(viewsets.ModelViewSet):
    """API endpoints for shops with geo-pin coordinates"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'shop_number', 'seller__username']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ShopDetailSerializer
        return ShopSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'nearby', 'route_to']:
            return [permissions.AllowAny()]
        elif self.action in ['create', 'update', 'partial_update']:
            return [IsSellerPermission()]
        return [IsAdminPermission()]
    
    def get_queryset(self):
        queryset = Shop.objects.select_related('market', 'seller').filter(is_active=True)
        
        # Filter by market
        market_id = self.request.query_params.get('market')
        if market_id:
            queryset = queryset.filter(market_id=market_id)
        
        # Filter by seller (for seller's own shops)
        if self.request.user.is_authenticated and self.request.user.role == User.ROLE_SELLER:
            if self.action in ['update', 'partial_update', 'destroy']:
                queryset = queryset.filter(seller=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    @action(detail=False, methods=['post'])
    def nearby(self, request):
        """Find nearby shops based on user location"""
        serializer = NearbyShopsSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            nearby_shops = NavigationService.find_nearby_shops(
                latitude=data['latitude'],
                longitude=data['longitude'],
                market_id=str(data['market_id']),
                radius_meters=data['radius_meters']
            )
            
            return Response({
                'shops': nearby_shops,
                'count': len(nearby_shops),
                'search_radius_meters': data['radius_meters'],
                'search_location': {
                    'latitude': data['latitude'],
                    'longitude': data['longitude']
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def route_to(self, request, pk=None):
        """Calculate route to a specific shop"""
        shop = self.get_object()
        serializer = RouteCalculationSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            route_data = NavigationService.calculate_route_to_shop(
                start_lat=data['start_latitude'],
                start_lon=data['start_longitude'],
                shop_id=str(shop.id),
                navigation_mode=data['navigation_mode']
            )
            
            if 'error' in route_data:
                return Response(route_data, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(route_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NavigationViewSet(viewsets.ViewSet):
    """API endpoints for navigation functionality"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def start_navigation(self, request):
        """Start a new navigation session"""
        serializer = RouteCalculationSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Calculate route
            if data.get('destination_shop_id'):
                route_data = NavigationService.calculate_route_to_shop(
                    start_lat=data['start_latitude'],
                    start_lon=data['start_longitude'],
                    shop_id=str(data['destination_shop_id']),
                    navigation_mode=data['navigation_mode']
                )
                
                if 'error' in route_data:
                    return Response(route_data, status=status.HTTP_400_BAD_REQUEST)
                
                # Get shop for destination
                try:
                    destination_shop = Shop.objects.get(id=data['destination_shop_id'])
                    destination_name = destination_shop.name
                    market = destination_shop.market
                except Shop.DoesNotExist:
                    return Response({'error': 'Destination shop not found'}, status=status.HTTP_404_NOT_FOUND)
                
            else:
                # Calculate route to coordinates
                destination_name = f"Location ({data['destination_latitude']}, {data['destination_longitude']})"
                route_data = {
                    'destination': {
                        'latitude': data['destination_latitude'],
                        'longitude': data['destination_longitude'],
                        'name': destination_name
                    },
                    'distance_meters': NavigationService.calculate_distance(
                        data['start_latitude'], data['start_longitude'],
                        data['destination_latitude'], data['destination_longitude']
                    ),
                    'coordinates': [
                        [data['start_longitude'], data['start_latitude']],
                        [data['destination_longitude'], data['destination_latitude']]
                    ]
                }
                market = NavigationService._detect_nearest_market(
                    data['destination_latitude'], data['destination_longitude']
                )
                destination_shop = None
            
            # Create navigation session
            session_data = {
                'user': request.user,
                'market': market,
                'destination_shop': destination_shop,
                'destination_latitude': data.get('destination_latitude'),
                'destination_longitude': data.get('destination_longitude'),
                'destination_name': destination_name,
                'route_coordinates': route_data.get('coordinates'),
                'start_latitude': data['start_latitude'],
                'start_longitude': data['start_longitude'],
                'navigation_mode': data['navigation_mode'],
                'use_indoor_navigation': data['use_indoor_navigation']
            }
            
            session = NavigationSession.objects.create(**session_data)
            
            response_data = {
                'session_id': str(session.id),
                'route': route_data,
                'navigation_mode': data['navigation_mode'],
                'use_indoor_navigation': data['use_indoor_navigation'],
                'started_at': session.started_at
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_location(self, request):
        """Update user's current location"""
        serializer = LocationUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                location = NavigationService.update_user_location(
                    user_id=str(request.user.id),
                    latitude=data['latitude'],
                    longitude=data['longitude'],
                    market_id=str(data['market_id']) if data.get('market_id') else None,
                    **{k: v for k, v in data.items() if k not in ['latitude', 'longitude', 'market_id']}
                )
                
                location_serializer = UserLocationSerializer(location)
                return Response(location_serializer.data)
                
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_navigation_status(self, request):
        """Update navigation session status"""
        serializer = NavigationStatusSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                session = NavigationSession.objects.get(
                    id=data['session_id'],
                    user=request.user
                )
                
                # Update session status
                session.current_step_index = data['current_step_index']
                session.status = data['status']
                
                if data['status'] == 'completed':
                    session.completed_at = timezone.now()
                
                # Calculate remaining distance
                if session.destination_latitude and session.destination_longitude:
                    remaining_distance = NavigationService.calculate_distance(
                        data['current_latitude'], data['current_longitude'],
                        session.destination_latitude, session.destination_longitude
                    )
                    session.distance_remaining_meters = remaining_distance
                    session.estimated_time_remaining_seconds = int(remaining_distance / 1.4)  # walking speed
                
                session.save()
                
                session_serializer = NavigationSessionSerializer(session)
                return Response(session_serializer.data)
                
            except NavigationSession.DoesNotExist:
                return Response({'error': 'Navigation session not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def active_session(self, request):
        """Get user's active navigation session"""
        try:
            session = NavigationSession.objects.get(
                user=request.user,
                status='active'
            )
            serializer = NavigationSessionSerializer(session)
            return Response(serializer.data)
        except NavigationSession.DoesNotExist:
            return Response({'message': 'No active navigation session'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def indoor_route(self, request):
        """Calculate indoor navigation route"""
        data = request.data
        
        required_fields = ['start_x', 'start_y', 'end_x', 'end_y', 'floor', 'market_id']
        if not all(field in data for field in required_fields):
            return Response({
                'error': 'Missing required fields',
                'required': required_fields
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            route_data = IndoorNavigationService.calculate_indoor_route(
                start_x=float(data['start_x']),
                start_y=float(data['start_y']),
                end_x=float(data['end_x']),
                end_y=float(data['end_y']),
                floor=int(data['floor']),
                market_id=str(data['market_id'])
            )
            
            if 'error' in route_data:
                return Response(route_data, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(route_data)
            
        except (ValueError, TypeError) as e:
            return Response({'error': f'Invalid input data: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class GeofenceViewSet(viewsets.ModelViewSet):
    """API endpoints for geofenced zones"""
    queryset = GeofenceZone.objects.all()
    serializer_class = GeofenceZoneSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminPermission()]
    
    def get_queryset(self):
        queryset = GeofenceZone.objects.select_related('market')
        
        # Filter by market
        market_id = self.request.query_params.get('market')
        if market_id:
            queryset = queryset.filter(market_id=market_id)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def detect_zone(self, request):
        """Detect which geofenced zone a location is in"""
        data = request.data
        
        if 'latitude' not in data or 'longitude' not in data or 'market_id' not in data:
            return Response({
                'error': 'latitude, longitude, and market_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            zone = NavigationService.detect_user_zone(
                latitude=float(data['latitude']),
                longitude=float(data['longitude']),
                market_id=str(data['market_id'])
            )
            
            if zone:
                serializer = GeofenceZoneSerializer(zone)
                return Response({
                    'zone': serializer.data,
                    'in_zone': True
                })
            else:
                return Response({
                    'zone': None,
                    'in_zone': False
                })
                
        except (ValueError, TypeError) as e:
            return Response({'error': f'Invalid input data: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
