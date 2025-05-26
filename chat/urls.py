from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, ChatMessageViewSet, SellerMessagesViewSet

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')
router.register(r'messages', ChatMessageViewSet, basename='chatmessage')
router.register(r'seller/messages', SellerMessagesViewSet, basename='seller-messages')

urlpatterns = [
    path('', include(router.urls)),
]
