from django.urls import path
from .views import *

urlpatterns = [
    path('custom-unit/', CustomUnitView.as_view()),
    path('products/', ProductView.as_view()),
    path('products/<int:id>/', ProductDetailView.as_view()),
    
]