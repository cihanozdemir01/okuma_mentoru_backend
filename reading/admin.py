# reading/admin.py

from django.contrib import admin
from .models import Kitap, Not # Modelimizin adı 'Kitap' olduğu için onu import ediyoruz.

# Kitap modelini admin paneline kaydet
admin.site.register(Kitap)
admin.site.register(Not)