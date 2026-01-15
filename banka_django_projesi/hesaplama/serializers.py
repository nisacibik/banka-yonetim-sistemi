# musteri_yonetimi/serializers.py
from rest_framework import serializers
from decimal import Decimal, ROUND_HALF_UP
import math
from .models import KrediHesaplama, KrediFaizOrani, KrediTuru

class KrediHesaplamaRequestSerializer(serializers.Serializer):
    """Kredi hesaplama isteği için serializer"""
    
    kredi_turu = serializers.ChoiceField(
        choices=KrediTuru.choices,
        default=KrediTuru.BIREYSEL,
        help_text="Kredi türü: bireysel, konut, tasit"
    )
    
    kredi_tutari = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('1000.00'),
        max_value=Decimal('10000000.00'),
        help_text="Kredi tutarı (TL) - Minimum: 1.000 TL"
    )
    
    vade_ay = serializers.IntegerField(
        min_value=1,
        max_value=360,
        help_text="Vade süresi (ay) - 1-360 arası"
    )
    
    faiz_orani = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('99.99'),
        help_text="Yıllık faiz oranı (%) - Örn: 2.50"
    )
    
    kaydet = serializers.BooleanField(
        default=False,
        help_text="Hesaplamayı veritabanına kaydet"
    )

class KrediHesaplamaResponseSerializer(serializers.Serializer):
    """Kredi hesaplama sonucu için serializer"""
    
    # Giriş bilgileri
    kredi_turu = serializers.CharField()
    kredi_turu_display = serializers.CharField()
    kredi_tutari = serializers.DecimalField(max_digits=12, decimal_places=2)
    vade_ay = serializers.IntegerField()
    faiz_orani = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Hesaplama sonuçları
    aylik_taksit = serializers.DecimalField(max_digits=12, decimal_places=2)
    toplam_odeme = serializers.DecimalField(max_digits=12, decimal_places=2)
    toplam_faiz = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Ek bilgiler
    aylik_faiz_orani = serializers.DecimalField(max_digits=8, decimal_places=6)
    faiz_yuzdesi = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Hesaplama detayları
    hesaplama_detaylari = serializers.DictField()
    hesaplama_id = serializers.IntegerField(required=False, allow_null=True)

class KrediHesaplamaSerializer(serializers.ModelSerializer):
    """KrediHesaplama model serializer'ı"""
    
    kredi_turu_display = serializers.CharField(source='get_kredi_turu_display', read_only=True)
    faiz_yuzdesi = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    aylik_faiz_orani = serializers.DecimalField(max_digits=8, decimal_places=6, read_only=True)
    
    class Meta:
        model = KrediHesaplama
        fields = [
            'id', 'kredi_turu', 'kredi_turu_display', 'kredi_tutari', 'vade_ay', 
            'faiz_orani', 'aylik_taksit', 'toplam_odeme', 'toplam_faiz',
            'hesaplama_tarihi', 'faiz_yuzdesi', 'aylik_faiz_orani',
            'hesaplama_detaylari'
        ]
        read_only_fields = [
            'id', 'aylik_taksit', 'toplam_odeme', 'toplam_faiz', 
            'hesaplama_tarihi', 'faiz_yuzdesi', 'aylik_faiz_orani'
        ]

class KrediFaizOraniSerializer(serializers.ModelSerializer):
    """KrediFaizOrani model serializer'ı"""
    
    kredi_turu_display = serializers.CharField(source='get_kredi_turu_display', read_only=True)
    
    class Meta:
        model = KrediFaizOrani
        fields = [
            'id', 'kredi_turu', 'kredi_turu_display',
            'min_faiz_orani', 'max_faiz_orani', 'varsayilan_faiz_orani',
            'min_tutar', 'max_tutar', 'min_vade_ay', 'max_vade_ay',
            'aktif', 'guncelleme_tarihi'
        ]

class KrediTurleriSerializer(serializers.Serializer):
    """Kredi türleri listesi için serializer"""
    
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()
    color = serializers.CharField()
    faiz_bilgisi = serializers.DictField(required=False)

def hesapla_kredi_taksiti(kredi_tutari, vade_ay, faiz_orani):
    """
    Kredi taksitini hesaplayan yardımcı fonksiyon
    
    Args:
        kredi_tutari (Decimal): Kredi tutarı
        vade_ay (int): Vade süresi (ay)
        faiz_orani (Decimal): Yıllık faiz oranı (%)
    
    Returns:
        dict: Hesaplama sonuçları
    """
    
    # Decimal hesaplamaları için hassasiyet ayarları
    kredi_tutari = Decimal(str(kredi_tutari))
    faiz_orani = Decimal(str(faiz_orani))
    vade_ay = int(vade_ay)
    
    # Aylık faiz oranı
    aylik_faiz_orani = faiz_orani / Decimal('100') / Decimal('12')
    
    # Faiz oranı 0 ise basit bölme
    if aylik_faiz_orani == 0:
        aylik_taksit = kredi_tutari / Decimal(str(vade_ay))
        toplam_faiz = Decimal('0')
    else:
        # Bileşik faiz hesaplama formülü: P * r * (1+r)^n / ((1+r)^n - 1)
        # P: Kredi tutarı, r: Aylık faiz oranı, n: Vade (ay)
        
        # (1 + r)^n hesaplanması
        bir_arti_r = Decimal('1') + aylik_faiz_orani
        
        # Python'un decimal modülü pow fonksiyonu kullanılarak
        bir_arti_r_uzeri_n = bir_arti_r ** vade_ay
        
        # Aylık taksit hesaplanması
        pay = kredi_tutari * aylik_faiz_orani * bir_arti_r_uzeri_n
        payda = bir_arti_r_uzeri_n - Decimal('1')
        
        aylik_taksit = pay / payda
        
        # Toplam faiz
        toplam_faiz = (aylik_taksit * Decimal(str(vade_ay))) - kredi_tutari
    
    # Toplam ödeme
    toplam_odeme = aylik_taksit * Decimal(str(vade_ay))
    
    # Sonuçları 2 ondalık basamağa yuvarlama
    aylik_taksit = aylik_taksit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    toplam_odeme = toplam_odeme.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    toplam_faiz = toplam_faiz.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Hesaplama detayları
    hesaplama_detaylari = {
        'aylik_faiz_orani': float(aylik_faiz_orani),
        'faiz_yuzdesi': float(faiz_orani),
        'hesaplama_metodu': 'bileşik_faiz' if aylik_faiz_orani > 0 else 'basit_bölme',
        'yuvarlama_metodu': 'ROUND_HALF_UP',
        'formula': 'P * r * (1+r)^n / ((1+r)^n - 1)' if aylik_faiz_orani > 0 else 'P / n'
    }
    
    return {
        'aylik_taksit': aylik_taksit,
        'toplam_odeme': toplam_odeme,
        'toplam_faiz': toplam_faiz,
        'aylik_faiz_orani': aylik_faiz_orani,
        'hesaplama_detaylari': hesaplama_detaylari
    }