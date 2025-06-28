from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import DailySalesReport
from rest_framework.permissions import IsAuthenticated
from .serializers import *

class DailySalesReportView(APIView):
    permission_classes = [IsAuthenticated]  # Only admin can see

    def get(self, request):
        reports = DailySalesReport.objects.all().order_by('-date')
        serializer = DailySalesReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    
class TransactionReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_staff or user.is_superuser:
            reports = TransactionReport.objects.all().order_by('-timestamp')
        else:
            reports = TransactionReport.objects.filter(user=user).order_by('-timestamp')

        serializer = TransactionReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)