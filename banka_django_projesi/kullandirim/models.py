# kredi_yonetimi/models.py
from django.db import models
from musteri_yonetimi.models import MusteriTemel  # Musteri yerine MusteriTemel
from decimal import Decimal

class KrediHesabi(models.Model):
    DOVIZ_CINSI_CHOICES = [
        ('TRY', 'Türk Lirası'),
        ('USD', 'Amerikan Doları'),
        ('EUR', 'Euro'),
        ('GBP', 'İngiliz Sterlini'),
    ]
    
    KREDI_TURU_CHOICES = [
        ('ihtiyac', 'İhtiyaç Kredisi'),
        ('konut', 'Konut Kredisi'),
        ('tasit', 'Taşıt Kredisi'),
    ]
    
    # Temel bilgiler
    kredi_hesap_no = models.CharField(max_length=20, unique=True, primary_key=True)
    musteri = models.ForeignKey(MusteriTemel, on_delete=models.CASCADE, related_name='kredi_hesaplari')  # Düzeltildi
    kredi_turu = models.CharField(max_length=20, choices=KREDI_TURU_CHOICES)
    
    # Kredi detayları
    kredi_tutari = models.DecimalField(max_digits=15, decimal_places=2, help_text='Ana kredi tutarı')
    doviz_cinsi = models.CharField(max_length=3, choices=DOVIZ_CINSI_CHOICES, default='TRY')
    vade = models.PositiveIntegerField(help_text='Vade (ay)')
    aylik_faiz_orani = models.DecimalField(max_digits=5, decimal_places=4, help_text='Aylık faiz oranı (%)')
    masraf_tutari = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Masraf tutarı')
    
    # Hesaplanan değerler
    aylik_odeme = models.DecimalField(max_digits=15, decimal_places=2, help_text='Aylık ödeme tutarı')
    toplam_geri_odeme = models.DecimalField(max_digits=15, decimal_places=2, help_text='Toplam geri ödeme tutarı')
    kalan_anapara = models.DecimalField(max_digits=15, decimal_places=2, help_text='Kalan anapara')
    kalan_vade = models.PositiveIntegerField(help_text='Kalan vade (ay)')
    
    # Durum bilgileri
    aktif = models.BooleanField(default=True)
    acilis_tarihi = models.DateField(auto_now_add=True)
    kapanis_tarihi = models.DateField(null=True, blank=True)
    
    # Sistem bilgileri
    created_by = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kredi_hesabi'
        verbose_name = 'Kredi Hesabı'
        verbose_name_plural = 'Kredi Hesapları'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Hesaplama işlemleri önce yapılmalı
        if self.aylik_faiz_orani == 0:
            self.aylik_odeme = self.kredi_tutari / self.vade
        else:
            faiz_orani = self.aylik_faiz_orani / 100
            carpan = (1 + faiz_orani) ** self.vade
            self.aylik_odeme = (self.kredi_tutari * faiz_orani * carpan) / (carpan - 1)
        
        self.toplam_geri_odeme = (self.aylik_odeme * self.vade) + self.masraf_tutari
        
        # İlk kayıtta kalan anapara ve vadeyi set et
        if not self.pk:
            if not self.kredi_hesap_no:
                self.kredi_hesap_no = self.generate_kredi_hesap_no()
            self.kalan_anapara = self.kredi_tutari
            self.kalan_vade = self.vade
        
        super().save(*args, **kwargs)
    
    def generate_kredi_hesap_no(self):
        # Döviz cinsine göre prefix belirle
        if self.doviz_cinsi == 'TRY':
            prefix = 'TP'
        else:
            prefix = 'YP'  # Yabancı Para
        
        # Son kredi hesap numarasını bul
        last_hesap = KrediHesabi.objects.filter(
            kredi_hesap_no__startswith=prefix
        ).order_by('kredi_hesap_no').last()
        
        if last_hesap:
            try:
                last_number = int(last_hesap.kredi_hesap_no[2:])
                next_number = last_number + 1
            except (ValueError, TypeError):
                next_number = 101 if prefix == 'TP' else 110
        else:
            next_number = 101 if prefix == 'TP' else 110
        
        new_hesap_no = f"{prefix}{next_number}"
        
        # Eğer bu numara zaten varsa bir sonrakini dene
        while KrediHesabi.objects.filter(kredi_hesap_no=new_hesap_no).exists():
            next_number += 1
            new_hesap_no = f"{prefix}{next_number}"
        
        return new_hesap_no
    
    def calculate_monthly_payment(self):
        """Aylık ödeme tutarını hesapla (eşit taksit)"""
        if self.aylik_faiz_orani == 0:
            return self.kredi_tutari / self.vade
        
        faiz_orani = self.aylik_faiz_orani / 100
        aylik_odeme = (self.kredi_tutari * faiz_orani * 
                      (1 + faiz_orani) ** self.vade) / \
                     (((1 + faiz_orani) ** self.vade) - 1)
        
        return round(aylik_odeme, 2)
    
    def calculate_total_payment(self):
        """Toplam geri ödeme tutarını hesapla"""
        return (self.aylik_odeme * self.vade) + self.masraf_tutari
    
    def get_musteri_display_name(self):
        """Müşteri görüntü adını al"""
        if self.musteri.musteri_turu == 'tuzel' and hasattr(self.musteri, 'tuzel_kisi'):
            return self.musteri.tuzel_kisi.sirket_unvani
        elif self.musteri.musteri_turu in ['bireysel', 'tfgk'] and hasattr(self.musteri, 'gercek_kisi'):
            if self.musteri.musteri_turu == 'tfgk' and self.musteri.gercek_kisi.isletme_unvani:
                return self.musteri.gercek_kisi.isletme_unvani
            else:
                return self.musteri.gercek_kisi.ad_soyad
        return 'Belirtilmemiş'
    
    def __str__(self):
        return f"{self.kredi_hesap_no} - {self.get_musteri_display_name()}"  # Düzeltildi


class KrediOdemePlanim(models.Model):
    """Kredi ödeme planı - her taksit için detay"""
    kredi_hesabi = models.ForeignKey(KrediHesabi, on_delete=models.CASCADE, related_name='odeme_plani')
    taksit_no = models.PositiveIntegerField()
    vade_tarihi = models.DateField()
    anapara_tutari = models.DecimalField(max_digits=15, decimal_places=2)
    faiz_tutari = models.DecimalField(max_digits=15, decimal_places=2)
    taksit_tutari = models.DecimalField(max_digits=15, decimal_places=2)
    kalan_bakiye = models.DecimalField(max_digits=15, decimal_places=2)
    odendi_mi = models.BooleanField(default=False)
    odeme_tarihi = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'kredi_odeme_plani'
        verbose_name = 'Ödeme Planı'
        verbose_name_plural = 'Ödeme Planları'
        ordering = ['taksit_no']
        unique_together = ['kredi_hesabi', 'taksit_no']
    
    def __str__(self):
        return f"{self.kredi_hesabi.kredi_hesap_no} - Taksit {self.taksit_no}"


class KrediOdemeHareketleri(models.Model):
    """Kredi ödeme hareketleri"""
    HAREKET_TURU_CHOICES = [
        ('odeme', 'Taksit Ödemesi'),
        ('erken_odeme', 'Erken Ödeme'),
        ('gecikme_faizi', 'Gecikme Faizi'),
        ('masraf', 'Masraf'),
    ]
    
    kredi_hesabi = models.ForeignKey(KrediHesabi, on_delete=models.CASCADE, related_name='hareketler')
    hareket_tarihi = models.DateTimeField(auto_now_add=True)
    hareket_turu = models.CharField(max_length=20, choices=HAREKET_TURU_CHOICES)
    tutar = models.DecimalField(max_digits=15, decimal_places=2)
    aciklama = models.TextField(blank=True)
    taksit_no = models.PositiveIntegerField(null=True, blank=True)
    
    # İşlem yapan personel
    islem_yapan = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'kredi_odeme_hareketleri'
        verbose_name = 'Kredi Hareketi'
        verbose_name_plural = 'Kredi Hareketleri'
        ordering = ['-hareket_tarihi']
    
    def __str__(self):
        return f"{self.kredi_hesabi.kredi_hesap_no} - {self.get_hareket_turu_display()}"