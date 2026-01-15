from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    personel_kodu = serializers.CharField(
        max_length=20,
        required=True,
        error_messages={
            'required': 'Personel kodu gereklidir.',
            'blank': 'Personel kodu boş bırakılamaz.'
        }
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'required': 'Şifre gereklidir.',
            'blank': 'Şifre boş bırakılamaz.'
        }
    )