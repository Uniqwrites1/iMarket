#!/usr/bin/env python3
"""
Complete navigation workflow testing script for iMarket
Tests all navigation endpoints and OTP authentication
"""

import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000'

def test_authentication():
    """Test user authentication and get JWT tokens"""
    print("🔐 Testing Authentication...")
    
    login_data = {
        'username': 'buyer1',
        'password': 'testpass123'
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/user/login/', json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access']
        user_data = tokens['user']
        print(f"✅ Login successful for user: {user_data['username']} (Role: {user_data['role']})")
        return access_token, user_data
    else:
        print(f"❌ Login failed: {response.text}")
        return None, None

def test_markets_and_shops(headers):
    """Test markets and shops endpoints"""
    print("\n🏪 Testing Markets and Shops...")
    
    # Get markets
    response = requests.get(f'{BASE_URL}/api/markets/', headers=headers)
    print(f"Markets Status: {response.status_code}")
    
    if response.status_code == 200:
        markets = response.json()
        print(f"✅ Found {len(markets)} markets")
        
        if markets:
            market = markets[0]
            market_id = market['id']
            print(f"Using market: {market['name']} (ID: {market_id})")
            
            # Get shops in this market
            response = requests.get(f'{BASE_URL}/api/shops/?market={market_id}', headers=headers)
            print(f"Shops Status: {response.status_code}")
            
            if response.status_code == 200:
                shops = response.json()
                print(f"✅ Found {len(shops)} shops in {market['name']}")
                return market, shops
    
    print("❌ Failed to get markets/shops data")
    return None, None

def test_navigation_workflow(headers, market, shops):
    """Test complete navigation workflow"""
    print("\n🧭 Testing Navigation Workflow...")
    
    if not shops:
        print("❌ No shops available for navigation testing")
        return
    
    # Test 1: Find nearby shops
    print("\n1. Testing nearby shops...")
    nearby_data = {
        'latitude': market['latitude'],
        'longitude': market['longitude'], 
        'market_id': market['id'],
        'radius_meters': 50
    }
    
    response = requests.post(f'{BASE_URL}/api/shops/nearby/', json=nearby_data, headers=headers)
    print(f"Nearby shops Status: {response.status_code}")
    
    if response.status_code == 200:
        nearby_result = response.json()
        print(f"✅ Found {nearby_result['count']} nearby shops")
    else:
        print(f"❌ Nearby shops failed: {response.text}")
    
    # Test 2: Calculate route to a shop
    destination_shop = shops[0]
    print(f"\n2. Testing route calculation to shop: {destination_shop['name']}...")
    
    route_data = {
        'start_latitude': market['latitude'] + 0.001,  # Slightly offset from market center
        'start_longitude': market['longitude'] + 0.001,
        'navigation_mode': 'walking'
    }
    
    response = requests.post(f'{BASE_URL}/api/shops/{destination_shop["id"]}/route_to/', json=route_data, headers=headers)
    print(f"Route calculation Status: {response.status_code}")
    
    if response.status_code == 200:
        route_result = response.json()
        print(f"✅ Route calculated successfully")
        print(f"   Distance: {route_result.get('distance_meters', 'N/A')} meters")
        print(f"   Estimated time: {route_result.get('estimated_walk_time_seconds', 'N/A')} seconds")
    else:
        print(f"❌ Route calculation failed: {response.text}")
    
    # Test 3: Start navigation session
    print(f"\n3. Testing navigation session start...")
    
    navigation_data = {
        'start_latitude': market['latitude'] + 0.001,
        'start_longitude': market['longitude'] + 0.001,
        'destination_shop_id': destination_shop['id'],
        'navigation_mode': 'walking',
        'use_indoor_navigation': False
    }
    
    response = requests.post(f'{BASE_URL}/api/navigation/start_navigation/', json=navigation_data, headers=headers)
    print(f"Start navigation Status: {response.status_code}")
    
    if response.status_code == 201:
        nav_session = response.json()
        session_id = nav_session['session_id']
        print(f"✅ Navigation session started: {session_id}")
        
        # Test 4: Check active session
        print(f"\n4. Testing active session retrieval...")
        response = requests.get(f'{BASE_URL}/api/navigation/active_session/', headers=headers)
        print(f"Active session Status: {response.status_code}")
        
        if response.status_code == 200:
            active_session = response.json()
            print(f"✅ Active session found: {active_session.get('id', 'N/A')}")
        else:
            print(f"❌ Active session check failed: {response.text}")
        
        # Test 5: Update location during navigation
        print(f"\n5. Testing location update...")
        
        location_data = {
            'latitude': market['latitude'] + 0.0005,  # Moving closer to destination
            'longitude': market['longitude'] + 0.0005,
            'market_id': market['id'],
            'accuracy_meters': 5.0,
            'is_indoor': False
        }
        
        response = requests.post(f'{BASE_URL}/api/navigation/update_location/', json=location_data, headers=headers)
        print(f"Location update Status: {response.status_code}")
        
        if response.status_code == 200:
            location_result = response.json()
            print(f"✅ Location updated successfully")
        else:
            print(f"❌ Location update failed: {response.text}")
        
        # Test 6: Update navigation status
        print(f"\n6. Testing navigation status update...")
        
        status_data = {
            'session_id': session_id,
            'current_step_index': 1,
            'status': 'active',
            'current_latitude': market['latitude'] + 0.0005,
            'current_longitude': market['longitude'] + 0.0005
        }
        
        response = requests.post(f'{BASE_URL}/api/navigation/update_navigation_status/', json=status_data, headers=headers)
        print(f"Status update Status: {response.status_code}")
        
        if response.status_code == 200:
            status_result = response.json()
            print(f"✅ Navigation status updated successfully")
        else:
            print(f"❌ Navigation status update failed: {response.text}")
        
        # Test 7: Complete navigation
        print(f"\n7. Testing navigation completion...")
        
        complete_data = {
            'session_id': session_id,
            'current_step_index': 5,
            'status': 'completed',
            'current_latitude': destination_shop['latitude'],
            'current_longitude': destination_shop['longitude']
        }
        
        response = requests.post(f'{BASE_URL}/api/navigation/update_navigation_status/', json=complete_data, headers=headers)
        print(f"Navigation completion Status: {response.status_code}")
        
        if response.status_code == 200:
            completion_result = response.json()
            print(f"✅ Navigation completed successfully")
        else:
            print(f"❌ Navigation completion failed: {response.text}")
            
    else:
        print(f"❌ Navigation session start failed: {response.text}")

def test_geofencing(headers, market):
    """Test geofencing functionality"""
    print("\n🏗️ Testing Geofencing...")
    
    # Get geofence zones
    response = requests.get(f'{BASE_URL}/api/geofence/?market={market["id"]}', headers=headers)
    print(f"Geofence zones Status: {response.status_code}")
    
    if response.status_code == 200:
        zones = response.json()
        print(f"✅ Found {len(zones)} geofence zones")
        
        # Test zone detection
        zone_detect_data = {
            'latitude': market['latitude'],
            'longitude': market['longitude'],
            'market_id': market['id']
        }
        
        response = requests.post(f'{BASE_URL}/api/geofence/detect_zone/', json=zone_detect_data, headers=headers)
        print(f"Zone detection Status: {response.status_code}")
        
        if response.status_code == 200:
            detection_result = response.json()
            print(f"✅ Zone detection: In zone = {detection_result.get('in_zone', False)}")
        else:
            print(f"❌ Zone detection failed: {response.text}")
    else:
        print(f"❌ Failed to get geofence zones: {response.text}")

def test_indoor_navigation(headers, market):
    """Test indoor navigation functionality"""
    print("\n🏢 Testing Indoor Navigation...")
    
    indoor_data = {
        'start_x': 10.0,
        'start_y': 20.0,
        'end_x': 50.0,
        'end_y': 80.0,
        'floor': 0,
        'market_id': market['id']
    }
    
    response = requests.post(f'{BASE_URL}/api/navigation/indoor_route/', json=indoor_data, headers=headers)
    print(f"Indoor navigation Status: {response.status_code}")
    
    if response.status_code == 200:
        indoor_result = response.json()
        print(f"✅ Indoor route calculated successfully")
        print(f"   Steps: {len(indoor_result.get('steps', []))}")
    else:
        print(f"❌ Indoor navigation failed: {response.text}")

def main():
    """Run complete navigation system test"""
    print("🚀 iMarket Navigation System - Complete Test Suite")
    print("=" * 60)
    
    # Test authentication
    access_token, user_data = test_authentication()
    if not access_token:
        print("❌ Authentication failed - cannot continue tests")
        return
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Test markets and shops
    market, shops = test_markets_and_shops(headers)
    if not market:
        print("❌ Market data unavailable - cannot continue navigation tests")
        return
    
    # Test navigation workflow
    test_navigation_workflow(headers, market, shops)
    
    # Test geofencing
    test_geofencing(headers, market)
    
    # Test indoor navigation
    test_indoor_navigation(headers, market)
    
    print("\n" + "=" * 60)
    print("🎉 Navigation System Test Suite Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
