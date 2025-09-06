# reading/serializers.py

from rest_framework import serializers
from .models import Kitap

class KitapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kitap
        fields = [
            'id', 
            'user', 
            'title', 
            'author', 
            'total_pages', 
            'current_page', 
            'status',
            'created_at'
        ]
        # user alanını API'den gelen veriyle değiştiremezsin,
        # sadece okunabilir.
        read_only_fields = ['user']