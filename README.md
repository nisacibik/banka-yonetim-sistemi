# 🏦 VakıfBank Web Stajı: Banka Yönetim Sistemi

Bu proje, **VakıfBank Web Geliştirme Stajı** süresince mini  bankacılık yönetim sistemi simülasyonu olarak geliştirilmiştir. Proje, modern web teknolojileri kullanılarak hem kullanıcı (müşteri) hem de yönetici (personel) ihtiyaçlarını karşılayacak şekilde tasarlanmıştır.

## 🛠️ Kullanılan Teknolojiler

### Backend (Django)
- **Framework:** Django 4.x
- **Veritabanı:** PostgreSQL (Güvenli ve ölçeklenebilir veri yönetimi için)
- **Güvenlik:** Ortam değişkenleri (`.env`) ile hassas veri yönetimi

### Frontend (React)
- **Kütüphane:** React.js
- **Stil:** CSS3 ve Modern UI yaklaşımları
- **Veri İletişimi:** Axios ile REST API entegrasyonu

## 🚀 Öne Çıkan Özellikler

- **Müşteri Yönetimi:** Yeni müşteri kaydı, hesap açma ve bakiye takibi.
- **Personel Paneli:** Şube ve personel bilgilerinin yönetimi.
- **Hesaplamalar:** Kredi faiz oranları, taksitlendirme ve finansal veri analizi modülleri.
- **Şube Entegrasyonu:** Farklı şubeler arasındaki veri akışının simülasyonu.

## 📂 Proje Yapısı

```text
banka_yonetim_sistemi/
├── banka_django_projesi/   # Django REST Framework Backend
└── banka_frontend_projesi/ # React.js Frontend Uygulaması
