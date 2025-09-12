from django.db import models
from django.contrib.auth.models import User

class Kitap(models.Model):
    STATUS_CHOICES = [
        ('okunuyor', 'Şu An Okunuyor'),
        ('bitti', 'Bitirildi'),
    ]
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
    # YENİ EKLENEN ALAN
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.author}"
    
    # YENİ ALAN: Kitap kapağı görselinin URL'ini saklamak için.
    # Bu alan boş olabilir, çünkü her kitap için kapak bulamayabiliriz.
    cover_image_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.author}"

class Not(models.Model):
    kitap = models.ForeignKey(Kitap, on_delete=models.CASCADE, related_name='notlar')
    icerik = models.TextField()
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.kitap.title} - Not: {self.icerik[:50]}..."

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    streak = models.IntegerField(default=0)
    son_okuma_tarihi = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile - Streak: {self.streak}"

# YENİ MODEL: Günlük okuma aktivitesini kaydetmek için
class OkumaGunu(models.Model):
    # Bu kaydın hangi kullanıcıya ait olduğu. Şimdilik null olabilir.
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # Aktivitenin gerçekleştiği tarih.
    tarih = models.DateField()
    # O gün okunan toplam sayfa sayısı.
    okunan_sayfa_sayisi = models.PositiveIntegerField(default=0)

    class Meta:
        # Bir kullanıcı için aynı tarihten birden fazla kayıt olmasını engeller.
        unique_together = ('user', 'tarih')

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonim'} - {self.tarih} - {self.okunan_sayfa_sayisi} sayfa"