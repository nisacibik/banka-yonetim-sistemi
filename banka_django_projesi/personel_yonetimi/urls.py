# personel_yonetimi/urls.py - Sadece API
from django.urls import path
from .views import login_view, logout_view

urlpatterns = [
    path('login/', login_view, name='api_login'),
    path('logout/', logout_view, name='api_logout'),
]