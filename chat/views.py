from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from users.models import User
from django.db.models import Q
from django.utils import timezone
import uuid

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        # Create a chat room and add the current user as a participant
        chat_room = serializer.save()
        chat_room.participants.add(self.request.user)
        
        # Add other participants from the request data
        participant_ids = self.request.data.get('participants', [])
        for participant_id in participant_ids:
            if str(participant_id) != str(self.request.user.id):
                try:
                    user = User.objects.get(id=participant_id)
                    chat_room.participants.add(user)
                except User.DoesNotExist:
                    pass
    
    @action(detail=False, methods=['post'])
    def get_or_create_private_room(self, request):
        """Get or create a private chat room between the current user and another user"""
        other_user_id = request.data.get('user_id')
        
        if not other_user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if a private room already exists between these users
        rooms = ChatRoom.objects.filter(participants=request.user).filter(participants=other_user)
        
        # Filter to rooms with exactly 2 participants
        for room in rooms:
            if room.participants.count() == 2:
                serializer = self.get_serializer(room, context={'request': request})
                return Response(serializer.data)
        
        # Create a new private room if one doesn't exist
        room = ChatRoom.objects.create(name=f"Chat with {other_user.username}")
        room.participants.add(request.user, other_user)
        
        serializer = self.get_serializer(room, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatMessage.objects.filter(
            room__participants=self.request.user
        ).order_by('timestamp')
    
    def perform_create(self, serializer):
        room_id = self.request.data.get('room')
        room = get_object_or_404(ChatRoom, id=room_id, participants=self.request.user)
        serializer.save(sender=self.request.user, room=room)
    
    @action(detail=False, methods=['get'])
    def room_messages(self, request):
        """Get all messages for a specific room"""
        room_id = request.query_params.get('room_id')
        
        if not room_id:
            return Response({"error": "room_id query parameter is required"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            room = ChatRoom.objects.get(id=room_id, participants=request.user)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found or you don't have access"}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        messages = ChatMessage.objects.filter(room=room).order_by('timestamp')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """Mark all messages in a room as read"""
        room_id = request.data.get('room_id')
        
        if not room_id:
            return Response({"error": "room_id is required"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            room = ChatRoom.objects.get(id=room_id, participants=request.user)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found or you don't have access"}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        # Mark messages from others as read
        ChatMessage.objects.filter(
            room=room, 
            is_read=False
        ).exclude(
            sender=request.user
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({"status": "Messages marked as read"}, status=status.HTTP_200_OK)
