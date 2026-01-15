# banka_projesi/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/personel/', include('personel.urls')),      # Personel CRUD + Login/Logout
    path('api/sube/', include('sube_yonetimi.urls')),     # Şube CRUD
    path('api/musteri/', include('musteri_yonetimi.urls')), # Müşteri CRUD (gelecekte)
    path('api/kredi/', include('kullandirim.urls')),
]