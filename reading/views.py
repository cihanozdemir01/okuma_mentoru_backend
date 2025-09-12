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
import requests
from django.conf import settings # API anahtarını güvenli bir şekilde almak için

def get_book_cover_url(title, author):
    """
    Kitap adı ve yazarına göre Google Books API'sinde arama yapıp
    kapak görseli URL'ini döndürür.
    """
    # API_KEY = getattr(settings, "GOOGLE_BOOKS_API_KEY", None)
    # if not API_KEY:
    #     return None # API anahtarı yoksa işlem yapma
        
    # Basit bir arama sorgusu oluşturuyoruz
    query = f"intitle:{title}+inauthor:{author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1" # &key={API_KEY}
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Hata durumunda exception fırlat
        data = response.json()
        
        if data.get("totalItems", 0) > 0:
            items = data.get("items", [])
            if items:
                volume_info = items[0].get("volumeInfo", {})
                image_links = volume_info.get("imageLinks", {})
                # 'thumbnail' veya 'smallThumbnail' linkini al
                cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")
                return cover_url
    except requests.exceptions.RequestException as e:
        print(f"Google Books API'ye erişirken hata: {e}")
        return None
    return None

# --- EKSİK OLAN VE GERİ GETİRİLEN SINIF ---
class KitapListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = KitapSerializer
    
    def get_queryset(self):
        return Kitap.objects.all()

    def perform_create(self, serializer):
        # Önce kitabı normal şekilde kaydet
        title = serializer.validated_data.get('title')
        author = serializer.validated_data.get('author')
        
        # Kapak görseli URL'ini al
        cover_url = get_book_cover_url(title, author)
        
        # Serializer'ı kapak URL'i ile birlikte kaydet
        serializer.save(cover_image_url=cover_url)
    
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
        # --- Veri Hazırlama ve Hesaplama ---
        
        instance = self.get_object() # Kitabın mevcut halini al
        
        # Okunan sayfa sayısını hesapla
        yeni_sayfa = request.data.get('current_page')
        okunan_sayfa = 0
        if yeni_sayfa is not None:
            try:
                okunan_sayfa = int(yeni_sayfa) - instance.current_page
            except (ValueError, TypeError):
                okunan_sayfa = 0

        # --- YENİ: Kapak Görseli Arama Mantığı ---
        
        # Gelen istekte 'title' veya 'author' güncelleniyor mu diye kontrol et
        new_title = request.data.get('title', instance.title)
        new_author = request.data.get('author', instance.author)
        
        # Eğer başlık veya yazar değiştiyse (veya ilk defa ekleniyorsa)
        # ve mevcut kapak URL'i boşsa, yeni bir kapak ara.
        if (new_title != instance.title or new_author != instance.author or not instance.cover_image_url):
            print(f"Yeni kapak aranıyor: {new_title} - {new_author}") # Hata ayıklama
            cover_url = get_book_cover_url(new_title, new_author)
            if cover_url:
                # Gelen isteğin verisine yeni URL'i ekle, böylece serializer bunu kaydeder.
                request.data['cover_image_url'] = cover_url

        # --- finished_at Mantığı ---
        
        new_status = request.data.get('status')
        if new_status == 'bitti' and instance.status != 'bitti':
            request.data['finished_at'] = timezone.now()
        elif new_status != 'bitti' and instance.status == 'bitti':
            request.data['finished_at'] = None

        # --- Ana Güncelleme İşlemi ---
        
        # Gelen isteği (üzerinde yaptığımız potansiyel değişikliklerle birlikte)
        # normal güncelleme sürecine sok.
        response = super().update(request, *args, **kwargs)
        
        # --- Güncelleme Sonrası İşlemler (Streak ve Heatmap) ---
        
        if response.status_code == 200:
            user = User.objects.first()
            if not user: return response

            # Sadece sayfa okunduysa aktiviteyi ve seriyi kaydet
            if okunan_sayfa > 0:
                # Heatmap (OkumaGunu) kaydı
                today = timezone.now().date()
                okuma_gunu, created = OkumaGunu.objects.get_or_create(
                    user=user, 
                    tarih=today,
                    defaults={'okunan_sayfa_sayisi': 0}
                )
                okuma_gunu.okunan_sayfa_sayisi += okunan_sayfa
                okuma_gunu.save()

                # Streak (Profile) kaydı
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

# YENİ VIEW: ISBN veya başlık/yazar ile kitap aramak için
class FindBookAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # URL'den arama parametrelerini al
        isbn = request.query_params.get('isbn')
        title = request.query_params.get('title')
        author = request.query_params.get('author')
        
        if not isbn and not (title and author):
            return Response(
                {"error": "ISBN veya başlık/yazar parametreleri gereklidir."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Google Books API'sinde arama yap
        if isbn:
            query = f"isbn:{isbn}"
        else:
            query = f"intitle:{title}+inauthor:{author}"
            
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("totalItems", 0) > 0:
                item = data.get("items", [])[0]
                volume_info = item.get("volumeInfo", {})
                
                # Flutter'a göndereceğimiz temiz veriyi oluştur
                book_data = {
                    "title": volume_info.get("title", ""),
                    "author": ", ".join(volume_info.get("authors", [""])),
                    "total_pages": volume_info.get("pageCount", 0),
                    "cover_image_url": (volume_info.get("imageLinks", {}).get("thumbnail") or 
                                        volume_info.get("imageLinks", {}).get("smallThumbnail"))
                }
                return Response(book_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Bu bilgilere sahip bir kitap bulunamadı."},
                    status=status.HTTP_404_NOT_FOUND
                )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"API'ye erişirken hata: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )