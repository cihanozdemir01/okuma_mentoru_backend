# reading/serializers.py

from rest_framework import serializers
from .models import Kitap, Not
from django.utils import timezone

class KitapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kitap
        fields = [
            'id', 
            'user', 
            'title', 
            'author', 
            'total_pages', 
            'current_page', 
            'status',
            'created_at'
        ]
        # user alanını API'den gelen veriyle değiştiremezsin,
        # sadece okunabilir.
        read_only_fields = ['user']

class NotSerializer(serializers.ModelSerializer):
    # 1. Yeni bir alan tanımlıyoruz. Bu, modeldeki bir alana bağlı değil.
    #    Bu alanın değerini aşağıdaki 'get_...' metodu belirleyecek.
    olusturma_tarihi_formatli = serializers.SerializerMethodField()

    class Meta:
        model = Not
        # 2. 'fields' listesine yeni alanımızı ekleyip, eskisini çıkaralım.
        fields = ['id', 'kitap', 'icerik', 'olusturma_tarihi_formatli']
        read_only_fields = ['kitap']

    # 3. 'get_<alan_adi>' formatında bir metot tanımlıyoruz.
    #    Bu metot, 'olusturma_tarihi_formatli' alanının değerini hesaplar.
    def get_olusturma_tarihi_formatli(self, obj):
        # Veritabanından gelen UTC zamanını al (obj.olusturma_tarihi)
        # ve onu sunucunun aktif saat dilimine (settings.TIME_ZONE) çevir.
        # Şimdilik en basit haliyle yapalım.
        # Django'nun kendi formatlama aracını kullanalım.
        
        # UTC zamanını al
        utc_time = obj.olusturma_tarihi
        
        # Türkiye saat dilimine (UTC+3) çevir
        # Not: Bu basit bir +3 saat eklemesidir, yaz/kış saati uygulamasını
        # dikkate almaz ama bizim durumumuz için yeterlidir.
        local_time = utc_time + timezone.timedelta(hours=3)
        
        # İstediğimiz formatta string'e çevir
        return local_time.strftime("%d %B %Y, %H:%M")