from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MarketViewSet, CategoryViewSet, ProductViewSet,
    SellerDashboardViewSet, UserOrderViewSet, HomeViewSet,
    AdminSellerViewSet, ShopViewSet, NavigationViewSet
)

router = DefaultRouter()
router.register(r'markets', MarketViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'seller', SellerDashboardViewSet, basename='seller')
router.register(r'orders', UserOrderViewSet, basename='order')
router.register(r'home', HomeViewSet, basename='home')
router.register(r'admin/sellers', AdminSellerViewSet, basename='admin-sellers')
router.register(r'shops', ShopViewSet, basename='shops')
router.register(r'navigation', NavigationViewSet, basename='navigation')

urlpatterns = [
    path('', include(router.urls)),
]
