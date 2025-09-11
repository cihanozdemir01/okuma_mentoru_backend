from rest_framework import generics
from .models import Kitap, Not, Profile, OkumaGunu
from .serializers import KitapSerializer, NotSerializer
from django.contrib.auth.models import User
from datetime import date, timedelta
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from django.db.models import Count
from django.db.models.functions import TruncMonth

# --- EKSİK OLAN VE GERİ GETİRİLEN SINIF ---
class KitapListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = KitapSerializer
    
    def get_queryset(self):
        return Kitap.objects.all()

    def perform_create(self, serializer):
        serializer.save()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        kitaplar_data = serializer.data
        
        bitirilen_kitap_sayisi = queryset.filter(status='bitti').count()
        toplam_okunan_sayfa = sum(k.current_page for k in queryset if k.current_page is not None)
        
        user = User.objects.first()
        streak = 0
        if user:
            profile, created = Profile.objects.get_or_create(user=user)
            today = date.today()
            if profile.son_okuma_tarihi and (today - profile.son_okuma_tarihi > timedelta(days=1)):
                profile.streak = 0
                profile.save()
            streak = profile.streak

        data = {
            'kitaplar': kitaplar_data,
            'istatistikler': {
                'bitirilen_kitap_sayisi': bitirilen_kitap_sayisi,
                'toplam_okunan_sayfa': toplam_okunan_sayfa,
                'gunluk_seri': streak
            }
        }
        
        return Response(data)

# --- MEVCUT DİĞER SINIFLAR ---
class KitapDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = KitapSerializer
    def get_queryset(self):
        return Kitap.objects.all()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        yeni_sayfa = request.data.get('current_page')
        okunan_sayfa = 0
        if yeni_sayfa is not None:
            try:
                okunan_sayfa = int(yeni_sayfa) - instance.current_page
            except (ValueError, TypeError):
                okunan_sayfa = 0

        new_status = request.data.get('status')
        if new_status == 'bitti' and instance.status != 'bitti':
            request.data['finished_at'] = timezone.now()
        elif new_status != 'bitti' and instance.status == 'bitti':
            request.data['finished_at'] = None

        response = super().update(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.first()
            if not user: return response

            if okunan_sayfa > 0:
                today = timezone.now().date()
                okuma_gunu, created = OkumaGunu.objects.get_or_create(
                    user=user, 
                    tarih=today,
                    defaults={'okunan_sayfa_sayisi': 0}
                )
                okuma_gunu.okunan_sayfa_sayisi += okunan_sayfa
                okuma_gunu.save()

                profile, created = Profile.objects.get_or_create(user=user)
                today_date = date.today()
                
                if profile.son_okuma_tarihi is None or (today_date - profile.son_okuma_tarihi > timedelta(days=1)):
                    profile.streak = 1
                elif (today_date - profile.son_okuma_tarihi == timedelta(days=1)):
                    profile.streak += 1
                
                profile.son_okuma_tarihi = today_date
                profile.save()
        return response

class NotListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NotSerializer
    def get_queryset(self):
        kitap_id = self.kwargs['kitap_pk']
        return Not.objects.filter(kitap_id=kitap_id)
    def perform_create(self, serializer):
        kitap_id = self.kwargs['kitap_pk']
        kitap = Kitap.objects.get(pk=kitap_id)
        serializer.save(kitap=kitap)

class NoteListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        notes = Not.objects.all().order_by('-olusturma_tarihi')
        serializer = NotSerializer(notes, many=True)
        return Response(serializer.data)

class MonthlySummaryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        current_year = timezone.now().year
        queryset = Kitap.objects.filter(
            status='bitti',
            finished_at__year=current_year
        ).annotate(
            month=TruncMonth('finished_at')
        ).values(
            'month'
        ).annotate(
            count=Count('id')
        ).order_by('month')
        
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        summary_data = [{"month": ay, "count": 0} for ay in aylar]
        
        for result in queryset:
            month_index = result['month'].month - 1
            if 0 <= month_index < 12:
                summary_data[month_index]['count'] = result['count']
        return Response(summary_data)

class HeatmapAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user = User.objects.first()
        if not user:
            return Response({})
        bir_yil_once = timezone.now().date() - timedelta(days=365)
        okuma_gunleri = OkumaGunu.objects.filter(user=user, tarih__gte=bir_yil_once)
        heatmap_data = {
            gun.tarih.strftime('%Y-%m-%d'): gun.okunan_sayfa_sayisi 
            for gun in okuma_gunleri
        }
        return Response(heatmap_data)