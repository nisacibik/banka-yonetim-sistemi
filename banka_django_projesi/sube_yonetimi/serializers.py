# serializers.py - Düzeltilmiş versiyon (source parametresi kaldırıldı)
from rest_framework import serializers
from .models import Sube, Il, Ilce

class IlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Il
        fields = ['id', 'il_kodu', 'il_adi']

class IlceSerializer(serializers.ModelSerializer):
    il_adi = serializers.CharField(source='il.il_adi', read_only=True)
    
    class Meta:
        model = Ilce
        fields = ['id', 'ilce_adi', 'il', 'il_adi']

class SubeSerializer(serializers.ModelSerializer):
    # DÜZELTME: il_adi için source parametresi kaldırıldı
    # Çünkü model'de zaten @property olarak tanımlı
    il_adi = serializers.ReadOnlyField()  # Model property'sinden otomatik gelir
    ilce_adi = serializers.CharField(source='ilce.ilce_adi', read_only=True)
    tam_adres = serializers.ReadOnlyField()
    personel_siniri = serializers.ReadOnlyField()
    
    # İl bilgisini sadece görüntüleme için
    il_id = serializers.IntegerField(source='ilce.il.id', read_only=True)
    
    class Meta:
        model = Sube
        fields = [
            'id', 'sube_kodu', 'sube_adi', 'sube_sinifi',
            'ilce', 'ilce_adi', 'il_id', 'il_adi', 'tam_adres',
            'personel_siniri', 'durum', 'kayit_tarihi', 'guncelleme_tarihi'
        ]
        read_only_fields = ['id', 'kayit_tarihi', 'guncelleme_tarihi']

    def validate_sube_kodu(self, value):
        """Şube kodu validasyonu"""
        value = value.strip().upper()
        
        if len(value) < 3:
            raise serializers.ValidationError("Şube kodu en az 3 karakter olmalıdır.")
        
        if len(value) > 10:
            raise serializers.ValidationError("Şube kodu en fazla 10 karakter olmalıdır.")
            
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError("Şube kodu sadece harf, rakam, '-' ve '_' karakterlerini içerebilir.")
        
        return value

class SubeListSerializer(serializers.ModelSerializer):
    # DÜZELTME: il_adi için source parametresi kaldırıldı
    il_adi = serializers.ReadOnlyField()  # Model property'sinden otomatik gelir
    ilce_adi = serializers.CharField(source='ilce.ilce_adi', read_only=True)
    personel_siniri = serializers.ReadOnlyField()
    
    class Meta:
        model = Sube
        fields = [
            'id', 'sube_kodu', 'sube_adi', 'sube_sinifi',
            'il_adi', 'ilce_adi', 'personel_siniri', 'durum',
        ]