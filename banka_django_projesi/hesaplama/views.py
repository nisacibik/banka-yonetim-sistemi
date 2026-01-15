# musteri_yonetimi/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import logging

from .models import KrediHesaplama, KrediFaizOrani, KrediTuru
from .serializers import (
    KrediHesaplamaRequestSerializer,
    KrediHesaplamaResponseSerializer,
    KrediHesaplamaSerializer,
    KrediFaizOraniSerializer,
    KrediTurleriSerializer,
    hesapla_kredi_taksiti
)

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """İstemci IP adresini alır"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@api_view(['POST'])
@permission_classes([AllowAny])  # Herkese açık
def kredi_hesapla(request):
    """
    Kredi hesaplama API endpoint'i
    
    POST /api/musteri/kredi-hesapla/
    
    Body:
    {
        "kredi_turu": "bireysel",
        "kredi_tutari": 50000.00,
        "vade_ay": 36,
        "faiz_orani": 2.50,
        "kaydet": true
    }
    """
    
    serializer = KrediHesaplamaRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'error': 'Geçersiz veri',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Validasyonu geçen verileri al
        validated_data = serializer.validated_data
        kredi_turu = validated_data['kredi_turu']
        kredi_tutari = validated_data['kredi_tutari']
        vade_ay = validated_data['vade_ay']
        faiz_orani = validated_data['faiz_orani']
        kaydet = validated_data.get('kaydet', False)
        
        # Kredi türü limitlerini kontrol et
        faiz_bilgisi = KrediFaizOrani.get_faiz_bilgisi(kredi_turu)
        if faiz_bilgisi:
            if kredi_tutari < faiz_bilgisi.min_tutar or kredi_tutari > faiz_bilgisi.max_tutar:
                return Response({
                    'success': False,
                    'error': f'{faiz_bilgisi.get_kredi_turu_display()} için tutar limitler: {faiz_bilgisi.min_tutar} - {faiz_bilgisi.max_tutar} TL'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if vade_ay < faiz_bilgisi.min_vade_ay or vade_ay > faiz_bilgisi.max_vade_ay:
                return Response({
                    'success': False,
                    'error': f'{faiz_bilgisi.get_kredi_turu_display()} için vade limitler: {faiz_bilgisi.min_vade_ay} - {faiz_bilgisi.max_vade_ay} ay'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kredi hesaplaması
        hesaplama_sonucu = hesapla_kredi_taksiti(kredi_tutari, vade_ay, faiz_orani)
        
        # Response data hazırla
        response_data = {
            'kredi_turu': kredi_turu,
            'kredi_turu_display': dict(KrediTuru.choices)[kredi_turu],
            'kredi_tutari': kredi_tutari,
            'vade_ay': vade_ay,
            'faiz_orani': faiz_orani,
            'aylik_taksit': hesaplama_sonucu['aylik_taksit'],
            'toplam_odeme': hesaplama_sonucu['toplam_odeme'],
            'toplam_faiz': hesaplama_sonucu['toplam_faiz'],
            'aylik_faiz_orani': hesaplama_sonucu['aylik_faiz_orani'],
            'faiz_yuzdesi': faiz_orani,
            'hesaplama_detaylari': hesaplama_sonucu['hesaplama_detaylari'],
            'hesaplama_id': None
        }
        
        # Kaydetme işlemi (isteğe bağlı)
        if kaydet:
            try:
                kredi_hesaplama = KrediHesaplama.objects.create(
                    kredi_turu=kredi_turu,
                    kredi_tutari=kredi_tutari,
                    vade_ay=vade_ay,
                    faiz_orani=faiz_orani,
                    aylik_taksit=hesaplama_sonucu['aylik_taksit'],
                    toplam_odeme=hesaplama_sonucu['toplam_odeme'],
                    toplam_faiz=hesaplama_sonucu['toplam_faiz'],
                    ip_adresi=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    hesaplama_detaylari=hesaplama_sonucu['hesaplama_detaylari']
                )
                response_data['hesaplama_id'] = kredi_hesaplama.id
                logger.info(f"Kredi hesaplama kaydedildi: ID={kredi_hesaplama.id}")
            except Exception as e:
                logger.error(f"Kredi hesaplama kaydetme hatası: {e}")
                # Kaydetme hatası olsa bile hesaplama sonucu döndürülür
        
        # Response serializer ile doğrula
        response_serializer = KrediHesaplamaResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response({
                'success': True,
                'data': response_serializer.validated_data
            }, status=status.HTTP_200_OK)
        else:
            logger.error(f"Response serializer hatası: {response_serializer.errors}")
            return Response({
                'success': False,
                'error': 'Hesaplama sonucu formatında hata'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Kredi hesaplama hatası: {e}")
        return Response({
            'success': False,
            'error': 'Hesaplama sırasında beklenmedik bir hata oluştu'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
@method_decorator(cache_page(60 * 15))  # 15 dakika cache
def kredi_turleri_listesi(request):
    """
    Kredi türleri listesi (frontend için)
    
    GET /api/musteri/kredi-turleri/
    """
    
    # Frontend'e uygun format
    kredi_turleri_data = [
        {
            'id': 'bireysel',
            'title': 'Bireysel Krediler',
            'description': 'İhtiyaç kredisi hesaplaması',
            'icon': 'User',
            'color': 'bg-blue',
            'borderColor': 'border-blue',
            'textColor': 'text-blue'
        },
        {
            'id': 'konut',
            'title': 'Konut Kredileri',
            'description': 'Ev kredisi hesaplaması',
            'icon': 'Home',
            'color': 'bg-green',
            'borderColor': 'border-green',
            'textColor': 'text-green'
        },
        {
            'id': 'tasit',
            'title': 'Taşıt Kredileri',
            'description': 'Araç kredisi hesaplaması',
            'icon': 'Car',
            'color': 'bg-purple',
            'borderColor': 'border-purple',
            'textColor': 'text-purple'
        }
    ]
    
    # Faiz bilgilerini ekle
    for kredi in kredi_turleri_data:
        faiz_bilgisi = KrediFaizOrani.get_faiz_bilgisi(kredi['id'])
        if faiz_bilgisi:
            kredi['faiz_bilgisi'] = faiz_bilgisi.to_dict()
    
    return Response({
        'success': True,
        'data': kredi_turleri_data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def faiz_oranlari(request):
    """
    Güncel faiz oranları listesi
    
    GET /api/musteri/faiz-oranlari/
    """
    
    try:
        faiz_oranlari = KrediFaizOrani.objects.filter(aktif=True)
        serializer = KrediFaizOraniSerializer(faiz_oranlari, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Faiz oranları listesi hatası: {e}")
        return Response({
            'success': False,
            'error': 'Faiz oranları alınamadı'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Sadece authenticated kullanıcılar
def hesaplama_gecmisi(request):
    """
    Kullanıcının kredi hesaplama geçmişi
    
    GET /api/musteri/hesaplama-gecmisi/
    Query Parameters:
    - limit: Sayfa başına kayıt sayısı (default: 20)
    - offset: Başlangıç noktası (default: 0)
    - kredi_turu: Kredi türü filtresi (opsiyonel)
    """
    
    try:
        # Query parametreleri
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        kredi_turu = request.GET.get('kr
