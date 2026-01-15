from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from personel.models import Personel
from personel.serializers import PersonelSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """API Login endpoint"""
    personel_kodu = request.data.get('personel_kodu')
    password = request.data.get('password') or request.data.get('sifre')
    
    if not personel_kodu or not password:
        return Response({
            'success': False,
            'message': 'Personel kodu ve şifre gerekli'
        }, status=status.HTTP_400_BAD_REQUEST)
   
    user = authenticate(username=personel_kodu, password=password)  
    if user and user.is_active:
        token, created = Token.objects.get_or_create(user=user)
        logger.info(f"Başarılı giriş: {personel_kodu}") 
        return Response({
            'success': True,
            'message': 'Giriş başarılı',
            'token': token.key,
            'user': PersonelSerializer(user).data
        })
    else:
        logger.warning(f"Başarısız giriş denemesi: {personel_kodu}")
        return Response({
            'success': False,
            'message': 'Kullanıcı adı veya şifre hatalı'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_view(request):
    """API Logout endpoint"""
    try:
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        return Response({
            'success': True,
            'message': 'Başarıyla çıkış yapıldı'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Çıkış işlemi başarısız'
        }, status=status.HTTP_400_BAD_REQUEST)