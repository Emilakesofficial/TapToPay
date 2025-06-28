from django.urls import path
from .views import MerchantSettingsView

urlpatterns = [
    path('get/merchant/settings/', MerchantSettingsView.as_view(), name='merchant-settings'),
    path('update/merchant/settings/', MerchantSettingsView.as_view(), name='merchant-settings'),
]
