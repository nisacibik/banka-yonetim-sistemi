# musteri_yonetimi/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from decimal import Decimal

class KrediTuru(models.TextChoices):
    """Kredi türleri için enum"""
    BIREYSEL = 'bireysel', 'Bireysel Kredi'
    KONUT = 'konut', 'Konut Kredisi'
    TASIT = 'tasit', 'Taşıt Kredisi'

class KrediHesaplama(models.Model):
    """Kredi hesaplama kayıtlarını tutan model"""
    
    # Kredi bilgileri
    kredi_turu = models.CharField(
        max_length=20,
        choices=KrediTuru.choices,
        default=KrediTuru.BIREYSEL,
        verbose_name="Kredi Türü"
    )
    
    kredi_tutari = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1000.00'))],
        verbose_name="Kredi Tutarı (TL)"
    )
    
    vade_ay = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(360)],
        verbose_name="Vade (Ay)"
    )
    
    faiz_orani = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('99.99'))],
        verbose_name="Faiz Oranı (%)"
    )
    
    # Hesaplama sonuçları
    aylik_taksit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Aylık Taksit (TL)"
    )
    
    toplam_odeme = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Toplam Ödeme (TL)"
    )
    
    toplam_faiz = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Toplam Faiz (TL)"
    )
    
    # Meta bilgiler
    hesaplama_tarihi = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Hesaplama Tarihi"
    )
    
    ip_adresi = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Adresi"
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="Tarayıcı Bilgisi"
    )
    
    # Ek hesaplama detayları (JSON formatında)
    hesaplama_detaylari = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Hesaplama Detayları"
    )
    
    class Meta:
        verbose_name = "Kredi Hesaplama"
        verbose_name_plural = "Kredi Hesaplamaları"
        ordering = ['-hesaplama_tarihi']
        indexes = [
            models.Index(fields=['kredi_turu', 'hesaplama_tarihi']),
            models.Index(fields=['hesaplama_tarihi']),
        ]
    
    def __str__(self):
        return f"{self.get_kredi_turu_display()} - {self.kredi_tutari} TL - {self.hesaplama_tarihi.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def faiz_yuzdesi(self):
        """Faiz oranını yüzde olarak döndürür"""
        return float(self.faiz_orani)
    
    @property
    def aylik_faiz_orani(self):
        """Aylık faiz oranını döndürür"""
        return float(self.faiz_orani) / 100 / 12
    
    def to_dict(self):
        """Model instance'ını dictionary'ye çevirir"""
        return {
            'id': self.id,
            'kredi_turu': self.kredi_turu,
            'kredi_turu_display': self.get_kredi_turu_display(),
            'kredi_tutari': float(self.kredi_tutari),
            'vade_ay': self.vade_ay,
            'faiz_orani': float(self.faiz_orani),
            'aylik_taksit': float(self.aylik_taksit),
            'toplam_odeme': float(self.toplam_odeme),
            'toplam_faiz': float(self.toplam_faiz),
            'hesaplama_tarihi': self.hesaplama_tarihi.isoformat(),
            'hesaplama_detaylari': self.hesaplama_detaylari
        }

class KrediFaizOrani(models.Model):
    """Kredi türlerine göre güncel faiz oranlarını tutan model"""
    
    kredi_turu = models.CharField(
        max_length=20,
        choices=KrediTuru.choices,
        unique=True,
        verbose_name="Kredi Türü"
    )
    
    min_faiz_orani = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Minimum Faiz Oranı (%)"
    )
    
    max_faiz_orani = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Maksimum Faiz Oranı (%)"
    )
    
    varsayilan_faiz_orani = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Varsayılan Faiz Oranı (%)"
    )
    
    min_tutar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('1000.00'),
        verbose_name="Minimum Tutar (TL)"
    )
    
    max_tutar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('500000.00'),
        verbose_name="Maksimum Tutar (TL)"
    )
    
    min_vade_ay = models.PositiveIntegerField(
        default=6,
        verbose_name="Minimum Vade (Ay)"
    )
    
    max_vade_ay = models.PositiveIntegerField(
        default=120,
        verbose_name="Maksimum Vade (Ay)"
    )
    
    aktif = models.BooleanField(
        default=True,
        verbose_name="Aktif"
    )
    
    guncelleme_tarihi = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncelleme Tarihi"
    )
    
    class Meta:
        verbose_name = "Kredi Faiz Oranı"
        verbose_name_plural = "Kredi Faiz Oranları"
    
    def __str__(self):
        return f"{self.get_kredi_turu_display()} - %{self.varsayilan_faiz_orani}"
    
    @classmethod
    def get_faiz_bilgisi(cls, kredi_turu):
        """Kredi türüne göre faiz bilgisini döndürür"""
        try:
            return cls.objects.get(kredi_turu=kredi_turu, aktif=True)
        except cls.DoesNotExist:
            return None
    
    def to_dict(self):
        """Model instance'ını dictionary'ye çevirir"""
        return {
            'kredi_turu': self.kredi_turu,
            'kredi_turu_display': self.get_kredi_turu_display(),
            'min_faiz_orani': float(self.min_faiz_orani),
            'max_faiz_orani': float(self.max_faiz_orani),
            'varsayilan_faiz_orani': float(self.varsayilan_faiz_orani),
            'min_tutar': float(self.min_tutar),
            'max_tutar': float(self.max_tutar),
            'min_vade_ay': self.min_vade_ay,
            'max_vade_ay': self.max_vade_ay
        }
