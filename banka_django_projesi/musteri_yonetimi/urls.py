from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MusteriViewSet

router = DefaultRouter()
router.register(r'', MusteriViewSet, basename='musteri')

urlpatterns = [
    path('', include(router.urls)),
    # Bu şu URL'leri oluşturacak:
    # GET    /api/musteri/          - Müşteri listesi
    # POST   /api/musteri/          - Yeni müşteri kayıt
    # GET    /api/musteri/{id}/     - Müşteri detay
    # PUT    /api/musteri/{id}/     - Müşteri güncelleme
    # DELETE /api/musteri/{id}/     - Müşteri silme
    # GET    /api/musteri/statistics/ - İstatistikler
]