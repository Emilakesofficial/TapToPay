from django.urls import path
from .views import *

urlpatterns = [
    path('initialize/payment/', StartPaymentView.as_view()),
    path('verify/payment/<str:reference>/', VerifyPaymentView.as_view()),
]