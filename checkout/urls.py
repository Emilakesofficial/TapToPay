from django.urls import path
from .views import *

urlpatterns = [
    path('get/cart/', CartView.as_view()),
    path('add/', AddRemoveCartItemView.as_view()),
    path('remove/', AddRemoveCartItemView.as_view()),
    path('cart/summary/', CartSummaryView.as_view()),
    path('cart/empty/', EmptyCartView.as_view()),
]