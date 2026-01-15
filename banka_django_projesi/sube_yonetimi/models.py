# models.py - Düzeltilmiş İl/İlçe ilişkili versiyon
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Il(models.Model):
    """İl tablosu"""
    il_kodu = models.CharField(max_length=2, unique=True)  # "06", "34" vs.
    il_adi = models.CharField(max_length=50, unique=True)  # "Ankara", "İstanbul"
    
    class Meta:
        db_table = 'il'
        verbose_name = 'İl'
        verbose_name_plural = 'İller'
        ordering = ['il_adi']

    def __str__(self):
        return self.il_adi

class Ilce(models.Model):
    """İlçe tablosu - İl'e bağlı"""
    il = models.ForeignKey(Il, on_delete=models.CASCADE, related_name='ilceler')
    ilce_adi = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'ilce'
        verbose_name = 'İlçe'
        verbose_name_plural = 'İlçeler'
        ordering = ['ilce_adi']
        unique_together = ['il', 'ilce_adi']  # Aynı ilde aynı ilçe adı olmasın

    def __str__(self):
        return f"{self.il.il_adi} / {self.ilce_adi}"

class Sube(models.Model):
    SUBE_SINIFI_CHOICES = [
        ('1', '1. Sınıf (Büyük) - 25 Personel'),
        ('2', '2. Sınıf (Orta) - 15 Personel'),
        ('3', '3. Sınıf (Küçük) - 8 Personel'),
    ]
    
    DURUM_CHOICES = [
        ('A', 'Aktif'),
        ('P', 'Pasif'),
    ]

    # Kullanıcının girdiği şube kodu
    sube_kodu = models.CharField(
        max_length=10,
        unique=True,
        help_text="Şube kodu (kullanıcı girecek, örn: ANK001)"
    )
    sube_adi = models.CharField(max_length=200)
    sube_sinifi = models.CharField(max_length=1, choices=SUBE_SINIFI_CHOICES)
    
    # SADECE İLÇE İLİŞKİSİ - İl bilgisi ilçe üzerinden gelecek
    ilce = models.ForeignKey(Ilce, on_delete=models.PROTECT, related_name='subeler')
    
    durum = models.CharField(max_length=1, choices=DURUM_CHOICES, default='A')
    kayit_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sube'
        verbose_name = 'Şube'
        verbose_name_plural = 'Şubeler'
        ordering = ['sube_kodu']

    def __str__(self):
        return f"{self.sube_kodu} - {self.sube_adi}"

    @property
    def il(self):
        """İl bilgisini ilçe üzerinden al"""
        return self.ilce.il if self.ilce else None
    
    @property
    def il_adi(self):
        """İl adını property olarak döndür"""
        return self.ilce.il.il_adi if self.ilce and self.ilce.il else None

    @property
    def personel_siniri(self):
        sinir_map = {'1': 25, '2': 15, '3': 8}
        return sinir_map.get(self.sube_sinifi, 10)

    @property
    def tam_adres(self):
        return f"{self.il_adi} / {self.ilce.ilce_adi}" if self.ilce else None