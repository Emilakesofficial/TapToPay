from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)  # Unpack the tuple
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
class AddRemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            product_id = request.data.get('product_id')
            action = request.data.get('action')  # "add" or "remove"
            quantity = int(request.data.get('quantity', 1))

            if action not in ['add', 'remove']:
                return Response({"error": "Invalid action. Must be 'add' or 'remove'."},
                                status=status.HTTP_400_BAD_REQUEST)

            cart, _ = Cart.objects.get_or_create(user=request.user)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

            item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if action == 'add':
                if product.stock < item.quantity + quantity:
                    return Response(
                        {"error": f"Only {product.quantity} left in stock for '{product.name}'."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                item.quantity += quantity
            elif action == 'remove':
                item.quantity = max(0, item.quantity - quantity)

            if item.quantity == 0:
                item.delete()
            else:
                item.save()

            # Return updated cart data
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CartSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            return Response({
                "subtotal": round(cart._calculate_subtotal(), 2),
                "tip": round(cart.calculate_tip(), 2),
                "tax": round(cart.calculate_tax(), 2),
                "service_fee": round(cart.calculate_fee(), 2),
                "total": round(cart.calculate_total(), 2),
            }, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

class EmptyCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response({"message": "Cart emptied successfully."}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
