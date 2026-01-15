from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MusteriTemel(models.Model):
    """Ana müşteri tablosu - ortak özellikler"""
    MUSTERI_TURU_CHOICES = [
        ('bireysel', 'Bireysel Müşteri'),
        ('tfgk', 'TFGK (Ticari Faaliyeti Olan Gerçek Kişi)'),
        ('tuzel', 'Tüzel Kişi'),
    ]
    
    musteri_no = models.CharField(max_length=20, unique=True, primary_key=True)
    musteri_turu = models.CharField(max_length=20, choices=MUSTERI_TURU_CHOICES)
    durum_kodu = models.BooleanField(default=True, help_text='Aktif/Pasif durumu')
    vergi_numarasi = models.CharField(max_length=10, blank=True, null=True)
    vergi_dairesi = models.CharField(max_length=100, blank=True, null=True)
    
    # Sistem bilgileri
    created_by = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'musteri_temel'
        verbose_name = 'Müşteri Temel'
        verbose_name_plural = 'Müşteri Temel Bilgileri'
    
    def save(self, *args, **kwargs):
        if not self.musteri_no:
            self.musteri_no = self.generate_musteri_no()
        super().save(*args, **kwargs)
    
    def generate_musteri_no(self):

        last_musteri = MusteriTemel.objects.order_by('musteri_no').last()
        
        if last_musteri and last_musteri.musteri_no.startswith('M'):
            try:
                last_number = int(last_musteri.musteri_no[1:])
                next_number = last_number + 1
            except (ValueError, TypeError):
                next_number = 10001
        else:
            next_number = 10001
        
        new_musteri_no = f"M{next_number:06d}"
        
        while MusteriTemel.objects.filter(musteri_no=new_musteri_no).exists():
            next_number += 1
            new_musteri_no = f"M{next_number:06d}"
        
        return new_musteri_no
    
    def __str__(self):
        return f"{self.musteri_no} - {self.get_musteri_turu_display()}"

class MusteriGercek(models.Model):
    """Gerçek kişi bilgileri - Bireysel ve TFGK için ortak"""
    CINSIYET_CHOICES = [
        ('Erkek', 'Erkek'),
        ('Kadın', 'Kadın'),
    ]
    
    MEDENI_HAL_CHOICES = [
        ('Bekar', 'Bekar'),
        ('Evli', 'Evli'),
        ('Boşanmış', 'Boşanmış'),
        ('Dul', 'Dul'),
    ]
    
    musteri = models.OneToOneField(MusteriTemel, on_delete=models.CASCADE, primary_key=True, related_name='gercek_kisi')
    tckn = models.CharField(max_length=11)
    adi = models.CharField(max_length=50)
    soyadi = models.CharField(max_length=50)
    dogum_tarihi = models.DateField(blank=True, null=True)
    cinsiyet = models.CharField(max_length=10, choices=CINSIYET_CHOICES, blank=True, null=True)
    medeni_hal = models.CharField(max_length=20, choices=MEDENI_HAL_CHOICES, blank=True, null=True)
    meslek = models.CharField(max_length=100, blank=True, null=True)
    
    nace_kodu = models.CharField(max_length=20, blank=True, null=True)
    isletme_unvani = models.CharField(max_length=200, blank=True, null=True)
    is_adresi = models.TextField(blank=True, null=True)
    oda_kaydi = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        db_table = 'musteri_gercek'
        verbose_name = 'Gerçek Kişi'
        verbose_name_plural = 'Gerçek Kişiler'
    
    @property
    def ad_soyad(self):
        return f"{self.adi} {self.soyadi}".strip()
    
    def __str__(self):
        return f"{self.musteri.musteri_no} - {self.ad_soyad}"

class MusteriTuzel(models.Model):
    """Tüzel kişi bilgileri"""
    SIRKET_TURU_CHOICES = [
        ('Limited Şirketi', 'Limited Şirketi'),
        ('Anonim Şirket', 'Anonim Şirket'),
        ('Komandit Şirket', 'Komandit Şirket'),
        ('Kolektif Şirket', 'Kolektif Şirket'),
    ]
    
    musteri = models.OneToOneField(MusteriTemel, on_delete=models.CASCADE, primary_key=True, related_name='tuzel_kisi')
    sirket_unvani = models.CharField(max_length=200)
    sirket_turu = models.CharField(max_length=50, choices=SIRKET_TURU_CHOICES, blank=True, null=True)
    kurulus_tarihi = models.DateField(blank=True, null=True)
    ticaret_sicil_no = models.CharField(max_length=50, blank=True, null=True)
    nace_kodu = models.CharField(max_length=20, blank=True, null=True)
    
    yetkili_adi = models.CharField(max_length=50)
    yetkili_soyadi = models.CharField(max_length=50)
    yetkili_tckn = models.CharField(max_length=11)
    yetkili_gorevi = models.CharField(max_length=100, blank=True, null=True)
    yetkili_temsil_yetkisi = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        db_table = 'musteri_tuzel'
        verbose_name = 'Tüzel Kişi'
        verbose_name_plural = 'Tüzel Kişiler'
    
    @property
    def yetkili_ad_soyad(self):
        return f"{self.yetkili_adi} {self.yetkili_soyadi}".strip()
    
    def __str__(self):
        return f"{self.musteri.musteri_no} - {self.sirket_unvani}"

class MusteriTelefon(models.Model):
    """Müşteri telefon bilgileri"""
    TELEFON_TIPI_CHOICES = [
        ('cep', 'Cep Telefonu'),
        ('ev', 'Ev Telefonu'),
        ('is', 'İş Telefonu'),
        ('diger', 'Diğer'),
    ]
    
    musteri = models.ForeignKey(MusteriTemel, on_delete=models.CASCADE, related_name='telefonlar')
    telefon = models.CharField(max_length=20)
    telefon_tipi = models.CharField(max_length=10, choices=TELEFON_TIPI_CHOICES, default='cep')
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'musteri_telefon'
        verbose_name = 'Müşteri Telefon'
        verbose_name_plural = 'Müşteri Telefonları'
    
    def __str__(self):
        return f"{self.musteri.musteri_no} - {self.telefon}"

class MusteriAdres(models.Model):
    """Müşteri adres bilgileri"""
    ADRES_TIPI_CHOICES = [
        ('ev', 'Ev Adresi'),
        ('is', 'İş Adresi'),
        ('diger', 'Diğer'),
    ]
    
    musteri = models.ForeignKey(MusteriTemel, on_delete=models.CASCADE, related_name='adresler')
    adres = models.TextField()
    adres_tipi = models.CharField(max_length=10, choices=ADRES_TIPI_CHOICES, default='ev')
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'musteri_adres'
        verbose_name = 'Müşteri Adres'
        verbose_name_plural = 'Müşteri Adresleri'
    
    def __str__(self):
        return f"{self.musteri.musteri_no} - {self.get_adres_tipi_display()}"

class MusteriEmail(models.Model):
    """Müşteri email bilgileri"""
    EMAIL_TIPI_CHOICES = [
        ('kisisel', 'Kişisel'),
        ('is', 'İş'),
        ('diger', 'Diğer'),
    ]
    
    musteri = models.ForeignKey(MusteriTemel, on_delete=models.CASCADE, related_name='emailler')
    email = models.EmailField()
    email_tipi = models.CharField(max_length=10, choices=EMAIL_TIPI_CHOICES, default='kisisel')
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'musteri_email'
        verbose_name = 'Müşteri Email'
        verbose_name_plural = 'Müşteri Emailleri'
    
    def __str__(self):
        return f"{self.musteri.musteri_no} - {self.email}"

class MusteriOrtak(models.Model):
    """Tüzel kişi ortakları"""
    musteri = models.ForeignKey(MusteriTuzel, on_delete=models.CASCADE, related_name='ortaklar')
    ad_soyad = models.CharField(max_length=100)
    pay = models.DecimalField(max_digits=5, decimal_places=2, help_text='Yüzde olarak')
    tckn = models.CharField(max_length=11, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'musteri_ortak'
        verbose_name = 'Müşteri Ortağı'
        verbose_name_plural = 'Müşteri Ortakları'
    
    def __str__(self):
        return f"{self.ad_soyad} - %{self.pay}"
