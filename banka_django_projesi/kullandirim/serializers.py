# kredi_yonetimi/serializers.py
from rest_framework import serializers
from .models import KrediHesabi, KrediOdemePlanim, KrediOdemeHareketleri
from musteri_yonetimi.models import MusteriTemel
from decimal import Decimal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class KrediHesabiSerializer(serializers.ModelSerializer):
    musteri_display_name = serializers.CharField(source='musteri.get_display_name', read_only=True)
    musteri_no = serializers.CharField(source='musteri.musteri_no', read_only=True)
    doviz_cinsi_display = serializers.CharField(source='get_doviz_cinsi_display', read_only=True)
    kredi_turu_display = serializers.CharField(source='get_kredi_turu_display', read_only=True)
    
    class Meta:
        model = KrediHesabi
        fields = '__all__'
        read_only_fields = ('kredi_hesap_no', 'aylik_odeme', 'toplam_geri_odeme', 
                            'kalan_anapara', 'kalan_vade', 'created_at', 'updated_at')

class KrediHesabiListSerializer(serializers.ModelSerializer):
    musteri_display_name = serializers.CharField(source='musteri.get_display_name', read_only=True)
    musteri_no = serializers.CharField(source='musteri.musteri_no', read_only=True)
    doviz_cinsi_display = serializers.CharField(source='get_doviz_cinsi_display', read_only=True)
    kredi_turu_display = serializers.CharField(source='get_kredi_turu_display', read_only=True)
    
    class Meta:
        model = KrediHesabi
        fields = [
            'kredi_hesap_no', 'musteri_no', 'musteri_display_name', 'kredi_turu',
            'kredi_turu_display', 'kredi_tutari', 'doviz_cinsi', 'doviz_cinsi_display',
            'vade', 'aylik_faiz_orani', 'aylik_odeme', 'kalan_anapara', 
            'kalan_vade', 'aktif', 'acilis_tarihi'
        ]

class MusteriKrediLookupSerializer(serializers.ModelSerializer):
    """Müşteri arama için basit serializer"""
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    
    class Meta:
        model = MusteriTemel
        fields = ['musteri_no', 'ad_soyad', 'sirket_unvani', 'isletme_unvani', 
                  'telefon', 'display_name', 'musteri_turu']

class KrediHesabiCreateSerializer(serializers.ModelSerializer):
    # Müşteri arama için
    musteri_no = serializers.CharField(write_only=True)
    
    class Meta:
        model = KrediHesabi
        fields = [
            'musteri_no', 'kredi_turu', 'kredi_tutari', 'doviz_cinsi', 
            'vade', 'aylik_faiz_orani', 'masraf_tutari'
        ]
    
    def validate_musteri_no(self, value):
        """Müşteri numarasının geçerliliğini kontrol et"""
        try:
            musteri = Musteri.objects.get(musteri_no=value, aktif=True)
            return value
        except Musteri.DoesNotExist:
            raise serializers.ValidationError("Geçerli bir müşteri numarası giriniz.")
    
    def validate_aylik_faiz_orani(self, value):
        """Faiz oranı validasyonu"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Faiz oranı 0-100 arasında olmalıdır.")
        return value
    
    def validate_vade(self, value):
        """Vade validasyonu"""
        if value < 1 or value > 600:  # Max 50 yıl
            raise serializers.ValidationError("Vade 1-600 ay arasında olmalıdır.")
        return value
    
    def validate_kredi_tutari(self, value):
        """Kredi tutarı validasyonu"""
        if value <= 0:
            raise serializers.ValidationError("Kredi tutarı 0'dan büyük olmalıdır.")
        return value
    
    def create(self, validated_data):
        logger.info(f"Kredi hesabı oluşturuluyor: {validated_data}")
        
        try:
            # Müşteri numarasını al ve musteri objesini bul
            musteri_no = validated_data.pop('musteri_no')
            musteri = Musteri.objects.get(musteri_no=musteri_no)
            
            # created_by alanını set et
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['created_by'] = getattr(request.user, 'username', 'system')
            
            # Kredi hesabını oluştur
            kredi_hesabi = KrediHesabi.objects.create(
                musteri=musteri,
                **validated_data
            )
            
            # Ödeme planını oluştur
            self.create_payment_schedule(kredi_hesabi)
            
            logger.info(f"Kredi hesabı oluşturuldu: {kredi_hesabi.kredi_hesap_no}")
            return kredi_hesabi
            
        except Exception as e:
            logger.error(f"Kredi oluşturma hatası: {str(e)}")
            raise
    
    def create_payment_schedule(self, kredi_hesabi):
        """Ödeme planını oluştur"""
        logger.info(f"Ödeme planı oluşturuluyor: {kredi_hesabi.kredi_hesap_no}")
        
        kredi_tutari = kredi_hesabi.kredi_tutari
        aylik_faiz_orani = kredi_hesabi.aylik_faiz_orani / 100
        vade = kredi_hesabi.vade
        aylik_odeme = kredi_hesabi.aylik_odeme
        
        kalan_bakiye = kredi_tutari
        base_date = datetime.now().date()
        
        for i in range(1, vade + 1):
            # Bu ayın faizi
            faiz_tutari = kalan_bakiye * aylik_faiz_orani
            # Anapara tutarı
            anapara_tutari = aylik_odeme - faiz_tutari
            # Kalan bakiye güncelleme
            kalan_bakiye = kalan_bakiye - anapara_tutari
            
            # Vade tarihi hesaplama
            vade_tarihi = base_date + timedelta(days=30 * i)
            
            # Son taksitte kalan bakiyeyi sıfırla (yuvarlama hatası için)
            if i == vade:
                kalan_bakiye = Decimal('0.00')
                anapara_tutari = aylik_odeme - faiz_tutari  # Düzeltme
            
            KrediOdemePlanim.objects.create(
                kredi_hesabi=kredi_hesabi,
                taksit_no=i,
                vade_tarihi=vade_tarihi,
                anapara_tutari=round(anapara_tutari, 2),
                faiz_tutari=round(faiz_tutari, 2),
                taksit_tutari=aylik_odeme,
                kalan_bakiye=round(kalan_bakiye, 2)
            )
        
        logger.info(f"Ödeme planı oluşturuldu: {vade} taksit")

class KrediOdemePlaniSerializer(serializers.ModelSerializer):
    class Meta:
        model = KrediOdemePlanim
        fields = '__all__'

class KrediOdemeHareketleriSerializer(serializers.ModelSerializer):
    hareket_turu_display = serializers.CharField(source='get_hareket_turu_display', read_only=True)
    
    class Meta:
        model = KrediOdemeHareketleri
        fields = '__all__'
        read_only_fields = ('hareket_tarihi',)