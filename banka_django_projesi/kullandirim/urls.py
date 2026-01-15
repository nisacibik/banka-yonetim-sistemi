# kredi_yonetimi/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KrediHesabiViewSet, MusteriLookupView

router = DefaultRouter()
router.register(r'hesap', KrediHesabiViewSet, basename='kredi-hesap')

urlpatterns = [
    path('musteri-arama/', MusteriLookupView.as_view(), name='musteri-arama'),
    path('', include(router.urls)),
]