from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Personel
from .serializers import PersonelSerializer
import logging

logger = logging.getLogger(__name__)

class PersonelViewSet(viewsets.ModelViewSet):
    """Personel CRUD API"""
    queryset = Personel.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PersonelSerializer
    
    def list(self, request, *args, **kwargs):
        """Personel listesi - array döndür"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Personel listesi çekildi: {len(serializer.data)} kayıt")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Personel listesi hatası: {str(e)}")
            return Response({
                'error': 'Personel listesi yüklenirken hata oluştu',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        logger.info("Yeni personel kaydı")
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            personel = serializer.save()
            token, created = Token.objects.get_or_create(user=personel)
            
            response_data = PersonelSerializer(personel).data
            response_data['token'] = token.key
            
            logger.info(f"Personel başarıyla kaydedildi: {personel.personel_kodu}")
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def login(self, request):
        """API Login"""
        personel_kodu = request.data.get('personel_kodu')
        password = request.data.get('password')
        
        if personel_kodu and password:
            user = authenticate(username=personel_kodu, password=password)
            if user and user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                logger.info(f"Başarılı giriş: {personel_kodu}")
                return Response({
                    'success': True,
                    'token': token.key,
                    'user': PersonelSerializer(user).data
                })
            else:
                logger.warning(f"Başarısız giriş: {personel_kodu}")
                return Response({
                    'error': 'Geçersiz kullanıcı bilgileri'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'error': 'Personel kodu ve şifre gerekli'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """API Logout"""
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Başarıyla çıkış yapıldı'})
        except:
            return Response({'error': 'Hata oluştu'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Kendi bilgilerimi getir"""
        serializer = PersonelSerializer(request.user)
        return Response(serializer.data)