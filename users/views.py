import random
from datetime import timedelta 
from django.shortcuts import get_object_or_404
from django.utils import timezone


from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import *
from .models import *
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.contrib.auth.hashers import make_password # to hash passcode



class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # Generate email verification token
                token = get_random_string(4)
                EmailVerificationToken.objects.create(user=user, token=token)
                
                # Send email
                send_mail(
                    subject = 'Verify Your email',
                    message= f"""
                    Hello {user.first_name}!

                    Thank you for signing up. Please verify your email address by entering the verification code below:
                    
                    Your Verification Code: {token}

                    If you have any issues, contact our support at topdave@gmail.com

                    Best regards,
                    """,
                        from_email = None,
                        recipient_list=[user.email],
                        fail_silently=False
                )
                return Response({"Message": "User Created successfully. Please verify Your email"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VerifyEmailView(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            token = request.data.get("token")
            
            if not email or not token:
                return Response({"error": "Email and token are required!"}, status=status.HTTP_400_BAD_REQUEST)
            
            if token == token:
                try:
                    user = User.objects.get(email=email)
                    user.profile.is_email_verified = True
                    user.profile.save()
                    del token
                    return Response({"message": "Email verified successfully."})
                except User.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error":"invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ResendEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if user.profile.is_email_verified:
                return Response({"message": "Email already verified."}, status=status.HTTP_200_OK)

            # Generate a new token
            token = get_random_string(4)
            EmailVerificationToken.objects.create(user=user, token=token)

            # Send the email again
            send_mail(
                subject='Verify Your email',
                message= f"""
                Hello {user.first_name}!

                Thank you for signing up. Please verify your email address by entering the verification code below:
                
                Your Verification Code: {token}

                If you didn't request this, please ignore this email.

                If you have any issues, contact our support at support@example.com.

                Best regards,
                """,
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False
            )

            return Response({"message": "Verification email resent. Please check your inbox."})
        
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    def post(self, request):
        try:
            username = request.data.get('username').strip().lower()
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if not user.profile.is_email_verified:
                    return Response({'error':'Email not verified'})
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message":f"{username} logged in successfully",
                    "access_token":str(refresh.access_token),
                    "refresh_token":str(refresh)
                }, status=status.HTTP_200_OK)
            return Response({"Message":"Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            profile = request.user.profile
            serializer = ProfileSerializer(profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request):
        try:
            profile = request.user.profile
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
def generate_otp():
    return str(random.randint(100000, 999999))

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({"message": "If the email exists, an OTP has been sent."}, status=status.HTTP_200_OK)

        otp = generate_otp()
        PasswordResetOTP.objects.create(user=user, otp=otp)

        # Send the OTP via email
        send_mail(
            "Your Password Reset OTP",
            f"Your OTP code is {otp}. It expires in 10 minutes.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "If the email exists, an OTP has been sent."}, status=status.HTTP_200_OK)

class VerifyForgotPasswordOTPView(APIView):
    def post(self, request):
        serializer = VerifyResetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
            otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp, is_verified=False).last()

            if not otp_obj or otp_obj.is_expired():
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

            otp_obj.is_verified = True
            otp_obj.save()

            return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
            otp_obj = PasswordResetOTP.objects.filter(user=user, is_verified=True).last()

            if not otp_obj or otp_obj.is_expired():
                return Response({"error": "OTP not verified or expired."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            # Invalidate used OTP
            otp_obj.delete()

            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({"message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "message": "Logout successful"
            }, status=status.HTTP_205_RESET_CONTENT)  
        except Exception as e:
            return Response({ "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CountryView(APIView):
        def get(self, request):
            try:
                countries = Country.objects.all()
                serializer = CountrySerializer(countries, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        def post(self, request):
            try:
                serializer = CountrySerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CountryDetailView(APIView):
    def put(self, request, pk):
        country = get_object_or_404(Country, pk=pk)
        serializer = CountrySerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        country = get_object_or_404(Country, pk=pk)
        serializer = CountrySerializer(country, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        country = get_object_or_404(Country, pk=pk)
        country.delete()
        return Response('deleted successfully', status=status.HTTP_200_OK)
        
class VerifyOldPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = VerifyOldPasswordSerializer(data=request.data, context={'request':request})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            #OTP
            user = request.user
            otp = ''.join([str(random.randint(0,9)) for i in range(4)])
            expires_at = timezone.now() + timedelta(minutes=5)
            
            # save or update OTP
            PasswordOTP.objects.update_or_create(
                user = user,
                defaults = {'otp':otp, 'expires_at':expires_at}
            )
            
            # send email
            send_mail(
                subject = 'OTP',
                message = f'Your OTP is {otp}. It expires in 5 minutes',
                from_email= None,
                recipient_list=[user.email]
                
            )
            return Response({'detail':'OTP sent to your email'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VerifyOTPView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            serializer = VerifyOTPSerializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                return Response({'detail':'OTP verified.You can now change password'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password) # hashing the password
                return Response({'message':'password changed successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
