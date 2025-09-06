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