from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from markets.models import Market, Category, Shop, GeofenceZone
from users.models import User
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing the iMarket navigation system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
          # Create sample users
        if not User.objects.filter(username='seller1').exists():
            seller1 = User.objects.create_user(
                username='seller1',
                email='seller1@example.com',
                password='password123',
                role='seller',
                first_name='John',
                last_name='Seller'
            )
            self.stdout.write(f'Created seller: {seller1.username}')
        else:
            seller1 = User.objects.get(username='seller1')

        if not User.objects.filter(username='buyer1').exists():
            buyer1 = User.objects.create_user(
                username='buyer1',
                email='buyer1@example.com',
                password='password123',
                role='user',
                first_name='Jane',
                last_name='Buyer'
            )
            self.stdout.write(f'Created buyer: {buyer1.username}')
        else:
            buyer1 = User.objects.get(username='buyer1')

        # Create sample market
        if not Market.objects.filter(name='Lagos Central Market').exists():
            market = Market.objects.create(
                name='Lagos Central Market',
                description='Main commercial market in Lagos',
                address='123 Market Street, Lagos Island',
                city='Lagos',
                state='Lagos',
                country='Nigeria',
                latitude=6.4531,
                longitude=3.3958,
                outdoor_navigation_enabled=True,
                indoor_map_enabled=True,
                boundary_coordinates=[
                    [6.4525, 3.3950],
                    [6.4535, 3.3950],
                    [6.4535, 3.3965],
                    [6.4525, 3.3965],
                    [6.4525, 3.3950]
                ]
            )
            self.stdout.write(f'Created market: {market.name}')
        else:
            market = Market.objects.get(name='Lagos Central Market')

        # Create sample categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Food & Beverages', 'description': 'Food items and drinks'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
        ]

        for cat_data in categories_data:
            if not Category.objects.filter(name=cat_data['name']).exists():
                category = Category.objects.create(**cat_data)
                self.stdout.write(f'Created category: {category.name}')

        # Create sample shops with geo-coordinates
        electronics_category = Category.objects.get(name='Electronics')
        clothing_category = Category.objects.get(name='Clothing')

        shops_data = [
            {
                'name': 'TechHub Electronics',
                'seller': seller1,
                'market': market,
                'description': 'Latest smartphones, laptops, and gadgets',
                'shop_number': 'A-101',
                'latitude': 6.4530,
                'longitude': 3.3955,
                'indoor_x': 100.0,
                'indoor_y': 50.0,
                'is_active': True,
                'is_verified': True
            },
            {
                'name': 'Fashion Central',
                'seller': seller1,
                'market': market,
                'description': 'Trendy clothing and accessories',
                'shop_number': 'B-205',
                'latitude': 6.4532,
                'longitude': 3.3960,
                'indoor_x': 200.0,
                'indoor_y': 150.0,
                'is_active': True,
                'is_verified': True
            },
            {
                'name': 'Mobile Repair Shop',
                'seller': seller1,
                'market': market,
                'description': 'Phone and laptop repair services',
                'shop_number': 'A-115',
                'latitude': 6.4529,
                'longitude': 3.3957,
                'indoor_x': 120.0,
                'indoor_y': 80.0,
                'is_active': True,
                'is_verified': True
            }
        ]

        for shop_data in shops_data:
            if not Shop.objects.filter(name=shop_data['name']).exists():
                shop = Shop.objects.create(**shop_data)
                self.stdout.write(f'Created shop: {shop.name}')

        # Create geofence zones
        zones_data = [
            {
                'name': 'Main Entrance',
                'market': market,
                'zone_type': 'entrance',
                'center_latitude': 6.4525,
                'center_longitude': 3.3952,
                'radius_meters': 10,
                'boundary_coordinates': [
                    [6.4524, 3.3951],
                    [6.4526, 3.3951],
                    [6.4526, 3.3953],
                    [6.4524, 3.3953],
                    [6.4524, 3.3951]
                ]
            },
            {
                'name': 'Food Court',
                'market': market,
                'zone_type': 'food_court',
                'center_latitude': 6.4533,
                'center_longitude': 3.3962,
                'radius_meters': 15,
                'boundary_coordinates': [
                    [6.4531, 3.3960],
                    [6.4535, 3.3960],
                    [6.4535, 3.3964],
                    [6.4531, 3.3964],
                    [6.4531, 3.3960]
                ]
            },
            {
                'name': 'Parking Area',
                'market': market,
                'zone_type': 'parking',
                'center_latitude': 6.4528,
                'center_longitude': 3.3948,
                'radius_meters': 20,
                'boundary_coordinates': [
                    [6.4525, 3.3945],
                    [6.4531, 3.3945],
                    [6.4531, 3.3951],
                    [6.4525, 3.3951],
                    [6.4525, 3.3945]
                ]
            }
        ]

        for zone_data in zones_data:
            if not GeofenceZone.objects.filter(name=zone_data['name']).exists():
                zone = GeofenceZone.objects.create(**zone_data)
                self.stdout.write(f'Created geofence zone: {zone.name}')

        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )
        
        # Display summary
        self.stdout.write('\n--- DATA SUMMARY ---')
        self.stdout.write(f'Markets: {Market.objects.count()}')
        self.stdout.write(f'Categories: {Category.objects.count()}')
        self.stdout.write(f'Shops: {Shop.objects.count()}')
        self.stdout.write(f'Geofence Zones: {GeofenceZone.objects.count()}')
        self.stdout.write(f'Users: {User.objects.count()}')
