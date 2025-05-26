"""
URL configuration for iMarket project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from iMarket.views import home_view  # Import the home_view
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# Custom token views for user/seller authentication
from users.views import UserTokenObtainPairView, SellerTokenObtainPairView
from users.otp_views import OTPAuthViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name="home"),  # API homepage response
    
    # JWT Authentication endpoints - standard
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Custom authentication endpoints based on roadmap
    path('api/auth/user/register/', include('users.urls')),  # Handled by AuthViewSet.user_register
    path('api/auth/user/login/', UserTokenObtainPairView.as_view(), name='user_token_obtain'),
    path('api/auth/seller/register/', include('users.urls')),  # Handled by AuthViewSet.seller_register
    path('api/auth/seller/login/', SellerTokenObtainPairView.as_view(), name='seller_token_obtain'),
    path('api/auth/logout/', include('users.urls')),  # Handled by AuthViewSet.logout
    path('api/auth/verify-token/', TokenVerifyView.as_view(), name='token_verify'),
    
    # OTP-based Authentication endpoints
    path('api/auth/email-login/', OTPAuthViewSet.as_view({'post': 'email_login'}), name='email_login'),
    path('api/auth/phone-login/', OTPAuthViewSet.as_view({'post': 'phone_login'}), name='phone_login'),
    path('api/auth/verify-login/', OTPAuthViewSet.as_view({'post': 'verify_login'}), name='verify_login'),
    path('api/auth/request-otp/', OTPAuthViewSet.as_view({'post': 'request_otp'}), name='request_otp'),
    path('api/auth/verify-otp/', OTPAuthViewSet.as_view({'post': 'verify_otp'}), name='verify_otp'),
    path('api/auth/reset-password-request/', OTPAuthViewSet.as_view({'post': 'reset_password_request'}), name='reset_password_request'),
    path('api/auth/reset-password-verify/', OTPAuthViewSet.as_view({'post': 'reset_password_verify'}), name='reset_password_verify'),
    
    # App URLs
    path('api/users/', include('users.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/', include('markets.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
