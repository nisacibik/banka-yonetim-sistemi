from rest_framework import serializers
from .models import (
    MusteriTemel, MusteriGercek, MusteriTuzel, MusteriTelefon, 
    MusteriAdres, MusteriEmail, MusteriOrtak
)
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class MusteriTelefonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusteriTelefon
        fields = ['id', 'telefon', 'telefon_tipi', 'aktif']

class MusteriAdresSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusteriAdres
        fields = ['id', 'adres', 'adres_tipi', 'aktif']

class MusteriEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusteriEmail
        fields = ['id', 'email', 'email_tipi', 'aktif']

class MusteriOrtakSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusteriOrtak
        fields = ['id', 'ad_soyad', 'pay', 'tckn', 'created_at']

class MusteriGercekSerializer(serializers.ModelSerializer):

    ad_soyad = serializers.CharField(read_only=True)
    
    class Meta:
        model = MusteriGercek
        fields = [
            'tckn', 'adi', 'soyadi', 'ad_soyad', 'dogum_tarihi', 
            'cinsiyet', 'medeni_hal', 'meslek', 'nace_kodu', 
            'isletme_unvani', 'is_adresi', 'oda_kaydi'
        ]

class MusteriTuzelSerializer(serializers.ModelSerializer):

    yetkili_ad_soyad = serializers.CharField(read_only=True)
    ortaklar = MusteriOrtakSerializer(many=True, read_only=True)
    
    class Meta:
        model = MusteriTuzel
        fields = [
            'sirket_unvani', 'sirket_turu', 'kurulus_tarihi', 
            'ticaret_sicil_no', 'nace_kodu', 'yetkili_adi', 'yetkili_soyadi',
            'yetkili_ad_soyad', 'yetkili_tckn', 'yetkili_gorevi', 
            'yetkili_temsil_yetkisi', 'ortaklar'
        ]



class MusteriSerializer(serializers.ModelSerializer):
    """Tam müşteri bilgisi - okuma için"""
    gercek_kisi = MusteriGercekSerializer(read_only=True)
    tuzel_kisi = MusteriTuzelSerializer(read_only=True)
    telefonlar = MusteriTelefonSerializer(many=True, read_only=True)
    adresler = MusteriAdresSerializer(many=True, read_only=True)
    emailler = MusteriEmailSerializer(many=True, read_only=True)
    
    display_name = serializers.SerializerMethodField()
    musteri_turu_display = serializers.CharField(source='get_musteri_turu_display', read_only=True)
    
    class Meta:
        model = MusteriTemel
        fields = [
            'musteri_no', 'musteri_turu', 'musteri_turu_display', 'durum_kodu',
            'vergi_numarasi', 'vergi_dairesi', 'display_name', 'created_by',
            'created_at', 'updated_at', 'gercek_kisi', 'tuzel_kisi',
            'telefonlar', 'adresler', 'emailler' 
        ]

        
    
    def get_display_name(self, obj):
        if obj.musteri_turu == 'tuzel' and hasattr(obj, 'tuzel_kisi'):
            return obj.tuzel_kisi.sirket_unvani
        elif obj.musteri_turu in ['bireysel', 'tfgk'] and hasattr(obj, 'gercek_kisi'):
            if obj.musteri_turu == 'tfgk' and obj.gercek_kisi.isletme_unvani:
                return obj.gercek_kisi.isletme_unvani
            return obj.gercek_kisi.ad_soyad
        return 'Belirtilmemiş'

class MusteriListSerializer(serializers.ModelSerializer):
    """Liste görünümü için hafif serializer"""
    display_name = serializers.SerializerMethodField()
    musteri_turu_display = serializers.CharField(source='get_musteri_turu_display', read_only=True)
    telefon = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = MusteriTemel
        fields = [
            'musteri_no', 'musteri_turu', 'musteri_turu_display', 
            'display_name', 'telefon', 'email', 'durum_kodu', 'created_at'
        ]
    
    def get_display_name(self, obj):
        if obj.musteri_turu == 'tuzel' and hasattr(obj, 'tuzel_kisi'):
            return obj.tuzel_kisi.sirket_unvani
        elif obj.musteri_turu in ['bireysel', 'tfgk'] and hasattr(obj, 'gercek_kisi'):
            if obj.musteri_turu == 'tfgk' and obj.gercek_kisi.isletme_unvani:
                return obj.gercek_kisi.isletme_unvani
            return obj.gercek_kisi.ad_soyad
        return 'Belirtilmemiş'
    
    def get_telefon(self, obj):
        first_phone = obj.telefonlar.filter(aktif=True).first()
        return first_phone.telefon if first_phone else ''
    
    def get_email(self, obj):
        first_email = obj.emailler.filter(aktif=True).first()
        return first_email.email if first_email else ''

class MusteriCreateSerializer(serializers.Serializer):
    """Müşteri oluşturma için kompleks serializer"""

    musteri_turu = serializers.ChoiceField(choices=MusteriTemel.MUSTERI_TURU_CHOICES)
    vergi_numarasi = serializers.CharField(max_length=10, required=False, allow_blank=True)
    vergi_dairesi = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    tckn = serializers.CharField(max_length=11, required=False, allow_blank=True)
    adi = serializers.CharField(max_length=50, required=False, allow_blank=True)
    soyadi = serializers.CharField(max_length=50, required=False, allow_blank=True)
    ad_soyad = serializers.CharField(max_length=100, required=False, allow_blank=True)  
    dogum_tarihi = serializers.DateField(required=False, allow_null=True)
    cinsiyet = serializers.ChoiceField(choices=MusteriGercek.CINSIYET_CHOICES, required=False, allow_blank=True)
    medeni_hal = serializers.ChoiceField(choices=MusteriGercek.MEDENI_HAL_CHOICES, required=False, allow_blank=True)
    meslek = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    nace_kodu = serializers.CharField(max_length=20, required=False, allow_blank=True)
    isletme_unvani = serializers.CharField(max_length=200, required=False, allow_blank=True)
    is_adresi = serializers.CharField(required=False, allow_blank=True)
    oda_kaydi = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    sirket_unvani = serializers.CharField(max_length=200, required=False, allow_blank=True)
    sirket_turu = serializers.ChoiceField(choices=MusteriTuzel.SIRKET_TURU_CHOICES, required=False, allow_blank=True)
    kurulus_tarihi = serializers.DateField(required=False, allow_null=True)
    ticaret_sicil_no = serializers.CharField(max_length=50, required=False, allow_blank=True)
    sirket_nace_kodu = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    yetkili_adi = serializers.CharField(max_length=50, required=False, allow_blank=True)
    yetkili_soyadi = serializers.CharField(max_length=50, required=False, allow_blank=True)
    yetkili_ad_soyad = serializers.CharField(max_length=100, required=False, allow_blank=True)  
    yetkili_tckn = serializers.CharField(max_length=11, required=False, allow_blank=True)
    yetkili_gorevi = serializers.CharField(max_length=100, required=False, allow_blank=True)
    yetkili_temsil_yetkisi = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    telefon = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    adres = serializers.CharField(required=False, allow_blank=True)
    
    telefonlar = serializers.ListField(
        child=serializers.DictField(), required=False, allow_empty=True
    )
    emailler = serializers.ListField(
        child=serializers.DictField(), required=False, allow_empty=True
    )
    adresler = serializers.ListField(
        child=serializers.DictField(), required=False, allow_empty=True
    )
    
    ortaklar = serializers.ListField(
        child=serializers.DictField(), required=False, allow_empty=True
    )
    
    def validate(self, data):
        musteri_turu = data.get('musteri_turu')
        logger.info(f"Validation başlıyor - Müşteri türü: {musteri_turu}")
        
        if musteri_turu == 'bireysel':
 
            required_fields = ['tckn']
            if data.get('ad_soyad') and not (data.get('adi') or data.get('soyadi')):
                ad_soyad_parts = data['ad_soyad'].strip().split(' ', 1)
                data['adi'] = ad_soyad_parts[0]
                data['soyadi'] = ad_soyad_parts[1] if len(ad_soyad_parts) > 1 else ''
            
            if not (data.get('adi') and data.get('soyadi')):
                raise serializers.ValidationError({'ad_soyad': 'Ad ve soyad bilgisi gereklidir.'})
            
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: f'{field} alanı bireysel müşteri için zorunludur.'})
        
        elif musteri_turu == 'tfgk':
            required_fields = ['tckn', 'vergi_numarasi', 'vergi_dairesi']
            if data.get('ad_soyad') and not (data.get('adi') or data.get('soyadi')):
                ad_soyad_parts = data['ad_soyad'].strip().split(' ', 1)
                data['adi'] = ad_soyad_parts[0]
                data['soyadi'] = ad_soyad_parts[1] if len(ad_soyad_parts) > 1 else ''
            
            if not (data.get('adi') and data.get('soyadi')):
                raise serializers.ValidationError({'ad_soyad': 'Ad ve soyad bilgisi gereklidir.'})
            
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: f'{field} alanı TFGK için zorunludur.'})
        
        elif musteri_turu == 'tuzel':
       
            required_fields = ['sirket_unvani', 'vergi_numarasi', 'vergi_dairesi', 'yetkili_tckn']
            if data.get('yetkili_ad_soyad') and not (data.get('yetkili_adi') or data.get('yetkili_soyadi')):
                yetkili_parts = data['yetkili_ad_soyad'].strip().split(' ', 1)
                data['yetkili_adi'] = yetkili_parts[0]
                data['yetkili_soyadi'] = yetkili_parts[1] if len(yetkili_parts) > 1 else ''
            
            if not (data.get('yetkili_adi') and data.get('yetkili_soyadi')):
                raise serializers.ValidationError({'yetkili_ad_soyad': 'Yetkili ad ve soyad bilgisi gereklidir.'})
            
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: f'{field} alanı tüzel kişi için zorunludur.'})
        
        logger.info("Validation başarılı")
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        logger.info(f"Müşteri kayıt işlemi başlıyor: {validated_data.get('musteri_turu')}")
        
        request = self.context.get('request')
        created_by = 'Unknown'
        if request and hasattr(request, 'user'):
            if hasattr(request.user, 'personel_kodu'):
                created_by = request.user.personel_kodu
            else:
                created_by = getattr(request.user, 'username', 'Unknown')
        
        musteri_turu = validated_data['musteri_turu']
        
        musteri_temel = MusteriTemel.objects.create(
            musteri_turu=musteri_turu,
            durum_kodu=True,
            vergi_numarasi=validated_data.get('vergi_numarasi'),
            vergi_dairesi=validated_data.get('vergi_dairesi'),
            created_by=created_by
        )
        logger.info(f"Müşteri temel kaydedildi: {musteri_temel.musteri_no}")
        
        if musteri_turu in ['bireysel', 'tfgk']:
            gercek_kisi = MusteriGercek.objects.create(
                musteri=musteri_temel,
                tckn=validated_data.get('tckn'),
                adi=validated_data.get('adi'),
                soyadi=validated_data.get('soyadi'),
                dogum_tarihi=validated_data.get('dogum_tarihi'),
                cinsiyet=validated_data.get('cinsiyet'),
                medeni_hal=validated_data.get('medeni_hal'),
                meslek=validated_data.get('meslek'),

                nace_kodu=validated_data.get('nace_kodu') if musteri_turu == 'tfgk' else None,
                isletme_unvani=validated_data.get('isletme_unvani') if musteri_turu == 'tfgk' else None,
                is_adresi=validated_data.get('is_adresi') if musteri_turu == 'tfgk' else None,
                oda_kaydi=validated_data.get('oda_kaydi') if musteri_turu == 'tfgk' else None,
            )
            logger.info(f"Gerçek kişi kaydedildi: {gercek_kisi.ad_soyad}")
        
        elif musteri_turu == 'tuzel':
            tuzel_kisi = MusteriTuzel.objects.create(
                musteri=musteri_temel,
                sirket_unvani=validated_data.get('sirket_unvani'),
                sirket_turu=validated_data.get('sirket_turu'),
                kurulus_tarihi=validated_data.get('kurulus_tarihi'),
                ticaret_sicil_no=validated_data.get('ticaret_sicil_no'),
                nace_kodu=validated_data.get('sirket_nace_kodu'),
                yetkili_adi=validated_data.get('yetkili_adi'),
                yetkili_soyadi=validated_data.get('yetkili_soyadi'),
                yetkili_tckn=validated_data.get('yetkili_tckn'),
                yetkili_gorevi=validated_data.get('yetkili_gorevi'),
                yetkili_temsil_yetkisi=validated_data.get('yetkili_temsil_yetkisi'),
            )
            logger.info(f"Tüzel kişi kaydedildi: {tuzel_kisi.sirket_unvani}")
            
            ortaklar_data = validated_data.get('ortaklar', [])
            for ortak_data in ortaklar_data:
                ad_soyad = ortak_data.get('adSoyad') or ortak_data.get('ad_soyad')
                pay = ortak_data.get('pay')
                tckn = ortak_data.get('tckn', '')
                
                if ad_soyad and pay:
                    try:
                        MusteriOrtak.objects.create(
                            musteri=tuzel_kisi,
                            ad_soyad=ad_soyad,
                            pay=float(pay),
                            tckn=tckn
                        )
                        logger.info(f"Ortak kaydedildi: {ad_soyad}")
                    except Exception as e:
                        logger.error(f"Ortak kayıt hatası: {str(e)}")
        self._create_iletisim_bilgileri(musteri_temel, validated_data)
        
        return musteri_temel
    
    def _create_iletisim_bilgileri(self, musteri, validated_data):
        """İletişim bilgilerini oluştur"""
        telefonlar = validated_data.get('telefonlar', [])
      
        if validated_data.get('telefon') and not telefonlar:
            telefonlar = [{'telefon': validated_data['telefon'], 'telefon_tipi': 'cep'}]
        
        for telefon_data in telefonlar:
            if telefon_data.get('telefon'):
                MusteriTelefon.objects.create(
                    musteri=musteri,
                    telefon=telefon_data['telefon'],
                    telefon_tipi=telefon_data.get('telefon_tipi', 'cep'),
                    aktif=True
                )
        emailler = validated_data.get('emailler', [])
        if validated_data.get('email') and not emailler:
            emailler = [{'email': validated_data['email'], 'email_tipi': 'kisisel'}]
        
        for email_data in emailler:
            if email_data.get('email'):
                MusteriEmail.objects.create(
                    musteri=musteri,
                    email=email_data['email'],
                    email_tipi=email_data.get('email_tipi', 'kisisel'),
                    aktif=True
                )

        adresler = validated_data.get('adresler', [])
        if validated_data.get('adres') and not adresler:
            adresler = [{'adres': validated_data['adres'], 'adres_tipi': 'ev'}]
        
        for adres_data in adresler:
            if adres_data.get('adres'):
                MusteriAdres.objects.create(
                    musteri=musteri,
                    adres=adres_data['adres'],
                    adres_tipi=adres_data.get('adres_tipi', 'ev'),
                    aktif=True
                )