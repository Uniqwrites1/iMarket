from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuthViewSet, UserWalletViewSet
from .otp_views import OTPAuthViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'wallet', UserWalletViewSet, basename='wallet')
router.register(r'otp', OTPAuthViewSet, basename='otp')

urlpatterns = [
    path('', include(router.urls)),
]

