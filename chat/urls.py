from django.urls import path
from .views import ChatListCreateView, ChatDetailView

urlpatterns = [
    path('', ChatListCreateView.as_view(), name='chat-list'),
    path('<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),
]
