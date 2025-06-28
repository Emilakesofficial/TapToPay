from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from rest_framework import status
from rest_framework.response import Response

class MerchantSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            merchant = request.user.merchant_profile
            serializer = MerchantProfileSerializer(merchant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MerchantProfile.DoesNotExist:
            return Response({"error": "Merchant profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        try:
            merchant = request.user.merchant_profile
        except MerchantProfile.DoesNotExist:
            return Response({"error": "Merchant profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MerchantProfileSerializer(merchant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Merchant settings updated.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


