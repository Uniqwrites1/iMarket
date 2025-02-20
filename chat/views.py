from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatListCreateView(generics.ListCreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

class ChatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
