from django.urls import path
from .views import (
    KitapListCreateAPIView, 
    KitapDetailAPIView, 
    NotListCreateAPIView,
    NoteListAPIView,
    KategoriListAPIView,
    AuthorListAPIView,
    HeatmapAPIView,
    SummaryAPIView,
    CharacterChatAPIView
)

urlpatterns = [
    # Kitap & Not URL'leri
    path('kitaplar/', KitapListCreateAPIView.as_view(), name='kitap-list-create'),
    path('kitaplar/<int:pk>/', KitapDetailAPIView.as_view(), name='kitap-detail'),
    path('kitaplar/<int:kitap_pk>/notlar/', NotListCreateAPIView.as_view(), name='not-list-create'),
    path('notes/', NoteListAPIView.as_view(), name='note-list-all'),

    # Filtreleme için yardımcı URL'ler
    path('kategoriler/', KategoriListAPIView.as_view(), name='kategori-list'),
    path('authors/', AuthorListAPIView.as_view(), name='author-list'),

    # İstatistik URL'leri
    path('stats/heatmap/', HeatmapAPIView.as_view(), name='heatmap-data'),
    path('stats/summary/', SummaryAPIView.as_view(), name='summary-api'),

    path('character-chat/', CharacterChatAPIView.as_view(), name='character-chat'),
]