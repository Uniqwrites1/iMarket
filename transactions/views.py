from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TransactionRecord, Wallet
from .serializers import (
    TransactionSerializer, WalletSerializer, 
    WalletFundSerializer
)
from django.db.models import Sum
from django.db import transaction
from django.shortcuts import get_object_or_404
from users.models import User


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Wallet.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get current user's wallet balance"""
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        return Response({
            "balance": wallet.balance,
            "user_id": request.user.id,
            "username": request.user.username
        })
    
    @action(detail=False, methods=['post'])
    def fund(self, request):
        """Add funds to wallet"""
        serializer = WalletFundSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        amount = serializer.validated_data['amount']
        payment_method = serializer.validated_data['payment_method']
        
        # Get or create wallet
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        # In a real app, you'd integrate with a payment gateway here
        # For now, we'll just create a transaction record and update the balance
        
        with transaction.atomic():
            # Create the transaction
            transaction_obj = TransactionRecord.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='deposit',
                status='completed',
                description=f"Wallet funding via {payment_method}",
                reference=f"FUND-{request.user.id}-{amount}"
            )
            
            # Update wallet balance
            wallet.balance += amount
            wallet.save()
        
        return Response({
            "message": "Wallet funded successfully",
            "transaction_id": transaction_obj.id,
            "new_balance": wallet.balance
        })


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """View and list transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return TransactionRecord.objects.filter(user=user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary for current user"""
        user = request.user
        transactions = TransactionRecord.objects.filter(user=user)
        
        # Calculate summary statistics
        deposits = transactions.filter(transaction_type='deposit').aggregate(total=Sum('amount'))
        withdrawals = transactions.filter(transaction_type='withdrawal').aggregate(total=Sum('amount'))
        orders = transactions.filter(transaction_type='order').aggregate(total=Sum('amount'))
        
        return Response({
            "deposits": deposits['total'] or 0,
            "withdrawals": withdrawals['total'] or 0,
            "orders": orders['total'] or 0,
            "transaction_count": transactions.count(),
        })
