from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

# DRF-YASG imports
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import re_path


from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="TapToPay Merchant API",
        default_version='v1',
        description="API documentation for the Real Estate project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="adegbemiadekunle56@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/checkout/', include('checkout.urls')),
    path('api/merchant/', include('merchant.urls')),
    path('api/payment/', include('payment.urls')),
    path('api/report/', include('report.urls')),
    path('', lambda request: JsonResponse({'message': 'TapToPay Merchant Backend API is live!'})),
    
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

