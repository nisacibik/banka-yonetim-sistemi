from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, personel_kodu, password=None, **extra_fields):
        if not personel_kodu:
            raise ValueError("Personel kodu boş bırakılamaz.")
        
        user = self.model(personel_kodu=personel_kodu, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, personel_kodu, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(personel_kodu, password, **extra_fields)

class Personel(AbstractBaseUser, PermissionsMixin):
    personel_kodu = models.CharField(max_length=20, unique=True, primary_key=True)
    password = models.CharField(max_length=128)
    ad = models.CharField(max_length=50, blank=False)
    soyad = models.CharField(max_length=50, blank=False)
    tel_no = models.CharField(max_length=15, blank=False)
    mail = models.EmailField(max_length=254, blank=False)
    sube_kodu = models.CharField(max_length=20, blank=False)
    rol = models.CharField(max_length=50, blank=False)
    aktif = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = "personel_kodu"

    class Meta:
        db_table = 'personel'

    def __str__(self):
        return f"{self.personel_kodu} - {self.ad} {self.soyad}"
    
    def get_full_name(self):
        return f"{self.ad} {self.soyad}"