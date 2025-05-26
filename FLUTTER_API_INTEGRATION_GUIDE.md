# iMarket Flutter Mobile App - Complete API Integration Guide

## 📱 Table of Contents

1. [Authentication & User Management](#authentication--user-management)
2. [Markets & Navigation](#markets--navigation)  
3. [Products & Categories](#products--categories)
4. [Orders & Transactions](#orders--transactions)
5. [Chat & Messaging](#chat--messaging)
6. [Seller Dashboard](#seller-dashboard)
7. [Flutter Integration Examples](#flutter-integration-examples)
8. [WebSocket Integration](#websocket-integration)
9. [Error Handling](#error-handling)
10. [State Management](#state-management)

---

## 🔐 Authentication & User Management

### Base URL
```
https://your-domain.com/api/
```

### 1. User Registration
```http
POST /api/auth/user/register/
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+2348012345678",
  "latitude": 6.5244,
  "longitude": 3.3792
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+2348012345678",
    "is_verified": false,
    "role": "user"
  },
  "message": "Registration successful. Please verify your email and/or phone number."
}
```

### 2. Seller Registration
```http
POST /api/auth/seller/register/
```

**Request Body:**
```json
{
  "username": "shop_owner",
  "email": "seller@example.com",
  "password": "securePassword123",
  "first_name": "Shop",
  "last_name": "Owner",
  "phone_number": "+2348012345678",
  "business_name": "John's Electronics Store",
  "business_description": "Electronics and gadgets",
  "shop_number": "A15",
  "market": 1
}
```

### 3. User Login
```http
POST /api/auth/user/login/
```

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

### 4. Seller Login
```http
POST /api/auth/seller/login/
```

### 5. OTP-Based Authentication

#### Request OTP
```http
POST /api/auth/request-otp/
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "verification_type": "email"
}
```

#### Verify OTP
```http
POST /api/auth/verify-otp/
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp_code": "123456",
  "verification_type": "email"
}
```

#### Email Login (OTP)
```http
POST /api/auth/email-login/
```

#### Phone Login (OTP)
```http
POST /api/auth/phone-login/
```

### 6. Password Reset

#### Request Password Reset
```http
POST /api/auth/reset-password-request/
```

#### Verify Password Reset
```http
POST /api/auth/reset-password-verify/
```

### 7. User Profile Management

#### Get Current User
```http
GET /api/users/me/
Authorization: Bearer <access_token>
```

#### Update Profile
```http
PUT /api/users/me/
Authorization: Bearer <access_token>
```

#### Change Password
```http
POST /api/users/change_password/
Authorization: Bearer <access_token>
```

#### Verify Email
```http
POST /api/users/verify_email/
Authorization: Bearer <access_token>
```

#### Verify Phone
```http
POST /api/users/verify_phone/
Authorization: Bearer <access_token>
```

---

## 🏪 Markets & Navigation

### 1. Markets

#### List All Markets
```http
GET /api/markets/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Computer Village",
    "address": "Ikeja, Lagos",
    "city": "Lagos",
    "state": "Lagos",
    "latitude": 6.5244,
    "longitude": 3.3792,
    "description": "Electronics market",
    "is_active": true
  }
]
```

#### Get Market Details
```http
GET /api/markets/{id}/
```

#### Get Market Map
```http
GET /api/markets/{id}/map/
```

#### Search Market by Location
```http
GET /api/markets/pin_search/?lat=6.5244&lng=3.3792
```

#### Get Market Sellers
```http
GET /api/markets/{id}/sellers/
```

#### Get Market Shops
```http
GET /api/markets/{id}/shops/
Authorization: Bearer <access_token>
```

#### Get Navigation Info
```http
GET /api/markets/{id}/navigation_info/
Authorization: Bearer <access_token>
```

#### Check Indoor Location
```http
POST /api/markets/{id}/check_indoor_location/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "latitude": 6.5244,
  "longitude": 3.3792
}
```

### 2. Shops

#### List Shops
```http
GET /api/shops/
```

#### Get Shop Details
```http
GET /api/shops/{id}/
```

#### Find Nearby Shops
```http
POST /api/shops/nearby/
```

**Request Body:**
```json
{
  "latitude": 6.5244,
  "longitude": 3.3792,
  "market_id": 1,
  "radius_meters": 100
}
```

#### Calculate Route to Shop
```http
POST /api/shops/{id}/route_to/
```

**Request Body:**
```json
{
  "start_latitude": 6.5244,
  "start_longitude": 3.3792,
  "navigation_mode": "walking"
}
```

### 3. Navigation

#### Start Navigation
```http
POST /api/navigation/start_navigation/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "start_latitude": 6.5244,
  "start_longitude": 3.3792,
  "destination_shop_id": 1,
  "navigation_mode": "walking",
  "use_indoor_navigation": true
}
```

#### Update Location
```http
POST /api/navigation/update_location/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "latitude": 6.5244,
  "longitude": 3.3792,
  "market_id": 1,
  "accuracy": 5.0,
  "altitude": 10.0,
  "heading": 45.0,
  "speed": 1.5
}
```

#### Get Active Session
```http
GET /api/navigation/active_session/
Authorization: Bearer <access_token>
```

#### Indoor Route Calculation
```http
POST /api/navigation/indoor_route/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "start_x": 10.0,
  "start_y": 20.0,
  "end_x": 50.0,
  "end_y": 60.0,
  "floor": 1,
  "market_id": "1"
}
```

---

## 🛍️ Products & Categories

### 1. Categories

#### List Categories
```http
GET /api/categories/
```

#### Get Category Details
```http
GET /api/categories/{id}/
```

#### Get Products in Category
```http
GET /api/categories/{id}/products/
```

### 2. Products

#### List Products
```http
GET /api/products/
```

**Query Parameters:**
- `search`: Search by name, description, seller
- `page`: Pagination

#### Get Product Details
```http
GET /api/products/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "iPhone 14 Pro",
  "description": "Latest iPhone model",
  "price": "450000.00",
  "category": {
    "id": 1,
    "name": "Smartphones"
  },
  "seller": {
    "id": 1,
    "username": "shop_owner",
    "business_name": "John's Electronics"
  },
  "market": {
    "id": 1,
    "name": "Computer Village"
  },
  "images": [
    {
      "id": 1,
      "image": "https://domain.com/media/products/iphone.jpg",
      "is_primary": true
    }
  ],
  "is_available": true,
  "stock_quantity": 10,
  "created_at": "2025-05-26T10:00:00Z"
}
```

---

## 🛒 Orders & Transactions

### 1. Orders

#### List User Orders
```http
GET /api/orders/
Authorization: Bearer <access_token>
```

#### Create Order
```http
POST /api/orders/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "seller": 1,
  "items": [
    {
      "product": 1,
      "quantity": 2,
      "price": "450000.00"
    }
  ],
  "delivery_address": "123 Main Street, Lagos",
  "notes": "Please call when you arrive"
}
```

### 2. Transactions

#### List Transactions
```http
GET /api/transactions/transactions/
Authorization: Bearer <access_token>
```

#### Get Wallet Info
```http
GET /api/transactions/wallet/
Authorization: Bearer <access_token>
```

### 3. User Wallet

#### Get Wallet Balance
```http
GET /api/users/wallet/wallet/
Authorization: Bearer <access_token>
```

#### Get Transaction History
```http
GET /api/users/wallet/transactions/
Authorization: Bearer <access_token>
```

#### Fund Wallet
```http
POST /api/users/wallet/fund/
Authorization: Bearer <access_token>
```

---

## 💬 Chat & Messaging

### 1. Chat Rooms

#### List Chat Rooms
```http
GET /api/chat/rooms/
Authorization: Bearer <access_token>
```

#### Create Chat Room
```http
POST /api/chat/rooms/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Chat with John's Electronics",
  "participants": [1, 2]
}
```

### 2. Messages

#### List Messages
```http
GET /api/chat/messages/
Authorization: Bearer <access_token>
```

#### Send Message
```http
POST /api/chat/messages/
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "room": 1,
  "content": "Hello, is this product available?",
  "message_type": "text"
}
```

### 3. Seller Messages

#### Get Seller Conversations
```http
GET /api/chat/seller/messages/conversations/
Authorization: Bearer <seller_access_token>
```

#### Get User Conversation
```http
GET /api/chat/seller/messages/{user_id}/user_conversation/
Authorization: Bearer <seller_access_token>
```

#### Send Message to User
```http
POST /api/chat/seller/messages/{user_id}/send_message/
Authorization: Bearer <seller_access_token>
```

---

## 💼 Seller Dashboard

### 1. Profile Management

#### Get/Update Seller Profile
```http
GET /api/seller/profile/
PUT /api/seller/profile/
Authorization: Bearer <seller_access_token>
```

#### Upload Verification Documents
```http
POST /api/seller/verify_docs/
Authorization: Bearer <seller_access_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `id_document`: File
- `cac_document`: File
- `store_photos`: File[]

### 2. Products Management

#### Get Seller Products
```http
GET /api/seller/products/
Authorization: Bearer <seller_access_token>
```

#### Create Product
```http
POST /api/products/
Authorization: Bearer <seller_access_token>
```

### 3. Orders Management

#### Get Seller Orders
```http
GET /api/seller/orders/
Authorization: Bearer <seller_access_token>
```

**Query Parameters:**
- `status`: Filter by order status

#### Update Order Status
```http
PUT /api/seller/orders/{id}/update_order/
Authorization: Bearer <seller_access_token>
```

**Request Body:**
```json
{
  "status": "confirmed",
  "seller_note": "Order confirmed and will be ready in 2 hours"
}
```

### 4. Analytics & Earnings

#### Get Analytics
```http
GET /api/seller/analytics/
Authorization: Bearer <seller_access_token>
```

#### Get Earnings
```http
GET /api/seller/earnings/
Authorization: Bearer <seller_access_token>
```

#### Get Wallet Details
```http
GET /api/seller/wallet/
Authorization: Bearer <seller_access_token>
```

#### Request Withdrawal
```http
POST /api/seller/withdraw/
Authorization: Bearer <seller_access_token>
```

**Request Body:**
```json
{
  "amount": "50000.00"
}
```

### 5. Admin Endpoints

#### Get Pending Sellers
```http
GET /api/admin/sellers/pending/
Authorization: Bearer <admin_access_token>
```

#### Approve Seller
```http
POST /api/admin/sellers/{id}/approve/
Authorization: Bearer <admin_access_token>
```

#### Reject Seller
```http
POST /api/admin/sellers/{id}/reject/
Authorization: Bearer <admin_access_token>
```

---

## 🏠 Home & Highlights

### Get Home Page Data
```http
GET /api/home/highlights/
```

**Response:**
```json
{
  "featured_sellers": [...],
  "featured_products": [...],
  "categories": [...],
  "markets": [...]
}
```

---

## 📱 Flutter Integration Examples

### 1. Setup HTTP Client

```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'https://your-domain.com/api';
  
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }
  
  static Future<Map<String, String>> getHeaders({bool requireAuth = true}) async {
    Map<String, String> headers = {
      'Content-Type': 'application/json',
    };
    
    if (requireAuth) {
      final token = await getToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    
    return headers;
  }
  
  static Future<http.Response> get(String endpoint, {bool requireAuth = true}) async {
    final headers = await getHeaders(requireAuth: requireAuth);
    return await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
    );
  }
  
  static Future<http.Response> post(String endpoint, Map<String, dynamic> data, {bool requireAuth = true}) async {
    final headers = await getHeaders(requireAuth: requireAuth);
    return await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: jsonEncode(data),
    );
  }
  
  static Future<http.Response> put(String endpoint, Map<String, dynamic> data, {bool requireAuth = true}) async {
    final headers = await getHeaders(requireAuth: requireAuth);
    return await http.put(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: jsonEncode(data),
    );
  }
}
```

### 2. Authentication Service

```dart
// lib/services/auth_service.dart
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class AuthService {
  static Future<Map<String, dynamic>> registerUser(Map<String, dynamic> userData) async {
    final response = await ApiService.post('/auth/user/register/', userData, requireAuth: false);
    
    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      await _saveTokens(data['access'], data['refresh']);
      return {'success': true, 'user': data['user']};
    } else {
      final error = jsonDecode(response.body);
      return {'success': false, 'error': error};
    }
  }
  
  static Future<Map<String, dynamic>> loginUser(String username, String password) async {
    final response = await ApiService.post('/auth/user/login/', {
      'username': username,
      'password': password,
    }, requireAuth: false);
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _saveTokens(data['access'], data['refresh']);
      return {'success': true, 'tokens': data};
    } else {
      final error = jsonDecode(response.body);
      return {'success': false, 'error': error};
    }
  }
  
  static Future<bool> requestOTP(String email) async {
    final response = await ApiService.post('/auth/request-otp/', {
      'email': email,
      'verification_type': 'email',
    }, requireAuth: false);
    
    return response.statusCode == 200;
  }
  
  static Future<bool> verifyOTP(String email, String otpCode) async {
    final response = await ApiService.post('/auth/verify-otp/', {
      'email': email,
      'otp_code': otpCode,
      'verification_type': 'email',
    }, requireAuth: false);
    
    return response.statusCode == 200;
  }
  
  static Future<void> _saveTokens(String accessToken, String refreshToken) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', accessToken);
    await prefs.setString('refresh_token', refreshToken);
  }
  
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
  }
  
  static Future<bool> isLoggedIn() async {
    final token = await ApiService.getToken();
    return token != null;
  }
}
```

### 3. Market Service

```dart
// lib/services/market_service.dart
import 'dart:convert';
import 'api_service.dart';

class MarketService {
  static Future<List<dynamic>> getMarkets() async {
    final response = await ApiService.get('/markets/', requireAuth: false);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load markets');
  }
  
  static Future<Map<String, dynamic>> getMarketDetails(int marketId) async {
    final response = await ApiService.get('/markets/$marketId/', requireAuth: false);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load market details');
  }
  
  static Future<Map<String, dynamic>> searchMarketByLocation(double lat, double lng) async {
    final response = await ApiService.get('/markets/pin_search/?lat=$lat&lng=$lng', requireAuth: false);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('No markets found near this location');
  }
  
  static Future<List<dynamic>> getNearbyShops(double lat, double lng, int marketId, {int radius = 100}) async {
    final response = await ApiService.post('/shops/nearby/', {
      'latitude': lat,
      'longitude': lng,
      'market_id': marketId,
      'radius_meters': radius,
    });
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['shops'];
    }
    throw Exception('Failed to find nearby shops');
  }
}
```

### 4. Navigation Service

```dart
// lib/services/navigation_service.dart
import 'dart:convert';
import 'api_service.dart';

class NavigationService {
  static Future<Map<String, dynamic>> startNavigation({
    required double startLat,
    required double startLng,
    int? shopId,
    double? destLat,
    double? destLng,
    String mode = 'walking',
    bool useIndoor = true,
  }) async {
    Map<String, dynamic> requestData = {
      'start_latitude': startLat,
      'start_longitude': startLng,
      'navigation_mode': mode,
      'use_indoor_navigation': useIndoor,
    };
    
    if (shopId != null) {
      requestData['destination_shop_id'] = shopId;
    } else if (destLat != null && destLng != null) {
      requestData['destination_latitude'] = destLat;
      requestData['destination_longitude'] = destLng;
    }
    
    final response = await ApiService.post('/navigation/start_navigation/', requestData);
    
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to start navigation');
  }
  
  static Future<void> updateLocation(double lat, double lng, int marketId) async {
    await ApiService.post('/navigation/update_location/', {
      'latitude': lat,
      'longitude': lng,
      'market_id': marketId,
    });
  }
  
  static Future<Map<String, dynamic>?> getActiveSession() async {
    final response = await ApiService.get('/navigation/active_session/');
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }
}
```

### 5. Product Service

```dart
// lib/services/product_service.dart
import 'dart:convert';
import 'api_service.dart';

class ProductService {
  static Future<List<dynamic>> getProducts({String? search, int page = 1}) async {
    String endpoint = '/products/?page=$page';
    if (search != null && search.isNotEmpty) {
      endpoint += '&search=$search';
    }
    
    final response = await ApiService.get(endpoint, requireAuth: false);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load products');
  }
  
  static Future<Map<String, dynamic>> getProductDetails(int productId) async {
    final response = await ApiService.get('/products/$productId/', requireAuth: false);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load product details');
  }
  
  static Future<List<dynamic>> getCategories() async {
    final response = await ApiService.get('/categories/', requireAuth: false);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load categories');
  }
  
  static Future<List<dynamic>> getCategoryProducts(int categoryId) async {
    final response = await ApiService.get('/categories/$categoryId/products/', requireAuth: false);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load category products');
  }
}
```

### 6. Order Service

```dart
// lib/services/order_service.dart
import 'dart:convert';
import 'api_service.dart';

class OrderService {
  static Future<List<dynamic>> getUserOrders() async {
    final response = await ApiService.get('/orders/');
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load orders');
  }
  
  static Future<Map<String, dynamic>> createOrder(Map<String, dynamic> orderData) async {
    final response = await ApiService.post('/orders/', orderData);
    
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to create order');
  }
}
```

### 7. Chat Service

```dart
// lib/services/chat_service.dart
import 'dart:convert';
import 'api_service.dart';

class ChatService {
  static Future<List<dynamic>> getChatRooms() async {
    final response = await ApiService.get('/chat/rooms/');
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load chat rooms');
  }
  
  static Future<List<dynamic>> getMessages(int roomId) async {
    final response = await ApiService.get('/chat/messages/?room=$roomId');
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load messages');
  }
  
  static Future<Map<String, dynamic>> sendMessage(int roomId, String content) async {
    final response = await ApiService.post('/chat/messages/', {
      'room': roomId,
      'content': content,
      'message_type': 'text',
    });
    
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to send message');
  }
}
```

---

## 🔌 WebSocket Integration

### WebSocket URLs
```
wss://your-domain.com/ws/chat/{room_id}/
wss://your-domain.com/ws/navigation/{user_id}/
```

### Flutter WebSocket Implementation

```dart
// lib/services/websocket_service.dart
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  
  void connectToChat(int roomId, String token) {
    _channel = WebSocketChannel.connect(
      Uri.parse('wss://your-domain.com/ws/chat/$roomId/?token=$token'),
    );
    
    _channel!.stream.listen((message) {
      final data = jsonDecode(message);
      _handleChatMessage(data);
    });
  }
  
  void connectToNavigation(int userId, String token) {
    _channel = WebSocketChannel.connect(
      Uri.parse('wss://your-domain.com/ws/navigation/$userId/?token=$token'),
    );
    
    _channel!.stream.listen((message) {
      final data = jsonDecode(message);
      _handleNavigationUpdate(data);
    });
  }
  
  void sendChatMessage(String message) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode({
        'message': message,
        'type': 'chat_message',
      }));
    }
  }
  
  void sendLocationUpdate(double lat, double lng) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode({
        'type': 'location_update',
        'latitude': lat,
        'longitude': lng,
      }));
    }
  }
  
  void _handleChatMessage(Map<String, dynamic> data) {
    // Handle incoming chat messages
    print('New chat message: ${data['message']}');
  }
  
  void _handleNavigationUpdate(Map<String, dynamic> data) {
    // Handle navigation updates
    print('Navigation update: $data');
  }
  
  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }
}
```

---

## ❌ Error Handling

### Standard Error Response Format
```json
{
  "error": "Error description",
  "details": "Detailed error information",
  "field_errors": {
    "field_name": ["Field-specific error message"]
  }
}
```

### Flutter Error Handling
```dart
// lib/utils/error_handler.dart
class ErrorHandler {
  static String getErrorMessage(Map<String, dynamic> errorResponse) {
    if (errorResponse.containsKey('error')) {
      return errorResponse['error'];
    }
    
    if (errorResponse.containsKey('detail')) {
      return errorResponse['detail'];
    }
    
    if (errorResponse.containsKey('field_errors')) {
      final fieldErrors = errorResponse['field_errors'] as Map<String, dynamic>;
      final firstError = fieldErrors.values.first;
      if (firstError is List && firstError.isNotEmpty) {
        return firstError.first.toString();
      }
    }
    
    return 'An unexpected error occurred';
  }
}
```

---

## 🗂️ State Management

### Using Provider for State Management

```dart
// lib/providers/auth_provider.dart
import 'package:flutter/foundation.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  bool _isLoggedIn = false;
  Map<String, dynamic>? _user;
  bool _isLoading = false;
  
  bool get isLoggedIn => _isLoggedIn;
  Map<String, dynamic>? get user => _user;
  bool get isLoading => _isLoading;
  
  Future<void> checkAuthStatus() async {
    _isLoading = true;
    notifyListeners();
    
    _isLoggedIn = await AuthService.isLoggedIn();
    
    _isLoading = false;
    notifyListeners();
  }
  
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    notifyListeners();
    
    final result = await AuthService.loginUser(username, password);
    
    if (result['success']) {
      _isLoggedIn = true;
      _user = result['user'];
    }
    
    _isLoading = false;
    notifyListeners();
    
    return result['success'];
  }
  
  Future<void> logout() async {
    await AuthService.logout();
    _isLoggedIn = false;
    _user = null;
    notifyListeners();
  }
}
```

### Using the Provider

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        // Add other providers here
      ],
      child: MyApp(),
    ),
  );
}

// In your widgets
class LoginScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        if (authProvider.isLoading) {
          return CircularProgressIndicator();
        }
        
        return LoginForm();
      },
    );
  }
}
```

---

## 📦 Required Flutter Dependencies

Add these to your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # HTTP requests
  http: ^1.1.0
  
  # Local storage
  shared_preferences: ^2.2.2
  
  # State management
  provider: ^6.1.1
  
  # WebSocket
  web_socket_channel: ^2.4.0
  
  # Location services
  geolocator: ^10.1.0
  location: ^5.0.3
  
  # Maps
  google_maps_flutter: ^2.5.0
  
  # Image handling
  image_picker: ^1.0.4
  cached_network_image: ^3.3.0
  
  # JSON handling
  json_annotation: ^4.8.1
  
  # File upload
  dio: ^5.3.3
  
  # Permission handling
  permission_handler: ^11.0.1
```

---

## 🚀 Getting Started

1. **Setup API Base URL**: Update the `baseUrl` in `ApiService`
2. **Configure Authentication**: Implement login/logout flow
3. **Handle Permissions**: Request location, camera, storage permissions
4. **Setup Maps**: Configure Google Maps API key
5. **Test API Calls**: Start with basic endpoints
6. **Implement WebSocket**: For real-time features
7. **Add Error Handling**: Implement comprehensive error handling
8. **Setup State Management**: Use Provider or Riverpod

This comprehensive guide provides all the API endpoints and Flutter integration examples needed to build the iMarket mobile app! 🎉
