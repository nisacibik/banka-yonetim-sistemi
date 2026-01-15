# personel/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonelViewSet

router = DefaultRouter()
router.register(r'', PersonelViewSet, basename='personel')

urlpatterns = [
    path('', include(router.urls)),
    # Custom actions:
    # POST /api/personel/login/
    # POST /api/personel/logout/  
    # GET  /api/personel/me/
]