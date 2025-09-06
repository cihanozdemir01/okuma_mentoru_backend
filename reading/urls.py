# reading/urls.py

from django.urls import path
from .views import KitapListCreateAPIView, KitapDetailAPIView

urlpatterns = [
    # /api/kitaplar/ -> Tüm kitapları listeler (GET) veya yeni kitap ekler (POST)
    path('', KitapListCreateAPIView.as_view(), name='api-kitap-list-create'),

    # /api/kitaplar/<id>/ -> Tek bir kitabı getirir (GET), günceller (PATCH), siler (DELETE)
    path('<int:pk>/', KitapDetailAPIView.as_view(), name='api-kitap-detail'),
]