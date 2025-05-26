"""
Navigation utilities for geo-pin based navigation system
"""
import math
import requests
from typing import List, Dict, Tuple, Optional
from django.conf import settings
from .models import Shop, NavigationRoute, GeofenceZone, UserLocation, Market
import json


class NavigationService:
    """Service class for handling navigation calculations and routing"""
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) * math.sin(delta_lon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def find_nearby_shops(latitude: float, longitude: float, market_id: str, radius_meters: int = 100) -> List[Dict]:
        """Find shops within a specified radius of given coordinates"""
        try:
            market = Market.objects.get(id=market_id)
            shops = market.shops.filter(is_active=True, is_verified=True)
            
            nearby_shops = []
            for shop in shops:
                distance = NavigationService.calculate_distance(
                    latitude, longitude, shop.latitude, shop.longitude
                )
                
                if distance <= radius_meters:
                    nearby_shops.append({
                        'shop': shop,
                        'distance_meters': round(distance, 2),
                        'latitude': shop.latitude,
                        'longitude': shop.longitude,
                        'name': shop.name,
                        'shop_number': shop.shop_number,
                        'floor_level': shop.floor_level
                    })
            
            # Sort by distance
            nearby_shops.sort(key=lambda x: x['distance_meters'])
            return nearby_shops
            
        except Market.DoesNotExist:
            return []
    
    @staticmethod
    def is_point_in_geofence(latitude: float, longitude: float, geofence_zone: GeofenceZone) -> bool:
        """Check if a point is within a geofenced area"""
        try:
            # Simple radius-based check
            distance = NavigationService.calculate_distance(
                latitude, longitude,
                geofence_zone.center_latitude, geofence_zone.center_longitude
            )
            return distance <= geofence_zone.radius_meters
            
        except Exception:
            return False
    
    @staticmethod
    def detect_user_zone(latitude: float, longitude: float, market_id: str) -> Optional[GeofenceZone]:
        """Detect which geofenced zone a user is currently in"""
        try:
            market = Market.objects.get(id=market_id)
            zones = market.geofence_zones.all()
            
            for zone in zones:
                if NavigationService.is_point_in_geofence(latitude, longitude, zone):
                    return zone
            
            return None
            
        except Market.DoesNotExist:
            return None
    
    @staticmethod
    def is_indoor_location(latitude: float, longitude: float, market_id: str) -> bool:
        """Determine if user location is indoors based on market boundaries"""
        try:
            market = Market.objects.get(id=market_id)
            
            if not market.boundary_coordinates:
                return False
            
            # Check if point is within market boundaries
            boundary_points = market.boundary_coordinates
            if isinstance(boundary_points, list) and len(boundary_points) >= 3:
                # Simple point-in-polygon check
                return NavigationService._point_in_polygon(latitude, longitude, boundary_points)
            
            return False
            
        except Market.DoesNotExist:
            return False
    
    @staticmethod
    def _point_in_polygon(lat: float, lon: float, polygon_coords: List[List[float]]) -> bool:
        """Check if point is inside polygon using ray casting algorithm"""
        x, y = lon, lat
        n = len(polygon_coords)
        inside = False
        
        p1x, p1y = polygon_coords[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon_coords[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    @staticmethod
    def calculate_route_to_shop(start_lat: float, start_lon: float, shop_id: str, navigation_mode: str = 'walking') -> Dict:
        """Calculate route from current location to a specific shop"""
        try:
            shop = Shop.objects.get(id=shop_id)
            
            # Check if we have a pre-calculated route
            existing_route = NavigationRoute.objects.filter(
                end_shop=shop,
                start_latitude__isnull=True,
                start_longitude__isnull=True
            ).first()
            
            if existing_route:
                # Use existing route as base and calculate from start point
                route_data = {
                    'route_id': str(existing_route.id),
                    'destination': {
                        'shop_id': str(shop.id),
                        'name': shop.name,
                        'latitude': shop.latitude,
                        'longitude': shop.longitude,
                        'shop_number': shop.shop_number,
                        'floor_level': shop.floor_level
                    },
                    'distance_meters': NavigationService.calculate_distance(
                        start_lat, start_lon, shop.latitude, shop.longitude
                    ),
                    'coordinates': existing_route.route_coordinates,
                    'indoor_coordinates': existing_route.indoor_route_coordinates,
                    'instructions': existing_route.turn_by_turn_instructions,
                    'landmarks': existing_route.landmarks_on_route,
                    'is_indoor_route': existing_route.is_indoor_route,
                    'is_accessible': existing_route.is_accessible_route
                }
            else:
                # Calculate new route
                distance = NavigationService.calculate_distance(
                    start_lat, start_lon, shop.latitude, shop.longitude
                )
                
                # Simple direct route for now
                route_coordinates = [
                    [start_lon, start_lat],
                    [shop.longitude, shop.latitude]
                ]
                
                route_data = {
                    'destination': {
                        'shop_id': str(shop.id),
                        'name': shop.name,
                        'latitude': shop.latitude,
                        'longitude': shop.longitude,
                        'shop_number': shop.shop_number,
                        'floor_level': shop.floor_level
                    },
                    'distance_meters': round(distance, 2),
                    'estimated_time_seconds': int(distance / 1.4),  # Average walking speed
                    'coordinates': route_coordinates,
                    'instructions': NavigationService._generate_basic_instructions(
                        start_lat, start_lon, shop.latitude, shop.longitude, shop.name
                    ),
                    'is_indoor_route': NavigationService.is_indoor_location(start_lat, start_lon, str(shop.market.id)),
                    'is_accessible': shop.is_accessible
                }
            
            return route_data
            
        except Shop.DoesNotExist:
            return {'error': 'Shop not found'}
    
    @staticmethod
    def _generate_basic_instructions(start_lat: float, start_lon: float, end_lat: float, end_lon: float, destination_name: str) -> List[Dict]:
        """Generate basic turn-by-turn instructions"""
        bearing = NavigationService._calculate_bearing(start_lat, start_lon, end_lat, end_lon)
        direction = NavigationService._bearing_to_direction(bearing)
        
        distance = NavigationService.calculate_distance(start_lat, start_lon, end_lat, end_lon)
        
        instructions = [
            {
                'step': 1,
                'instruction': f"Head {direction} toward {destination_name}",
                'distance_meters': round(distance, 2),
                'bearing': bearing,
                'coordinates': [start_lon, start_lat]
            },
            {
                'step': 2,
                'instruction': f"Arrive at {destination_name}",
                'distance_meters': 0,
                'bearing': bearing,
                'coordinates': [end_lon, end_lat]
            }
        ]
        
        return instructions
    
    @staticmethod
    def _calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing between two points"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        y = math.sin(delta_lon) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return bearing
    
    @staticmethod
    def _bearing_to_direction(bearing: float) -> str:
        """Convert bearing to cardinal direction"""
        directions = [
            "north", "northeast", "east", "southeast",
            "south", "southwest", "west", "northwest"
        ]
        index = round(bearing / 45) % 8
        return directions[index]
    
    @staticmethod
    def update_user_location(user_id: str, latitude: float, longitude: float, market_id: str = None, **kwargs) -> UserLocation:
        """Update user's current location and detect context"""
        from users.models import User
        
        try:
            user = User.objects.get(id=user_id)
            
            # Detect market if not provided
            if not market_id and kwargs.get('auto_detect_market', True):
                market = NavigationService._detect_nearest_market(latitude, longitude)
                market_id = str(market.id) if market else None
            
            # Detect if location is indoor
            is_indoor = False
            current_zone = None
            current_shop = None
            
            if market_id:
                is_indoor = NavigationService.is_indoor_location(latitude, longitude, market_id)
                current_zone = NavigationService.detect_user_zone(latitude, longitude, market_id)
                
                # Check if user is near any shop
                nearby_shops = NavigationService.find_nearby_shops(latitude, longitude, market_id, 10)
                if nearby_shops:
                    current_shop = nearby_shops[0]['shop']
            
            # Create or update user location
            location_data = {
                'user': user,
                'latitude': latitude,
                'longitude': longitude,
                'altitude': kwargs.get('altitude'),
                'accuracy_meters': kwargs.get('accuracy_meters'),
                'indoor_x': kwargs.get('indoor_x'),
                'indoor_y': kwargs.get('indoor_y'),
                'floor_level': kwargs.get('floor_level'),
                'is_indoor': is_indoor,
                'current_shop': current_shop,
                'current_zone': current_zone,
                'battery_level': kwargs.get('battery_level'),
                'signal_strength': kwargs.get('signal_strength')
            }
            
            if market_id:
                try:
                    market = Market.objects.get(id=market_id)
                    location_data['market'] = market
                except Market.DoesNotExist:
                    pass
            
            location = UserLocation.objects.create(**location_data)
            return location
            
        except User.DoesNotExist:
            raise ValueError("User not found")
    
    @staticmethod
    def _detect_nearest_market(latitude: float, longitude: float, max_distance_km: float = 5.0) -> Optional[Market]:
        """Detect the nearest market to given coordinates"""
        markets = Market.objects.all()
        nearest_market = None
        min_distance = float('inf')
        
        for market in markets:
            distance = NavigationService.calculate_distance(
                latitude, longitude, market.latitude, market.longitude
            )
            
            if distance < min_distance and distance <= (max_distance_km * 1000):
                min_distance = distance
                nearest_market = market
        
        return nearest_market


class ExternalNavigationService:
    """Service for integrating with external navigation APIs like Google Maps, Mapbox"""
    
    @staticmethod
    def get_google_maps_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, mode: str = 'walking') -> Dict:
        """Get route from Google Maps Directions API"""
        if not hasattr(settings, 'GOOGLE_MAPS_API_KEY') or not settings.GOOGLE_MAPS_API_KEY:
            return {'error': 'Google Maps API key not configured'}
        
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            'origin': f"{start_lat},{start_lon}",
            'destination': f"{end_lat},{end_lon}",
            'mode': mode,
            'key': settings.GOOGLE_MAPS_API_KEY
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'Google Maps API error: {str(e)}'}
    
    @staticmethod
    def get_mapbox_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, profile: str = 'walking') -> Dict:
        """Get route from Mapbox Directions API"""
        if not hasattr(settings, 'MAPBOX_ACCESS_TOKEN') or not settings.MAPBOX_ACCESS_TOKEN:
            return {'error': 'Mapbox access token not configured'}
        
        url = f"https://api.mapbox.com/directions/v5/mapbox/{profile}/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            'access_token': settings.MAPBOX_ACCESS_TOKEN,
            'geometries': 'geojson',
            'steps': 'true'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'Mapbox API error: {str(e)}'}


class IndoorNavigationService:
    """Service for indoor navigation within markets"""
    
    @staticmethod
    def calculate_indoor_route(start_x: float, start_y: float, end_x: float, end_y: float, floor: int, market_id: str) -> Dict:
        """Calculate route for indoor navigation using indoor coordinates"""
        try:
            market = Market.objects.get(id=market_id)
            
            if not market.indoor_map_enabled:
                return {'error': 'Indoor navigation not available for this market'}
            
            # Simple direct indoor route
            route_points = [
                {'x': start_x, 'y': start_y, 'floor': floor},
                {'x': end_x, 'y': end_y, 'floor': floor}
            ]
            
            # Calculate distance (assuming indoor coordinates are in meters)
            distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
            
            return {
                'route_points': route_points,
                'distance_meters': round(distance, 2),
                'estimated_time_seconds': int(distance / 1.0),  # Slower indoor walking speed
                'floor': floor,
                'instructions': IndoorNavigationService._generate_indoor_instructions(
                    start_x, start_y, end_x, end_y, floor
                )
            }
            
        except Market.DoesNotExist:
            return {'error': 'Market not found'}
    
    @staticmethod
    def _generate_indoor_instructions(start_x: float, start_y: float, end_x: float, end_y: float, floor: int) -> List[Dict]:
        """Generate indoor navigation instructions"""
        dx = end_x - start_x
        dy = end_y - start_y
        
        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "forward" if dy > 0 else "backward"
        
        distance = math.sqrt(dx**2 + dy**2)
        
        return [
            {
                'step': 1,
                'instruction': f"Walk {direction} for {round(distance, 1)} meters",
                'distance_meters': round(distance, 2),
                'indoor_coordinates': {'x': start_x, 'y': start_y, 'floor': floor}
            },
            {
                'step': 2,
                'instruction': "You have arrived at your destination",
                'distance_meters': 0,
                'indoor_coordinates': {'x': end_x, 'y': end_y, 'floor': floor}
            }
        ]
