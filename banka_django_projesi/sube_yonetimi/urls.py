# sube_yonetimi/urls.py - DÜZELTILMIŞ VERSİYON (Çakışma giderildi)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubeViewSet, IlViewSet, IlceViewSet

# Router şube CRUD için
router = DefaultRouter()
router.register(r'subeler', SubeViewSet, basename='sube')

urlpatterns = [
    # İl/İlçe API'leri - Statik path'ler
    path('iller/', IlViewSet.as_view({'get': 'list'}), name='il-list'),
    path('ilceler/', IlceViewSet.as_view({'get': 'list'}), name='ilce-list'),
    
    # Şube CRUD API'leri - Router ile (ÇAKIŞMA GİDERİLDİ)
    path('', include(router.urls)),
    
    # KALDIRILAN ÇAKIŞAN KODLAR:
    # path('subeler/', ...) - Bu satırlar kaldırıldı çünkü router zaten bunları hallediyor
    # path('subeler/<int:pk>/', ...) - Bu satırlar kaldırıldı
]

# SONUÇ URL YAPISI:
# GET  /api/sube/iller/                -> İl listesi
# GET  /api/sube/ilceler/              -> İlçe listesi  
# GET  /api/sube/ilceler/?il_id=6      -> Belirli ildeki ilçeler
# GET  /api/sube/subeler/              -> Şube listesi (Router)
# POST /api/sube/subeler/              -> Yeni şube oluştur (Router)
# GET  /api/sube/subeler/1/            -> Tekil şube (Router)
# PUT  /api/sube/subeler/1/            -> Şube güncelle (Router)
# DELETE /api/sube/subeler/1/          -> Şube sil (Router)