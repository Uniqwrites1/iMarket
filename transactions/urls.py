from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, WalletViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'wallet', WalletViewSet, basename='wallet')

urlpatterns = [
    path('', include(router.urls)),
]
