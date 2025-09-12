# Django-filter kütüphanesini import ediyoruz.
from django_filters import rest_framework as filters

# Filtreleme yapacağımız Kitap modelini import ediyoruz.
from .models import Kitap

class KitapFilter(filters.FilterSet):
    """
    Kitap modeli için özel filtrelerimizi tanımladığımız sınıf.
    Bu sınıf, gelen URL parametrelerini (`?yazar=...` gibi) alıp
    veritabanı sorgularına dönüştürür.
    """

    # 'yazar' adında bir filtre tanımlıyoruz.
    # Bu, ?yazar=Yaşar Kemal gibi bir isteği karşılayacak.
    # CharFilter: Metin tabanlı bir filtre olduğunu belirtir.
    # field_name='author': Bu filtrenin Kitap modelindeki 'author' alanını hedeflediğini söyler.
    # lookup_expr='icontains': Arama mantığını belirler. 'icontains', "büyük/küçük harf
    # duyarsız bir şekilde, verilen metni İÇERENLERİ bul" demektir.
    yazar = filters.CharFilter(field_name='author', lookup_expr='icontains')
    
    # 'kategori' adında bir filtre tanımlıyoruz.
    # Bu, ?kategori=1 gibi bir isteği karşılayacak.
    # NumberFilter: Sayı tabanlı bir filtre olduğunu belirtir.
    # field_name='kategoriler__id': Bu, ManyToMany ilişkisi üzerinden arama yapmamızı sağlar.
    # "Kitap'ın 'kategoriler' ilişkisindeki nesnelerin 'id' alanına bak" demektir.
    kategori = filters.NumberFilter(field_name='kategoriler__id')

    class Meta:
        # Bu filtre setinin hangi model üzerinde çalışacağını belirtiyoruz.
        model = Kitap
        
        # 'fields' listesine eklediğimiz alanlar için django-filter
        # otomatik olarak "tam eşleşme" filtresi oluşturur.
        # Örneğin, 'status' için ?status=bitti gibi bir istek,
        # status alanı tam olarak 'bitti' olan kitapları getirecektir.
        fields = ['status', 'yazar', 'kategori']