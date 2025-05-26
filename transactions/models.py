from django.db import models
from users.models import User
import uuid

class TransactionRecord(models.Model):
    """General transaction model"""
    TRANSACTION_TYPES = [
        ('order', 'Order Payment'),
        ('deposit', 'Deposit to Wallet'),
        ('withdrawal', 'Withdrawal from Wallet'),
        ('refund', 'Refund'),
        ('transfer', 'Transfer between Users'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='order')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # For bidirectional transactions between users
    recipient = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='received_transactions'
    )
    
    # Order relationship - will be set for order payments
    order = models.ForeignKey(
        'markets.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transactions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.transaction_type}"
        
    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"


class Wallet(models.Model):
    """User wallet for handling payments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    # Payment information
    payment_methods = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Wallet - ₦{self.balance}"
