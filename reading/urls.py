# reading/urls.py

from django.urls import path
from .views import KitapListCreateAPIView, KitapDetailAPIView, NotListCreateAPIView

urlpatterns = [
    # /api/kitaplar/ -> Tüm kitapları listeler (GET) veya yeni kitap ekler (POST)
    path('', KitapListCreateAPIView.as_view(), name='api-kitap-list-create'),

    # /api/kitaplar/<id>/ -> Tek bir kitabı getirir (GET), günceller (PATCH), siler (DELETE)
    path('<int:pk>/', KitapDetailAPIView.as_view(), name='api-kitap-detail'),

    # Bu yapı, belirli bir kitaba ait notları hedefler.
    # <int:kitap_pk> -> Bu kısım, URL'deki sayıyı yakalar ve view'a 'kitap_pk'
    #                  adında bir değişken olarak gönderir.
    path('<int:kitap_pk>/notlar/', NotListCreateAPIView.as_view(), name='api-not-list-create'),
]