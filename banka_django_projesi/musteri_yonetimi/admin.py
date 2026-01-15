from django.contrib import admin
from .models import Musteri, MusteriOrtak, MusteriNotlari

class MusteriOrtakInline(admin.TabularInline):
    model = MusteriOrtak
    extra = 1
    fields = ['ad_soyad', 'pay', 'tckn']

class MusteriNotlariInline(admin.TabularInline):
    model = MusteriNotlari
    extra = 0
    fields = ['not_baslik', 'not_icerik', 'olusturan']
    readonly_fields = ['olusturan', 'created_at']

@admin.register(Musteri)
class MusteriAdmin(admin.ModelAdmin):
    list_display = [
        'musteri_no', 
        'get_display_name', 
        'musteri_turu', 
        'telefon', 
        'aktif_durum', 
        'created_at'
    ]
    list_filter = [
        'musteri_turu', 
        'aktif_durum', 
        'cinsiyet', 
        'medeni_hal', 
        'calisma_durumu',
        'created_at'
    ]
    search_fields = [
        'musteri_no',
        'ad_soyad', 
        'sirket_unvani', 
        'isletme_unvani', 
        'tckn', 
        'telefon', 
        'email'
    ]
    readonly_fields = [
        'musteri_no', 
        'created_at', 
        'updated_at', 
        'created_by'
    ]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': (
                'musteri_no', 
                'musteri_turu', 
                'aktif_durum', 
                'created_by'
            )
        }),
        ('Kişisel Bilgiler', {
            'fields': (
                'tckn', 
                'ad_soyad', 
                'dogum_tarihi', 
                'cinsiyet', 
                'medeni_hal', 
                'uyrugu'
            ),
            'classes': ['collapse']
        }),
        ('İletişim Bilgileri', {
            'fields': (
                'telefon', 
                'email', 
                'adres'
            )
        }),
        ('Bireysel Müşteri Bilgileri', {
            'fields': (
                'meslek', 
                'gelir_durumu', 
                'calisma_durumu'
            ),
            'classes': ['collapse']
        }),
        ('Ticari Bilgiler', {
            'fields': (
                'vergi_numarasi', 
                'vergi_dairesi', 
                'faaliyet_turu', 
                'nace_kodu'
            ),
            'classes': ['collapse']
        }),
        ('TFGK Bilgileri', {
            'fields': (
                'isletme_unvani', 
                'is_yeri_adresi', 
                'ticaret_sicil_no', 
                'oda_kaydi'
            ),
            'classes': ['collapse']
        }),
        ('Tüzel Kişi Bilgileri', {
            'fields': (
                'sirket_unvani', 
                'sirket_vergi_numarasi', 
                'sirket_vergi_dairesi',
                'sirket_turu', 
                'sirket_ticaret_sicil_no', 
                'kurulus_tarihi',
                'sirket_faaliyet_alani', 
                'sirket_nace_kodu', 
                'sirket_sermaye',
                'merkez_adres', 
                'sirket_telefon', 
                'sirket_email'
            ),
            'classes': ['collapse']
        }),
        ('Yetkili Bilgileri', {
            'fields': (
                'yetkili_ad_soyad', 
                'yetkili_tckn', 
                'yetkili_gorev', 
                'yetkili_temsil_yetkisi'
            ),
            'classes': ['collapse']
        }),
        ('Sistem Bilgileri', {
            'fields': (
                'created_at', 
                'updated_at'
            ),
            'classes': ['collapse']
        }),
    )
    
    inlines = [MusteriOrtakInline, MusteriNotlariInline]
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Müşteri Adı'

@admin.register(MusteriOrtak)
class MusteriOrtakAdmin(admin.ModelAdmin):
    list_display = ['musteri', 'ad_soyad', 'pay', 'tckn']
    list_filter = ['musteri__musteri_turu']
    search_fields = ['ad_soyad', 'tckn', 'musteri__musteri_no', 'musteri__sirket_unvani']

@admin.register(MusteriNotlari)
class MusteriNotlariAdmin(admin.ModelAdmin):
    list_display = ['musteri', 'not_baslik', 'olusturan', 'created_at']
    list_filter = ['created_at', 'olusturan']
    search_fields = ['not_baslik', 'not_icerik', 'musteri__musteri_no']
    readonly_fields = ['created_at']
