# Generated by Django 5.2.1 on 2025-05-25 21:46

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='market',
            name='boundary_coordinates',
            field=models.JSONField(blank=True, help_text='Polygon coordinates for market boundary', null=True),
        ),
        migrations.AddField(
            model_name='market',
            name='indoor_map_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='market',
            name='outdoor_navigation_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='GeofenceZone',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('zone_type', models.CharField(choices=[('entrance', 'Market Entrance'), ('parking', 'Parking Area'), ('food_court', 'Food Court'), ('restroom', 'Restroom'), ('section', 'Market Section'), ('emergency_exit', 'Emergency Exit'), ('loading_dock', 'Loading Dock')], max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('boundary_coordinates', models.JSONField(help_text='Polygon coordinates defining the zone boundary')),
                ('center_latitude', models.FloatField()),
                ('center_longitude', models.FloatField()),
                ('radius_meters', models.FloatField(default=10)),
                ('is_indoor', models.BooleanField(default=False)),
                ('floor_level', models.IntegerField(default=0)),
                ('is_restricted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='geofence_zones', to='markets.market')),
            ],
        ),
        migrations.CreateModel(
            name='NavigationRoute',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start_latitude', models.FloatField(blank=True, null=True)),
                ('start_longitude', models.FloatField(blank=True, null=True)),
                ('end_latitude', models.FloatField(blank=True, null=True)),
                ('end_longitude', models.FloatField(blank=True, null=True)),
                ('route_coordinates', models.JSONField(help_text='Array of coordinate points for the route')),
                ('indoor_route_coordinates', models.JSONField(blank=True, help_text='Indoor navigation coordinates', null=True)),
                ('distance_meters', models.FloatField()),
                ('estimated_walk_time_seconds', models.IntegerField()),
                ('is_indoor_route', models.BooleanField(default=False)),
                ('is_accessible_route', models.BooleanField(default=True)),
                ('turn_by_turn_instructions', models.JSONField(blank=True, null=True)),
                ('landmarks_on_route', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='routes', to='markets.market')),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('shop_number', models.CharField(blank=True, max_length=50, null=True)),
                ('floor_level', models.CharField(default='Ground Floor', max_length=20)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('altitude', models.FloatField(blank=True, null=True)),
                ('indoor_x', models.FloatField(blank=True, help_text='X coordinate on indoor map', null=True)),
                ('indoor_y', models.FloatField(blank=True, help_text='Y coordinate on indoor map', null=True)),
                ('indoor_floor', models.IntegerField(default=0, help_text='Floor number for multi-story markets')),
                ('entrance_latitude', models.FloatField(blank=True, null=True)),
                ('entrance_longitude', models.FloatField(blank=True, null=True)),
                ('shop_width', models.FloatField(blank=True, null=True)),
                ('shop_length', models.FloatField(blank=True, null=True)),
                ('is_accessible', models.BooleanField(default=True)),
                ('has_wheelchair_access', models.BooleanField(default=False)),
                ('navigation_landmarks', models.JSONField(blank=True, help_text='Nearby landmarks for navigation', null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('operating_hours', models.JSONField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='shop_images/')),
                ('is_active', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shops', to='markets.market')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shops', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('market', 'shop_number')},
            },
        ),
        migrations.CreateModel(
            name='NavigationSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('destination_latitude', models.FloatField(blank=True, null=True)),
                ('destination_longitude', models.FloatField(blank=True, null=True)),
                ('destination_name', models.CharField(blank=True, max_length=200, null=True)),
                ('route_coordinates', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('paused', 'Paused')], default='active', max_length=20)),
                ('start_latitude', models.FloatField()),
                ('start_longitude', models.FloatField()),
                ('current_step_index', models.IntegerField(default=0)),
                ('distance_remaining_meters', models.FloatField(blank=True, null=True)),
                ('estimated_time_remaining_seconds', models.IntegerField(blank=True, null=True)),
                ('navigation_mode', models.CharField(default='walking', max_length=20)),
                ('use_indoor_navigation', models.BooleanField(default=False)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='navigation_sessions', to='markets.market')),
                ('selected_route', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='markets.navigationroute')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='navigation_sessions', to=settings.AUTH_USER_MODEL)),
                ('destination_shop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='navigation_sessions', to='markets.shop')),
            ],
        ),
        migrations.AddField(
            model_name='navigationroute',
            name='end_shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='routes_to', to='markets.shop'),
        ),
        migrations.AddField(
            model_name='navigationroute',
            name='start_shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='routes_from', to='markets.shop'),
        ),
        migrations.CreateModel(
            name='UserLocation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('altitude', models.FloatField(blank=True, null=True)),
                ('accuracy_meters', models.FloatField(blank=True, null=True)),
                ('indoor_x', models.FloatField(blank=True, null=True)),
                ('indoor_y', models.FloatField(blank=True, null=True)),
                ('floor_level', models.IntegerField(blank=True, null=True)),
                ('is_indoor', models.BooleanField(default=False)),
                ('battery_level', models.IntegerField(blank=True, null=True)),
                ('signal_strength', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('current_shop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='markets.shop')),
                ('current_zone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='markets.geofencezone')),
                ('market', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_locations', to='markets.market')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
