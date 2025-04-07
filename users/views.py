from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Profile
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
)

verification_token ={}

class RegisterView(generics.CreateAPIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # Generate email verification token
                token = get_random_string(20)
                verification_token[user.email] = token
                
                # Send email
                send_mail(
                    subject = 'Verify Your email',
                    message= f"""
                    Hello {user.first_name}!

                    Thank you for signing up. Please verify your email address by entering the verification code below:
                    
                    Your Verification Code: {token}

                    If you didn't request this, please ignore this email.

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
            
            if verification_token.get(email) == token:
                try:
                    user = User.objects.get(email=email)
                    user.profile.is_email_verified = True
                    user.profile.save()
                    del verification_token[email]
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
            token = get_random_string(20)
            verification_token[user.email] = token

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
