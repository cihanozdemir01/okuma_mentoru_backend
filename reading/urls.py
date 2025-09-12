from django.urls import path
from .views import (
    KitapListCreateAPIView, 
    KitapDetailAPIView, 
    NotListCreateAPIView,
    NoteListAPIView,
    MonthlySummaryAPIView,
    HeatmapAPIView,
    FindBookAPIView
)

urlpatterns = [
    # Sonuç URL: /api/kitaplar/
    path('kitaplar/', KitapListCreateAPIView.as_view(), name='kitap-list-create'),
    
    # Sonuç URL: /api/kitaplar/<id>/
    path('kitaplar/<int:pk>/', KitapDetailAPIView.as_view(), name='kitap-detail'),
    
    # Sonuç URL: /api/kitaplar/<id>/notlar/
    path('kitaplar/<int:kitap_pk>/notlar/', NotListCreateAPIView.as_view(), name='not-list-create'),
    
    # Sonuç URL: /api/notes/
    path('notes/', NoteListAPIView.as_view(), name='note-list-all'),
    
    path('stats/monthly-summary/', MonthlySummaryAPIView.as_view(), name='monthly-summary'),

    path('stats/heatmap/', HeatmapAPIView.as_view(), name='heatmap-data'),

    path('find-book/', FindBookAPIView.as_view(), name='find-book'),
]