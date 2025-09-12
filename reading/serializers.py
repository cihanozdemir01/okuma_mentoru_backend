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
            'created_at',
            'finished_at',
            'cover_image_url'  # YENİ ALAN EKLENDİ
        ]
        read_only_fields = ['user']

# NotSerializer içinde kullanmak için daha verimli bir serializer
class KitapIlişkiliSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kitap
        fields = ['id', 'title']

class NotSerializer(serializers.ModelSerializer):
    olusturma_tarihi_formatli = serializers.SerializerMethodField()
    # 'kitap' alanını yukarıdaki küçük serializer ile değiştiriyoruz
    kitap = KitapIlişkiliSerializer(read_only=True)

    class Meta:
        model = Not
        # 'fields' listesini güncelliyoruz
        fields = ['id', 'kitap', 'icerik', 'olusturma_tarihi_formatli']

    def get_olusturma_tarihi_formatli(self, obj):
        utc_time = obj.olusturma_tarihi
        local_time = utc_time + timezone.timedelta(hours=3)
        return local_time.strftime("%d %B %Y, %H:%M")