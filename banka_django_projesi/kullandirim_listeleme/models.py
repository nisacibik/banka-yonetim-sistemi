from django.db import models

class KrediRaporu(models.Model):

    hesap_no = models.CharField(max_length=20, unique=True)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    notlar = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Rapor: {self.hesap_no}"
