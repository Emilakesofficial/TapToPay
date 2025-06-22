from django.urls import path
from .views import *

urlpatterns = [
    path('get-cart/', CartView.as_view()),
    path('add/', AddRemoveCartItemView.as_view()),
    path('remove/', AddRemoveCartItemView.as_view()),
    path('update-tip/', UpdateTipView.as_view()),
]