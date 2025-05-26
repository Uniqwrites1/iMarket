from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import logout
from .models import User, OTPVerification
from .serializers import (
    UserSerializer, UserDetailSerializer, 
    SellerSerializer, SellerDetailSerializer,
    OTPVerifySerializer
)
from .utils import generate_otp, send_email_otp, send_phone_otp
from markets.views import IsSellerPermission, IsBuyerPermission


class UserTokenObtainPairView(TokenObtainPairView):
    """Login for users"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                
                # Ensure this is a user, not a seller
                if user.role != User.ROLE_USER:
                    return Response({
                        'error': 'Invalid credentials for user login'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Add user data to response
                response.data['user'] = UserDetailSerializer(user).data
                
            except User.DoesNotExist:
                pass
                
        return response


class SellerTokenObtainPairView(TokenObtainPairView):
    """Login for sellers"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                
                # Ensure this is a seller
                if user.role != User.ROLE_SELLER:
                    return Response({
                        'error': 'Invalid credentials for seller login'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if seller is verified
                if not user.is_verified:
                    refresh_token = response.data.get('refresh')
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                    
                    return Response({
                        'error': 'Your seller account is pending verification',
                        'status': user.verification_status
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Add seller data to response
                response.data['seller'] = SellerDetailSerializer(user).data
                
            except User.DoesNotExist:
                pass
                
        return response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return UserSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current authenticated user's details"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """Verify user email with verification code"""
        otp_code = request.data.get('otp_code')
        
        if not otp_code:
            return Response({"error": "Verification code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find OTP verification record
        try:
            otp_record = OTPVerification.objects.filter(
                user=request.user,
                email=request.user.email,
                otp_code=otp_code,
                verification_type=OTPVerification.TYPE_EMAIL,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not otp_record:
                return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_record.is_expired:
                return Response({"error": "Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark as verified
            otp_record.is_verified = True
            otp_record.save()
            
            # Update user
            request.user.email_verified = True
            if request.user.phone_verified or not request.user.phone_number:
                request.user.is_verified = True
            request.user.save()
            
            return Response({"message": "Email verification successful"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": f"Verification failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def verify_phone(self, request):
        """Verify user phone number with verification code"""
        otp_code = request.data.get('otp_code')
        
        if not otp_code:
            return Response({"error": "Verification code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find OTP verification record
        try:
            otp_record = OTPVerification.objects.filter(
                user=request.user,
                phone_number=request.user.phone_number,
                otp_code=otp_code,
                verification_type=OTPVerification.TYPE_PHONE,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not otp_record:
                return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_record.is_expired:
                return Response({"error": "Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark as verified
            otp_record.is_verified = True
            otp_record.save()
            
            # Update user
            request.user.phone_verified = True
            if request.user.email_verified:
                request.user.is_verified = True
            request.user.save()
            
            return Response({"message": "Phone verification successful"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": f"Verification failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response({"error": "Invalid old password"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints for users and sellers"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def user_register(self, request):
        """Register user account"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Create the user but don't mark as verified yet
                user = serializer.save()
                user.role = User.ROLE_USER
                user.is_verified = False
                user.save()
                
                # Generate OTP codes for verification
                # Send email OTP if email provided
                if user.email:
                    email_otp = generate_otp()
                    OTPVerification.objects.create(
                        user=user,
                        email=user.email,
                        otp_code=email_otp,
                        verification_type=OTPVerification.TYPE_EMAIL
                    )
                    send_email_otp(user.email, email_otp, OTPVerification.TYPE_EMAIL)
                
                # Send phone OTP if phone provided
                if user.phone_number:
                    phone_otp = generate_otp()
                    OTPVerification.objects.create(
                        user=user,
                        phone_number=user.phone_number,
                        otp_code=phone_otp,
                        verification_type=OTPVerification.TYPE_PHONE
                    )
                    send_phone_otp(user.phone_number, phone_otp)
                
                # Generate token for immediate access
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserDetailSerializer(user).data,
                    'message': 'Registration successful. Please verify your email and/or phone number.'
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def seller_register(self, request):
        """Register seller account"""
        serializer = SellerSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Create the user, SellerSerializer sets role to SELLER
                user = serializer.save()
                user.is_verified = False
                user.save()
                
                # Generate OTP codes for verification
                # Send email OTP if email provided
                if user.email:
                    email_otp = generate_otp()
                    OTPVerification.objects.create(
                        user=user,
                        email=user.email,
                        otp_code=email_otp,
                        verification_type=OTPVerification.TYPE_EMAIL
                    )
                    send_email_otp(user.email, email_otp, OTPVerification.TYPE_EMAIL)
                
                # Send phone OTP if phone provided
                if user.phone_number:
                    phone_otp = generate_otp()
                    OTPVerification.objects.create(
                        user=user,
                        phone_number=user.phone_number,
                        otp_code=phone_otp,
                        verification_type=OTPVerification.TYPE_PHONE
                    )
                    send_phone_otp(user.phone_number, phone_otp)
            
                return Response({
                    'message': 'Seller registration successful. Please verify your email and/or phone number. Your account is also pending admin verification.',
                    'user': SellerDetailSerializer(user).data
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout current session"""
        if request.user.is_authenticated:
            # Blacklist the token
            try:
                refresh_token = request.data["refresh"]
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)


class UserWalletViewSet(viewsets.ViewSet):
    """User wallet endpoints"""
    permission_classes = [IsAuthenticated, IsBuyerPermission]
    
    @action(detail=False, methods=['get'])
    def wallet(self, request):
        """View wallet balance"""
        # In a real app, you'd have a user wallet model
        # For now, we'll just return a placeholder
        return Response({
            "balance": 0.0,
            "message": "User wallet functionality will be implemented in future phases."
        })
    
    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """List of past transactions"""
        # Placeholder for future implementation
        return Response({
            "transactions": [],
            "message": "Transaction history will be implemented in future phases."
        })
    
    @action(detail=False, methods=['post'])
    def fund(self, request):
        """Add funds to wallet"""
        # Placeholder for future implementation
        return Response({
            "message": "Wallet funding will be implemented in future phases."
        })
