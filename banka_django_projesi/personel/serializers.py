from rest_framework import serializers
from django.contrib.auth import get_user_model

Personel = get_user_model()

class PersonelSerializer(serializers.ModelSerializer):
    personel_kodu = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Personel
        fields = ['personel_kodu', 'ad', 'soyad', 'tel_no', 'mail', 'sube_kodu', 'rol', 'password', 'full_name', 'aktif']
        extra_kwargs = {
            'password': {'write_only': True},
            'personel_kodu': {'read_only': True},
        }
    
    def create(self, validated_data):
        personel_kodu = self.generate_next_personel_kodu()
        validated_data['personel_kodu'] = personel_kodu
        
        if 'password' not in validated_data or not validated_data['password']:
            validated_data['password'] = '123456'
        
        password = validated_data.pop('password')
        personel_kodu = validated_data.pop('personel_kodu')
        
        user = Personel.objects.create_user(
            personel_kodu=personel_kodu,
            password=password,
            **validated_data
        )
        return user
    
    def generate_next_personel_kodu(self):
        last_personel = Personel.objects.order_by('personel_kodu').last()
        
        if last_personel and last_personel.personel_kodu.startswith('P'):
            try:
                last_number = int(last_personel.personel_kodu[1:])
                next_number = last_number + 1
            except (ValueError, TypeError):
                next_number = 10001
        else:
            next_number = 10001
        
        new_personel_kodu = f"P{next_number:05d}"
        
        while Personel.objects.filter(personel_kodu=new_personel_kodu).exists():
            next_number += 1
            new_personel_kodu = f"P{next_number:05d}"
        
        return new_personel_kodu