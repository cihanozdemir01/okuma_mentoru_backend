# config/urls.py
from django.contrib import admin
from django.urls import path, include # include'u buraya ekle

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', include('reading.urls')), # Bu satırı ekle
    path('api/kitaplar/', include('reading.urls')),

]