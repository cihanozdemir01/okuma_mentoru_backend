from rest_framework import serializers
from .models import Kitap, Not, Kategori
from django.utils import timezone

# 1. KATEGORİ SERIALIZER'I (Değişiklik yok)
# Bu, Kategori modelindeki verileri (id ve ad) JSON formatına çevirir.
class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategori
        fields = ['id', 'ad']

# 2. KİTAP SERIALIZER'I (GÜNCELLENEN KISIM)
class KitapSerializer(serializers.ModelSerializer):
    # OKUMA İÇİN: Bu alan, GET isteklerinde tam kategori nesnesini
    # ({'id': 1, 'ad': 'Roman'}) döndürür.
    # 'source' parametresi, bunun modeldeki 'kategoriler' alanını kullandığını belirtir.
    kategoriler_detay = KategoriSerializer(source='kategoriler', many=True, read_only=True)

    # YAZMA İÇİN: Bu alan, POST/PATCH isteklerinde sadece kategori ID'lerinin
    # bir listesini ([1, 3] gibi) kabul eder. 'write_only=True' olduğu için
    # GET yanıtlarında bu basit liste görünmez.
    kategoriler = serializers.PrimaryKeyRelatedField(
        queryset=Kategori.objects.all(),
        many=True,
        write_only=True,
        required=False # Kategori seçimi zorunlu olmasın
    )

    class Meta:
        model = Kitap
        # 'fields' listesine hem okuma hem de yazma alanlarımızı ekliyoruz.
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
            'cover_image_url',
            'kategoriler_detay', # Okuma için
            'kategoriler'      # Yazma için
        ]
        read_only_fields = ['user']

# 3. DİĞER SERIALIZER'LAR (Değişiklik yok)

class KitapIlişkiliSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kitap
        fields = ['id', 'title']

class NotSerializer(serializers.ModelSerializer):
    olusturma_tarihi_formatli = serializers.SerializerMethodField()
    kitap = KitapIlişkiliSerializer(read_only=True)

    class Meta:
        model = Not
        fields = ['id', 'kitap', 'icerik', 'olusturma_tarihi_formatli']

    def get_olusturma_tarihi_formatli(self, obj):
        utc_time = obj.olusturma_tarihi
        local_time = utc_time + timezone.timedelta(hours=3)
        return local_time.strftime("%d %B %Y, %H:%M")