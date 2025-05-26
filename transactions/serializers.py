from rest_framework import serializers
from .models import TransactionRecord, Wallet
from users.serializers import UserDetailSerializer

class TransactionSerializer(serializers.ModelSerializer):
    user_details = UserDetailSerializer(source='user', read_only=True)
    recipient_details = UserDetailSerializer(source='recipient', read_only=True)
    
    class Meta:
        model = TransactionRecord
        fields = [
            'id', 'user', 'user_details', 'amount', 'transaction_type',
            'status', 'reference', 'description', 'recipient', 
            'recipient_details', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WalletSerializer(serializers.ModelSerializer):
    user_details = UserDetailSerializer(source='user', read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'user_details', 'balance', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance', 'is_active', 'created_at', 'updated_at']


class WalletFundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.CharField(max_length=50)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

