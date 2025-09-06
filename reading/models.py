# reading/models.py

from django.db import models
from django.contrib.auth.models import User

class Kitap(models.Model):
    STATUS_CHOICES = [
        ('okunuyor', 'Şu An Okunuyor'),
        ('bitti', 'Bitirildi'),
    ]

    # Bu alanı, geliştirme sürecini kolaylaştırmak için
    # boş bırakılabilir (nullable) yapmıştık.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kitaplar', null=True, blank=True)

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    total_pages = models.PositiveIntegerField()
    current_page = models.PositiveIntegerField(default=0)
    
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='okunuyor'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.author}"

class Not(models.Model):
    # Her not, bir kitaba ait olmalı.
    # Kitap silinirse, o kitaba ait tüm notlar da silinir (on_delete=models.CASCADE).
    # 'related_name="notlar"', bir Kitap nesnesi üzerinden .notlar diyerek
    # o kitaba ait tüm notlara kolayca erişmemizi sağlar.
    kitap = models.ForeignKey(Kitap, on_delete=models.CASCADE, related_name='notlar')
    
    # Notun metin içeriği.
    icerik = models.TextField()
    
    # Notun oluşturulduğu tarihi otomatik olarak kaydeder.
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Admin panelinde notun ilk 50 karakteriyle görünmesini sağlar.
        return f"{self.kitap.title} - Not: {self.icerik[:50]}..."

class Profile(models.Model):
    # Her profil, Django'nun dahili User modeline birebir bağlı olacak.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Kullanıcının art arda okuma yaptığı gün sayısı.
    streak = models.IntegerField(default=0)
    
    # Kullanıcının en son ne zaman bir kitabın sayfasını güncellediği.
    # Bu alan, serinin devam edip etmediğini kontrol etmek için kullanılacak.
    son_okuma_tarihi = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile - Streak: {self.streak}"