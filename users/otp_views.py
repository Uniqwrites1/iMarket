from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .models import User, OTPVerification
from .serializers import (
    OTPRequestSerializer, OTPVerifySerializer,
    EmailLoginSerializer, PhoneLoginSerializer, OTPLoginSerializer,
    UserDetailSerializer
)
from .utils import generate_otp, send_email_otp, send_phone_otp


class OTPAuthViewSet(viewsets.ViewSet):
    """OTP-based authentication views"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def request_otp(self, request):
        """Request an OTP via email or phone"""
        serializer = OTPRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get('email')
        phone_number = serializer.validated_data.get('phone_number')
        verification_type = serializer.validated_data['verification_type']
        
        # Generate OTP
        otp_code = generate_otp()
        
        # Find the user if it exists (for login or password reset)
        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                if verification_type in [OTPVerification.TYPE_PASSWORD_RESET, OTPVerification.TYPE_LOGIN]:
                    return Response(
                        {"error": "No user found with this email address"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                # For registration, this is fine
        
        if phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                if verification_type in [OTPVerification.TYPE_PASSWORD_RESET, OTPVerification.TYPE_LOGIN]:
                    return Response(
                        {"error": "No user found with this phone number"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                # For registration, this is fine
        
        # Create OTP verification record
        otp_record = OTPVerification.objects.create(
            user=user,
            email=email,
            phone_number=phone_number,
            otp_code=otp_code,
            verification_type=verification_type
        )
        
        # Send OTP
        success = False
        if email:
            success = send_email_otp(email, otp_code, verification_type)
        elif phone_number:
            success = send_phone_otp(phone_number, otp_code)
        
        if not success:
            return Response(
                {"error": "Failed to send verification code. Please try again later."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            "message": f"Verification code sent to {'email' if email else 'phone'}",
            "verification_id": str(otp_record.id)
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        """Verify an OTP code"""
        serializer = OTPVerifySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get('email')
        phone_number = serializer.validated_data.get('phone_number')
        otp_code = serializer.validated_data['otp_code']
        verification_type = serializer.validated_data['verification_type']
        
        # Find the OTP record
        filter_kwargs = {
            'verification_type': verification_type,
            'otp_code': otp_code,
            'is_verified': False
        }
        
        if email:
            filter_kwargs['email'] = email
        elif phone_number:
            filter_kwargs['phone_number'] = phone_number
        
        try:
            otp_record = OTPVerification.objects.filter(**filter_kwargs).order_by('-created_at').first()
            if not otp_record:
                return Response(
                    {"error": "Invalid verification code"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if expired
            if otp_record.is_expired:
                return Response(
                    {"error": "Verification code has expired. Please request a new one."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark as verified
            otp_record.is_verified = True
            otp_record.save()
            
            # Update user if associated
            if otp_record.user:
                user = otp_record.user
                
                # Update verification status based on type
                if verification_type == OTPVerification.TYPE_EMAIL:
                    user.email_verified = True
                    if user.phone_verified or not user.phone_number:
                        user.is_verified = True
                
                elif verification_type == OTPVerification.TYPE_PHONE:
                    user.phone_verified = True
                    if user.email_verified:
                        user.is_verified = True
                
                user.save()
                
                # For login OTP, generate tokens
                if verification_type == OTPVerification.TYPE_LOGIN:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': UserDetailSerializer(user).data
                    }, status=status.HTTP_200_OK)
            
            return Response({
                'message': 'Verification successful',
                'verification_type': verification_type,
                'verified': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Verification failed: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def email_login(self, request):
        """Login with email - first step to request OTP"""
        serializer = EmailLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        # Generate OTP
        otp_code = generate_otp()
        
        # Get user
        try:
            user = User.objects.get(email=email)
            
            # Create OTP record
            otp_record = OTPVerification.objects.create(
                user=user,
                email=email,
                otp_code=otp_code,
                verification_type=OTPVerification.TYPE_LOGIN
            )
            
            # Send OTP
            success = send_email_otp(email, otp_code, OTPVerification.TYPE_LOGIN)
            
            if not success:
                return Response(
                    {"error": "Failed to send verification code. Please try again later."}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                "message": "Verification code sent to email",
                "verification_id": str(otp_record.id)
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "No user found with this email address"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def phone_login(self, request):
        """Login with phone - first step to request OTP"""
        serializer = PhoneLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data['phone_number']
        
        # Generate OTP
        otp_code = generate_otp()
        
        # Get user
        try:
            user = User.objects.get(phone_number=phone_number)
            
            # Create OTP record
            otp_record = OTPVerification.objects.create(
                user=user,
                phone_number=phone_number,
                otp_code=otp_code,
                verification_type=OTPVerification.TYPE_LOGIN
            )
            
            # Send OTP
            success = send_phone_otp(phone_number, otp_code)
            
            if not success:
                return Response(
                    {"error": "Failed to send verification code. Please try again later."}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                "message": "Verification code sent to phone",
                "verification_id": str(otp_record.id)
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "No user found with this phone number"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def verify_login(self, request):
        """Verify OTP and complete login"""
        serializer = OTPLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get('email')
        phone_number = serializer.validated_data.get('phone_number')
        otp_code = serializer.validated_data['otp_code']
        
        # Find the OTP record
        filter_kwargs = {
            'verification_type': OTPVerification.TYPE_LOGIN,
            'otp_code': otp_code,
            'is_verified': False
        }
        
        if email:
            filter_kwargs['email'] = email
        elif phone_number:
            filter_kwargs['phone_number'] = phone_number
        
        try:
            otp_record = OTPVerification.objects.filter(**filter_kwargs).order_by('-created_at').first()
            if not otp_record:
                return Response(
                    {"error": "Invalid verification code"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if expired
            if otp_record.is_expired:
                return Response(
                    {"error": "Verification code has expired. Please request a new one."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark as verified
            otp_record.is_verified = True
            otp_record.save()
            
            # Generate tokens
            user = otp_record.user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserDetailSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Login failed: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def reset_password_request(self, request):
        """Request password reset via email or phone"""
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        
        if not email and not phone_number:
            return Response({
                "error": "Either email or phone number is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find user
            user = None
            if email:
                user = User.objects.get(email=email)
            elif phone_number:
                user = User.objects.get(phone_number=phone_number)
                
            if not user:
                return Response({
                    "error": "No account found with the provided information"
                }, status=status.HTTP_404_NOT_FOUND)
                
            # Generate OTP
            otp_code = generate_otp()
            
            # Create OTP verification record
            otp_record = OTPVerification.objects.create(
                user=user,
                email=email if email else None,
                phone_number=phone_number if phone_number else None,
                otp_code=otp_code,
                verification_type=OTPVerification.TYPE_PASSWORD_RESET
            )
            
            # Send OTP
            if email:
                send_email_otp(email, otp_code, OTPVerification.TYPE_PASSWORD_RESET)
                message = "Password reset code sent to your email"
            else:
                send_phone_otp(phone_number, otp_code)
                message = "Password reset code sent to your phone"
                
            return Response({
                "message": message,
                "verification_id": str(otp_record.id)
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                "error": "No account found with the provided information"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": f"Failed to process request: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def reset_password_verify(self, request):
        """Verify password reset OTP and set new password"""
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        otp_code = request.data.get('otp_code')
        new_password = request.data.get('new_password')
        
        if not otp_code:
            return Response({"error": "Verification code is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not new_password:
            return Response({"error": "New password is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not email and not phone_number:
            return Response({"error": "Either email or phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find the OTP record
        filter_kwargs = {
            'verification_type': OTPVerification.TYPE_PASSWORD_RESET,
            'otp_code': otp_code,
            'is_verified': False
        }
        
        if email:
            filter_kwargs['email'] = email
        elif phone_number:
            filter_kwargs['phone_number'] = phone_number
        
        try:
            otp_record = OTPVerification.objects.filter(**filter_kwargs).order_by('-created_at').first()
            if not otp_record:
                return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_record.is_expired:
                return Response({"error": "Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark as verified
            otp_record.is_verified = True
            otp_record.save()
            
            # Update user password
            user = otp_record.user
            user.set_password(new_password)
            user.save()
            
            return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": f"Password reset failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
