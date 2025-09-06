# reading/views.py

from rest_framework import generics
# `permissions`'ı şimdilik import etmeye gerek yok, çünkü kullanmıyoruz.
# from rest_framework import permissions 
from .models import Kitap, Not
from .serializers import KitapSerializer, NotSerializer

class KitapListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = KitapSerializer
    
    def get_queryset(self):
        # Şimdilik kullanıcıya göre filtreleme yapmadan TÜM kitapları döndür.
        return Kitap.objects.all()

    def perform_create(self, serializer):
        # Şimdilik kullanıcı olmadan kaydet
        serializer.save()

class KitapDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = KitapSerializer

    def get_queryset(self):
        # Şimdilik kullanıcıya bakmadan tüm kitapları getir.
        return Kitap.objects.all()

class NotListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NotSerializer

    def get_queryset(self):
        """
        Bu metot, sadece URL'de belirtilen kitaba ait notları
        getirecek şekilde queryset'i filtreler.
        Örn: /api/kitaplar/5/notlar/ adresine gelen istek için
        sadece 5 ID'li kitaba ait notları döndürür.
        """
        kitap_id = self.kwargs['kitap_pk']
        return Not.objects.filter(kitap_id=kitap_id)

    def perform_create(self, serializer):
        """
        Yeni bir not oluşturulurken, 'kitap' alanını dışarıdan gelen
        veriyle değil, doğrudan URL'den alınan kitap ID'si ile doldurur.
        Bu, bir nota yanlışlıkla başka bir kitap atamayı önler.
        """
        kitap_id = self.kwargs['kitap_pk']
        kitap = Kitap.objects.get(pk=kitap_id)
        serializer.save(kitap=kitap)