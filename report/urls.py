from django.urls import path
from .views import *

urlpatterns = [
    path('daily-sales/', DailySalesReportView.as_view()),
    path('transactions/', TransactionReportAPIView.as_view()),
]
