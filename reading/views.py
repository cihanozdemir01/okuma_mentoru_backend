# reading/views.py

from rest_framework import generics
# `permissions`'ı şimdilik import etmeye gerek yok, çünkü kullanmıyoruz.
# from rest_framework import permissions 
from .models import Kitap
from .serializers import KitapSerializer

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