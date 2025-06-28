from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class CustomUnitView(APIView):
        def get(self, request):
            try:
                unit = CustomUnit.objects.all()
                serializer = CustomUnitSerializer(unit, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        def post(self, request):
            try:
                serializer = CustomUnitSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class CustomUnitDetailedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        try:
            unit = CustomUnit.objects.get(id=id)
            serializer = CustomUnitSerializer(unit)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUnit.DoesNotExist:
            return Response({'error': 'Unit not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, id):
        try:        
            unit = CustomUnit.objects.get(id=id)
            serializer = CustomUnitSerializer(unit, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUnit.DoesNotExist:
            return Response({'error': 'Unit not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, id):
        try:
            unit = CustomUnit.objects.get(id=id)
            unit.delete()
            return Response({'Unit deleted successfully'}, status=status.HTTP_200_OK)
        except CustomUnit.DoesNotExist:
            return Response({'error': 'Unit not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class ProductView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            products = Product.objects.filter(user=request.user)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        try:
            serializer = ProductSerializer(data=request.data, context = {'request':request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, id, user):
        try:
            return Product.objects.get(id=id, user=user)
        except Product.DoesNotExist:
            return None
        
    def get(self, request, id):
        try:
            product = self.get_object(id, request.user)
            if not product:
                return Response({'detail':'Product not found'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, id):
        try:
            product = self.get_object(id, request.user)
            if not product:
                return Response({'detail': 'Product not found'}, status=status.HTTP_400_BAD_REQUEST)
            if product.user != request.user: # check if the user is the one updating the product
                return Response({'detail':'Permission denied'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                updated_product = serializer.save()
                updated_product.update_availability()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, id):
        try:
            product = self.get_object(id, request.user)
            if not product:
                return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
            product.delete()
            return Response({'message':'deleted successfully'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        