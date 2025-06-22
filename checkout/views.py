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
                item.quantity += quantity
            elif action == 'remove':
                item.quantity = max(0, item.quantity - quantity)

            if item.quantity == 0:
                item.delete()
            else:
                item.save()

            return Response({"message": "Cart updated"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class UpdateTipView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        tip_amount = request.data.get("tip_amount")
        tip_percentage = request.data.get("tip_percentage")

        if tip_amount is not None:
            cart.tip_amount = tip_amount
            cart.tip_percentage = 0
        elif tip_percentage is not None:
            cart.tip_percentage = tip_percentage
            cart.tip_amount = 0

        cart.save()
        return Response({"message": "Tip updated"}, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)

            # Step 1: Validate stock
            for item in cart.items.all():
                product = item.product
                if product.quantity < item.quantity:
                    return Response(
                        {"error": f"Not enough stock for '{product.name}'. Only {product.quantity} left."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Step 2: Deduct stock and update availability
            for item in cart.items.all():
                product = item.product
                product.quantity -= item.quantity
                product.update_availability()
                product.save()

            # Step 3: Clear the cart
            cart.items.all().delete()

            return Response({"message": "Checkout successful."}, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

