# kredi_yonetimi/views.py
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, Avg
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from .models import KrediHesabi, KrediOdemePlanim, KrediOdemeHareketleri
from musteri_yonetimi.models import MusteriTemel
from .serializers import (
    KrediHesabiSerializer, KrediHesabiCreateSerializer, KrediHesabiListSerializer,
    MusteriKrediLookupSerializer, KrediOdemePlaniSerializer, 
    KrediOdemeHareketleriSerializer
)
import logging

logger = logging.getLogger(__name__)

class MusteriLookupView(generics.ListAPIView):
    """Müşteri arama API'si - kredi hesabı açarken kullanılacak"""
    serializer_class = MusteriKrediLookupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = MusteriTemel.objects.filter(aktif=True)
        
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(musteri_no__icontains=search) |
                Q(ad_soyad__icontains=search) |
                Q(sirket_unvani__icontains=search) |
                Q(isletme_unvani__icontains=search) |
                Q(telefon__icontains=search) |
                Q(tckn__icontains=search)
            )[:10]  # İlk 10 sonuç
        
        return queryset

class KrediHesabiViewSet(viewsets.ModelViewSet):
    """Kredi Hesabı CRUD API"""
    queryset = KrediHesabi.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return KrediHesabiCreateSerializer
        elif self.action == 'list':
            return KrediHesabiListSerializer
        return KrediHesabiSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Query parameters
        search = self.request.query_params.get('search')
        musteri_no = self.request.query_params.get('musteri_no')
        aktif = self.request.query_params.get('aktif', 'true')
        doviz_cinsi = self.request.query_params.get('doviz_cinsi')
        kredi_turu = self.request.query_params.get('kredi_turu')
        
        if search:
            queryset = queryset.filter(
                Q(kredi_hesap_no__icontains=search) |
                Q(musteri__musteri_no__icontains=search) |
                Q(musteri__ad_soyad__icontains=search) |
                Q(musteri__sirket_unvani__icontains=search) |
                Q(musteri__isletme_unvani__icontains=search)
            )
        
        if musteri_no:
            queryset = queryset.filter(musteri__musteri_no=musteri_no)
        
        if aktif.lower() == 'true':
            queryset = queryset.filter(aktif=True)
        elif aktif.lower() == 'false':
            queryset = queryset.filter(aktif=False)
        
        if doviz_cinsi:
            queryset = queryset.filter(doviz_cinsi=doviz_cinsi)
        
        if kredi_turu:
            queryset = queryset.filter(kredi_turu=kredi_turu)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        logger.info(f"Yeni kredi hesabı açılıyor - User: {request.user}")
        logger.info(f"Gelen veri: {request.data}")
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                kredi_hesabi = serializer.save()
                logger.info(f"Kredi hesabı başarıyla açıldı: {kredi_hesabi.kredi_hesap_no}")
                
                response_data = KrediHesabiSerializer(kredi_hesabi).data
                return Response({
                    'success': True,
                    'message': 'Kredi hesabı başarıyla açıldı',
                    'data': response_data
                }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                logger.error(f"Kredi hesabı açma hatası: {str(e)}")
                import traceback
                logger.error(f"Stack trace: {traceback.format_exc()}")
                return Response({
                    'success': False,
                    'message': 'Kredi hesabı açılırken hata oluştu',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.error(f"Kredi hesabı validation hatası: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Validation hatası',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """Kredi hesap listesi"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Kredi hesap listesi çekildi: {len(serializer.data)} kayıt")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Kredi hesap listesi hatası: {str(e)}")
            return Response({
                'error': 'Kredi hesap listesi yüklenirken hata oluştu',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def odeme_plani(self, request, pk=None):
        """Kredi ödeme planını getir"""
        kredi_hesabi = self.get_object()
        odeme_plani = KrediOdemePlanim.objects.filter(kredi_hesabi=kredi_hesabi)
        serializer = KrediOdemePlaniSerializer(odeme_plani, many=True)
        
        # Özet bilgiler
        toplam_anapara = sum([plan.anapara_tutari for plan in odeme_plani])
        toplam_faiz = sum([plan.faiz_tutari for plan in odeme_plani])
        odenen_taksit = odeme_plani.filter(odendi_mi=True).count()
        kalan_taksit = odeme_plani.filter(odendi_mi=False).count()
        
        return Response({
            'kredi_hesap_no': kredi_hesabi.kredi_hesap_no,
            'musteri': kredi_hesabi.musteri.get_display_name(),
            'toplam_anapara': toplam_anapara,
            'toplam_faiz': toplam_faiz,
            'odenen_taksit': odenen_taksit,
            'kalan_taksit': kalan_taksit,
            'odeme_plani': serializer.data
        })
    
    @action(detail=True, methods=['get', 'post'])
    def hareketler(self, request, pk=None):
        """Kredi hesap hareketleri"""
        kredi_hesabi = self.get_object()
        
        if request.method == 'POST':
            # Yeni hareket ekle (ödeme, vb.)
            serializer = KrediOdemeHareketleriSerializer(data=request.data)
            if serializer.is_valid():
                hareket = serializer.save(
                    kredi_hesabi=kredi_hesabi,
                    islem_yapan=getattr(request.user, 'personel_kodu', 'Unknown')
                )
                
                # Eğer taksit ödemesi ise, ilgili taksiti güncelle
                if hareket.hareket_turu == 'odeme' and hareket.taksit_no:
                    try:
                        taksit = KrediOdemePlanim.objects.get(
                            kredi_hesabi=kredi_hesabi,
                            taksit_no=hareket.taksit_no
                        )
                        taksit.odendi_mi = True
                        taksit.odeme_tarihi = hareket.hareket_tarihi.date()
                        taksit.save()
                        
                        # Kalan anapara ve vadeyi güncelle
                        self.update_remaining_balance(kredi_hesabi)
                        
                    except KrediOdemePlanim.DoesNotExist:
                        pass
                
                return Response(
                    KrediOdemeHareketleriSerializer(hareket).data, 
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Hareketleri listele
        hareketler = KrediOdemeHareketleri.objects.filter(kredi_hesabi=kredi_hesabi)
        serializer = KrediOdemeHareketleriSerializer(hareketler, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def taksit_ode(self, request, pk=None):
        """Taksit ödeme işlemi"""
        kredi_hesabi = self.get_object()
        taksit_no = request.data.get('taksit_no')
        
        if not taksit_no:
            return Response({
                'error': 'Taksit numarası gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # İlgili taksiti bul
            taksit = KrediOdemePlanim.objects.get(
                kredi_hesabi=kredi_hesabi,
                taksit_no=taksit_no,
                odendi_mi=False
            )
            
            # Taksiti ödenmiş olarak işaretle
            taksit.odendi_mi = True
            taksit.odeme_tarihi = datetime.now().date()
            taksit.save()
            
            # Hareket kaydı oluştur
            KrediOdemeHareketleri.objects.create(
                kredi_hesabi=kredi_hesabi,
                hareket_turu='odeme',
                tutar=taksit.taksit_tutari,
                taksit_no=taksit_no,
                aciklama=f'{taksit_no}. taksit ödemesi',
                islem_yapan=getattr(request.user, 'personel_kodu', 'Unknown')
            )
            
            # Kalan anapara ve vadeyi güncelle
            self.update_remaining_balance(kredi_hesabi)
            
            return Response({
                'success': True,
                'message': f'{taksit_no}. taksit başarıyla ödendi',
                'odenen_tutar': taksit.taksit_tutari,
                'kalan_bakiye': kredi_hesabi.kalan_anapara
            })
            
        except KrediOdemePlanim.DoesNotExist:
            return Response({
                'error': 'Belirtilen taksit bulunamadı veya zaten ödenmiş'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Taksit ödeme hatası: {str(e)}")
            return Response({
                'error': 'Taksit ödemesi sırasında hata oluştu',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update_remaining_balance(self, kredi_hesabi):
        """Kalan anapara ve vadeyi güncelle"""
        try:
            # Ödenmemiş taksitleri al
            kalan_taksitler = KrediOdemePlanim.objects.filter(
                kredi_hesabi=kredi_hesabi,
                odendi_mi=False
            ).order_by('taksit_no')
            
            if kalan_taksitler.exists():
                # En son ödenmemiş taksitin kalan bakiyesi = kalan anapara
                en_son_taksit = kalan_taksitler.last()
                kredi_hesabi.kalan_anapara = en_son_taksit.kalan_bakiye
                kredi_hesabi.kalan_vade = kalan_taksitler.count()
            else:
                # Tüm taksitler ödendiyse
                kredi_hesabi.kalan_anapara = 0
                kredi_hesabi.kalan_vade = 0
                kredi_hesabi.aktif = False
                kredi_hesabi.kapanis_tarihi = datetime.now().date()
            
            kredi_hesabi.save()
            logger.info(f"Kredi hesabı güncellendi: {kredi_hesabi.kredi_hesap_no}")
            
        except Exception as e:
            logger.error(f"Kalan bakiye güncelleme hatası: {str(e)}")
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Kredi portföy istatistikleri"""
        try:
            aktif_krediler = KrediHesabi.objects.filter(aktif=True)
            
            # Genel istatistikler
            toplam_kredi_sayisi = aktif_krediler.count()
            toplam_kredi_tutari = aktif_krediler.aggregate(
                toplam=Sum('kredi_tutari')
            )['toplam'] or 0
            toplam_kalan_bakiye = aktif_krediler.aggregate(
                toplam=Sum('kalan_anapara')
            )['toplam'] or 0
            
            # Döviz cinsine göre dağılım
            doviz_stats = {}
            for doviz_kod, doviz_ad in KrediHesabi.DOVIZ_CINSI_CHOICES:
                krediler = aktif_krediler.filter(doviz_cinsi=doviz_kod)
                doviz_stats[doviz_ad] = {
                    'adet': krediler.count(),
                    'tutar': krediler.aggregate(toplam=Sum('kredi_tutari'))['toplam'] or 0
                }
            
            # Kredi türüne göre dağılım
            turu_stats = {}
            for turu_kod, turu_ad in KrediHesabi.KREDI_TURU_CHOICES:
                krediler = aktif_krediler.filter(kredi_turu=turu_kod)
                turu_stats[turu_ad] = {
                    'adet': krediler.count(),
                    'tutar': krediler.aggregate(toplam=Sum('kredi_tutari'))['toplam'] or 0
                }
            
            # Aylık kredi açılış istatistikleri
            aylik_data = KrediHesabi.objects.filter(
                acilis_tarihi__year=datetime.now().year
            ).annotate(
                month=TruncMonth('acilis_tarihi')
            ).values('month').annotate(
                adet=Count('kredi_hesap_no'),
                tutar=Sum('kredi_tutari')
            ).order_by('month')
            
            return Response({
                'toplam_kredi_sayisi': toplam_kredi_sayisi,
                'toplam_kredi_tutari': toplam_kredi_tutari,
                'toplam_kalan_bakiye': toplam_kalan_bakiye,
                'doviz_dagilimi': doviz_stats,
                'turu_dagilimi': turu_stats,
                'aylik_acilis': list(aylik_data)
            })
            
        except Exception as e:
            logger.error(f"İstatistik hatası: {str(e)}")
            return Response({
                'error': 'İstatistikler yüklenirken hata oluştu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)