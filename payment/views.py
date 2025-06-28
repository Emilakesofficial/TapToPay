import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from .models import Payment
from decimal import Decimal
from .serializers import PaymentSerializer
from .paystack import initialize_payment, verify_payment
from checkout.models import Cart

from datetime import date
from report.models import DailySalesReport
from report.models import TransactionReport

class StartPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            amount = cart.calculate_total()
            reference = str(uuid.uuid4())
            
            # create payment record
            payment = Payment.objects.create(
                user = request.user,
                cart = cart,
                amount = amount,
                reference = reference,
                status='pending',
            )
            
            paystack_response = initialize_payment(request.user.email, amount, reference)
            if paystack_response.get('status'):
                return Response({
                    'authorization_url': paystack_response['data']['authorization_url'],
                    'reference': reference
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get(self, request, reference):
        try:
            payment = Payment.objects.select_related("cart").get(reference=reference, user=request.user)
            if payment.status == "success":
                return Response({"message": "Payment already verified."}, status=status.HTTP_200_OK)

            paystack_response = verify_payment(reference)
            if paystack_response.get("data", {}).get("status") == "success":
                payment.status = "success"
                payment.save()
                
                TransactionReport.objects.create(
                user=request.user,
                payment_reference=payment.reference,
                amount=Decimal(str(payment.amount)),
                status="success"
            )
                
                today = date.today()
                report, created = DailySalesReport.objects.get_or_create(date=today)

                payment_amount = Decimal(str(payment.amount))  # safely convert float or string to Decimal
                report.total_sales_amount = report.total_sales_amount + payment_amount
                report.total_transactions +=1
                report.successful_transactions += 1
                report.save()

                cart = payment.cart
                if cart:
                    for item in cart.items.select_related("product").select_for_update():  # lock rows
                        product = item.product
                        if product.stock >= item.quantity:
                            product.stock -= item.quantity
                            product.save()
                        else:
                            return Response({
                                "error": f"Insufficient stock for {product.name}"
                            }, status=status.HTTP_400_BAD_REQUEST)

                    cart.items.all().delete()

                return Response({"message": "Payment verified, stock updated, cart cleared."}, status=status.HTTP_200_OK)

            else:
                payment.status = "failed"
                payment.save()
                
                TransactionReport.objects.create(
                user=request.user,
                payment_reference=payment.reference,
                amount=Decimal(str(payment.amount)),
                status="failed"
            )
                
                today = date.today()
                report, created = DailySalesReport.objects.get_or_create(date=today)

                report.total_transactions += 1
                report.failed_transactions += 1
                report.save()
                return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
