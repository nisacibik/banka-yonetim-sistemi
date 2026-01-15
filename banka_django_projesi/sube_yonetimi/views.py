# views.py - IlViewSet düzeltilmiş versiyon
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count
from .models import Sube, Il, Ilce
from .serializers import (
    SubeSerializer, SubeListSerializer, 
    IlSerializer, IlceSerializer
)
import logging

logger = logging.getLogger(__name__)

class IlViewSet(viewsets.ReadOnlyModelViewSet):
    """İl listesi API (sadece okuma)"""
    queryset = Il.objects.all().order_by('il_adi')
    serializer_class = IlSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        """İl listesi - DÜZELTME: Direkt queryset kullan"""
        try:
            # Direkt queryset'i çek ve serialize et
            iller = self.queryset.all()
            serializer = self.serializer_class(iller, many=True)
            
            logger.info(f"İl listesi çekildi: {len(serializer.data)} kayıt")
            print(f"DEBUG: İl sayısı: {len(serializer.data)}")  # Console debug
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"İl listesi hatası: {str(e)}")
            return Response({
                'error': 'İl listesi yüklenirken hata oluştu',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IlceViewSet(viewsets.ReadOnlyModelViewSet):
    """İlçe listesi API (sadece okuma)"""
    queryset = Ilce.objects.select_related('il').all()
    serializer_class = IlceSerializer
    permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        """İlçe listesi - DÜZELTME: Filter logic düzeltildi"""
        try:
            # Base queryset
            queryset = self.queryset.all()
            
            # İl filtresi varsa uygula
            il_id = request.query_params.get('il_id')
            if il_id:
                queryset = queryset.filter(il_id=il_id)
            
            # Sıralama
            queryset = queryset.order_by('ilce_adi')
            
            # Serialize et
            serializer = self.serializer_class(queryset, many=True)
            
            logger.info(f"İlçe listesi çekildi (il_id={il_id}): {len(serializer.data)} kayıt")
            print(f"DEBUG: İlçe sayısı: {len(serializer.data)}")  # Console debug
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"İlçe listesi hatası: {str(e)}")
            return Response({
                'error': 'İlçe listesi yüklenirken hata oluştu',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# SubeViewSet aynı kalabilir
class SubeViewSet(viewsets.ModelViewSet):
    """Şube CRUD API"""
    queryset = Sube.objects.select_related('ilce__il').all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SubeListSerializer
        return SubeSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        search = self.request.query_params.get('search')
        il_id = self.request.query_params.get('il_id')
        sinif = self.request.query_params.get('sinif')
        durum = self.request.query_params.get('durum', 'A')
        
        if search:
            queryset = queryset.filter(
                Q(sube_kodu__icontains=search) |
                Q(sube_adi__icontains=search) |
                Q(ilce__il__il_adi__icontains=search) |
                Q(ilce__ilce_adi__icontains=search)
            )
        
        if il_id:
            queryset = queryset.filter(ilce__il_id=il_id)
        if sinif:
            queryset = queryset.filter(sube_sinifi=sinif)
        if durum:
            queryset = queryset.filter(durum=durum)
        
        return queryset.order_by('sube_kodu')
    
    def list(self, request, *args, **kwargs):
        """Şube listesi"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Şube listesi çekildi: {len(serializer.data)} kayıt")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Şube listesi hatası: {str(e)}")
            return Response({
                'error': 'Şube listesi yüklenirken hata oluştu',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Şube istatistikleri"""
        try:
            total = Sube.objects.count()
            aktif = Sube.objects.filter(durum='A').count()
            pasif = Sube.objects.filter(durum='P').count()
            
            # Sınıf istatistikleri
            sinif_stats = {}
            for sinif_kod, sinif_ad in Sube.SUBE_SINIFI_CHOICES:
                count = Sube.objects.filter(sube_sinifi=sinif_kod).count()
                sinif_stats[sinif_ad] = count
            
            # Şehir istatistikleri
            sehir_stats = list(
                Sube.objects.select_related('ilce__il')
                .values('ilce__il__il_adi')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            
            return Response({
                'toplam_sube': total,
                'aktif_sube': aktif,
                'pasif_sube': pasif,
                'sinif_istatistik': sinif_stats,
                'sehir_istatistik': sehir_stats
            })
        except Exception as e:
            logger.error(f"İstatistik hatası: {str(e)}")
            return Response({
                'error': 'İstatistik yüklenirken hata oluştu',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)