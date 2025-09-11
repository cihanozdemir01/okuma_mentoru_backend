from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ESKİ SATIR (Bunu silin): path('api/kitaplar/', include('reading.urls')),
    
    # YENİ SATIR (Bunu ekleyin): Artık 'api/' ile başlayan her şey reading.urls'e gidecek.
    path('api/', include('reading.urls')),
]