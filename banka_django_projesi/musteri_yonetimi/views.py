from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Prefetch
from django.db.models.functions import TruncMonth
from datetime import datetime
from .models import (
    MusteriTemel, MusteriGercek, MusteriTuzel, MusteriTelefon,
    MusteriAdres, MusteriEmail, MusteriOrtak
)
from .serializers import (
    MusteriSerializer, MusteriCreateSerializer, MusteriListSerializer,
    MusteriOrtakSerializer, MusteriTelefonSerializer, MusteriAdresSerializer, MusteriEmailSerializer
)
import logging
import traceback

logger = logging.getLogger(__name__)

class MusteriViewSet(viewsets.ModelViewSet):
    """Müşteri CRUD API - Normalize edilmiş yapı"""
    queryset = MusteriTemel.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MusteriCreateSerializer
        elif self.action == 'list':
            return MusteriListSerializer
        return MusteriSerializer
    
    def get_queryset(self):
        # Prefetch ile ilişkili tabloları getir (N+1 sorgusu önlemi)
        queryset = MusteriTemel.objects.select_related(
            'gercek_kisi', 'tuzel_kisi'
        ).prefetch_related(
            'telefonlar', 'adresler', 'emailler', 'notlar',
            Prefetch('tuzel_kisi__ortaklar', queryset=MusteriOrtak.objects.all())
        )
        
        search = self.request.query_params.get('search')
        musteri_turu = self.request.query_params.get('turu')
        aktif = self.request.query_params.get('aktif', 'true')
        
        if search:
            # Arama: müşteri no, ad/soyad, şirket unvanı, telefon, email, tckn
            queryset = queryset.filter(
                Q(musteri_no__icontains=search) |
                Q(gercek_kisi__adi__icontains=search) |
                Q(gercek_kisi__soyadi__icontains=search) |
                Q(gercek_kisi__tckn__icontains=search) |
                Q(tuzel_kisi__sirket_unvani__icontains=search) |
                Q(tuzel_kisi__yetkili_adi__icontains=search) |
                Q(tuzel_kisi__yetkili_soyadi__icontains=search) |
                Q(telefonlar__telefon__icontains=search) |
                Q(emailler__email__icontains=search)
            ).distinct()
        
        if musteri_turu:
            queryset = queryset.filter(musteri_turu=musteri_turu)
        
        if aktif.lower() == 'true':
            queryset = queryset.filter(durum_kodu=True)
        elif aktif.lower() == 'false':
            queryset = queryset.filter(durum_kodu=False)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        logger.info(f"Yeni müşteri kaydı - User: {request.user}")
        logger.info(f"Gelen ham veri: {request.data}")
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                musteri = serializer.save()
                logger.info(f"Müşteri başarıyla kaydedildi: {musteri.musteri_no}")
                
                # Tam bilgilerle response döndür
                response_data = MusteriSerializer(musteri).data
                return Response({
                    'success': True,
                    'message': 'Müşteri başarıyla kaydedildi',
                    'data': response_data
                }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                logger.error(f"Müşteri kayıt hatası: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")  # Düzeltildi
                return Response({
                    'success': False,
                    'message': 'Kayıt sırasında hata oluştu',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.error(f"Müşteri kayıt validation hatası: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Validation hatası',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """Müşteri listesi - array döndür"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Müşteri listesi çekildi: {len(serializer.data)} kayıt")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Müşteri listesi hatası: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")  # Düzeltildi
            return Response({
                'error': 'Müşteri listesi yüklenirken hata oluştu',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Müşteri istatistikleri"""
        try:
            total = MusteriTemel.objects.filter(durum_kodu=True).count()
            
            turu_stats = {}
            for turu_kod, turu_ad in MusteriTemel.MUSTERI_TURU_CHOICES:
                count = MusteriTemel.objects.filter(musteri_turu=turu_kod, durum_kodu=True).count()
                turu_stats[turu_ad] = count
            
            monthly_data = MusteriTemel.objects.filter(
                created_at__year=datetime.now().year,
                durum_kodu=True
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('musteri_no')
            ).order_by('month')
            
            return Response({
                'toplam_musteri': total,
                'turu_istatistik': turu_stats,
                'aylik_kayit': list(monthly_data)
            })
        except Exception as e:
            logger.error(f"İstatistik hatası: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return Response({
                'error': 'İstatistik yüklenirken hata oluştu',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        """Müşteri durumunu aktif/pasif yap"""
        try:
            musteri = self.get_object()
            eski_durum = musteri.durum_kodu
            musteri.durum_kodu = not musteri.durum_kodu
            musteri.save()
            
            return Response({
                'message': f'Müşteri {"aktif" if musteri.durum_kodu else "pasif"} duruma getirildi',
                'musteri_no': musteri.musteri_no,
                'eski_durum': eski_durum,
                'yeni_durum': musteri.durum_kodu
            })
        except Exception as e:
            logger.error(f"Durum değiştirme hatası: {str(e)}")
            return Response({
                'error': 'Durum değiştirilemedi',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
   


    
    @action(detail=True, methods=['get', 'post'])
    def ortaklar(self, request, pk=None):
        """Müşteri ortakları (Tüzel kişi için)"""
        musteri = self.get_object()
        
        # Tüzel kişi kontrolü
        if musteri.musteri_turu != 'tuzel' or not hasattr(musteri, 'tuzel_kisi'):
            return Response({
                'error': 'Sadece tüzel kişi müşteriler için ortak bilgisi mevcuttur'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'POST':
            serializer = MusteriOrtakSerializer(data=request.data)
            if serializer.is_valid():
                ortak = serializer.save(musteri=musteri.tuzel_kisi)
                return Response(MusteriOrtakSerializer(ortak).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        ortaklar = MusteriOrtak.objects.filter(musteri=musteri.tuzel_kisi)
        serializer = MusteriOrtakSerializer(ortaklar, many=True)
        toplam_pay = sum([ortak.pay for ortak in ortaklar])
        
        return Response({
            'ortaklar': serializer.data,
            'toplam_pay': toplam_pay
        })
    
    # İletişim bilgileri yönetimi
    @action(detail=True, methods=['get', 'post'])
    def telefonlar(self, request, pk=None):
        """Müşteri telefon bilgileri"""
        musteri = self.get_object()
        
        if request.method == 'POST':
            serializer = MusteriTelefonSerializer(data=request.data)
            if serializer.is_valid():
                telefon = serializer.save(musteri=musteri)
                return Response(MusteriTelefonSerializer(telefon).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        telefonlar = musteri.telefonlar.filter(aktif=True)
        serializer = MusteriTelefonSerializer(telefonlar, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def adresler(self, request, pk=None):
        """Müşteri adres bilgileri"""
        musteri = self.get_object()
        
        if request.method == 'POST':
            serializer = MusteriAdresSerializer(data=request.data)
            if serializer.is_valid():
                adres = serializer.save(musteri=musteri)
                return Response(MusteriAdresSerializer(adres).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        adresler = musteri.adresler.filter(aktif=True)
        serializer = MusteriAdresSerializer(adresler, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def emailler(self, request, pk=None):
        """Müşteri email bilgileri"""
        musteri = self.get_object()
        
        if request.method == 'POST':
            serializer = MusteriEmailSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.save(musteri=musteri)
                return Response(MusteriEmailSerializer(email).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        emailler = musteri.emailler.filter(aktif=True)
        serializer = MusteriEmailSerializer(emailler, many=True)
        return Response(serializer.data)