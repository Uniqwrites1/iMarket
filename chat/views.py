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

# Import seller permission from markets app
from markets.views import IsSellerPermission

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


class SellerMessagesViewSet(viewsets.ViewSet):
    """API endpoints for seller messages"""
    permission_classes = [IsSellerPermission]
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Get all conversations initiated by users for this seller"""
        seller = request.user
        
        # Get chat rooms where this seller is a participant
        chat_rooms = ChatRoom.objects.filter(participants=seller)
        
        # Only get rooms with exactly 2 participants (private chats)
        private_rooms = []
        for room in chat_rooms:
            if room.participants.count() == 2:
                private_rooms.append(room)
        
        # Serialize the rooms with additional info about the other participant
        result = []
        for room in private_rooms:
            # Get the other participant (not the seller)
            other_user = room.participants.exclude(id=seller.id).first()
            
            if other_user:
                # Get the latest message
                latest_message = ChatMessage.objects.filter(room=room).order_by('-timestamp').first()
                
                # Count unread messages
                unread_count = ChatMessage.objects.filter(
                    room=room,
                    sender=other_user,
                    is_read=False
                ).count()
                
                result.append({
                    'room_id': room.id,
                    'user': {
                        'id': other_user.id,
                        'username': other_user.username,
                        'first_name': other_user.first_name,
                        'last_name': other_user.last_name,
                        'profile_picture': request.build_absolute_uri(other_user.profile_picture.url) if other_user.profile_picture else None
                    },
                    'last_message': ChatMessageSerializer(latest_message).data if latest_message else None,
                    'unread_count': unread_count
                })
        
        # Sort by latest message time
        result.sort(key=lambda x: x.get('last_message', {}).get('timestamp', ''), reverse=True)
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def user_conversation(self, request, pk=None):
        """Get conversation with a specific user"""
        seller = request.user
        
        try:
            user = User.objects.get(pk=pk, role=User.ROLE_USER)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Find a chat room between these users, or create one
        chat_rooms = ChatRoom.objects.filter(participants=seller).filter(participants=user)
        
        # Filter to rooms with exactly 2 participants
        room = None
        for candidate in chat_rooms:
            if candidate.participants.count() == 2:
                room = candidate
                break
        
        # Create a new room if one doesn't exist
        if room is None:
            room = ChatRoom.objects.create(name=f"Chat with {user.username}")
            room.participants.add(seller, user)
        
        # Get all messages
        messages = ChatMessage.objects.filter(room=room).order_by('timestamp')
        
        # Mark messages as read
        ChatMessage.objects.filter(
            room=room, 
            sender=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        room_data = ChatRoomSerializer(room).data
        messages_data = ChatMessageSerializer(messages, many=True).data
        
        return Response({
            'room': room_data,
            'messages': messages_data,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to a specific user"""
        seller = request.user
        content = request.data.get('content')
        
        if not content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(pk=pk, role=User.ROLE_USER)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Find a chat room between these users, or create one
        chat_rooms = ChatRoom.objects.filter(participants=seller).filter(participants=user)
        
        # Filter to rooms with exactly 2 participants
        room = None
        for candidate in chat_rooms:
            if candidate.participants.count() == 2:
                room = candidate
                break
        
        # Create a new room if one doesn't exist
        if room is None:
            room = ChatRoom.objects.create(name=f"Chat with {user.username}")
            room.participants.add(seller, user)
        
        # Create the message
        message = ChatMessage.objects.create(
            room=room,
            sender=seller,
            content=content
        )
        
        return Response(ChatMessageSerializer(message).data)
