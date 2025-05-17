import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
from users.models import User
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = data['message']
            sender_id = data['sender_id']
            
            # Save message to database
            message_data = await self.save_message(sender_id, message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id,
                    'timestamp': message_data['timestamp'].isoformat(),
                    'message_id': str(message_data['id'])
                }
            )
        elif message_type == 'read_messages':
            sender_id = data['sender_id']
            await self.mark_messages_as_read(sender_id)
            
            # Notify other users that messages have been read
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user_id': sender_id,
                }
            )
    
    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))
    
    # Receive read notification from room group
    async def messages_read(self, event):
        # Send read notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'user_id': event['user_id'],
        }))
    
    @database_sync_to_async
    def save_message(self, sender_id, content):
        sender = User.objects.get(id=sender_id)
        room = ChatRoom.objects.get(id=self.room_id)
        message = ChatMessage.objects.create(
            room=room,
            sender=sender,
            content=content
        )
        return {'id': message.id, 'timestamp': message.timestamp}
    
    @database_sync_to_async
    def mark_messages_as_read(self, user_id):
        user = User.objects.get(id=user_id)
        room = ChatRoom.objects.get(id=self.room_id)
        now = timezone.now()
        
        # Mark all unread messages sent by others as read
        ChatMessage.objects.filter(
            room=room,
            is_read=False
        ).exclude(
            sender=user
        ).update(
            is_read=True,
            read_at=now
        )
