import google.generativeai as genai
from django.conf import settings

# Django ve Python kütüphaneleri
from datetime import date, timedelta
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone

# Django REST Framework kütüphaneleri
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# Kendi uygulama dosyalarımız
from .models import Kitap, Not, Profile, OkumaGunu, Kategori
from .serializers import KitapSerializer, NotSerializer, KategoriSerializer
from .filters import KitapFilter

if getattr(settings, 'GOOGLE_API_KEY', None):
    genai.configure(api_key=settings.GOOGLE_API_KEY)


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

class KategoriListAPIView(generics.ListAPIView):
    queryset = Kategori.objects.all()
    serializer_class = KategoriSerializer

# --- EKSİK OLAN VE GERİ GETİRİLEN SINIF ---
class KitapListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = KitapSerializer
    # GÜNCELLEME: queryset'i doğrudan sınıf seviyesinde tanımlamak daha standarttır.
    queryset = Kitap.objects.all().order_by('-created_at') # En yeni eklenenler üstte olsun
    
    # YENİ: View'a, URL parametrelerini işlemek için bu filtre sınıfını kullanmasını söylüyoruz.
    filterset_class = KitapFilter
    
    def perform_create(self, serializer):
        title = serializer.validated_data.get('title')
        author = serializer.validated_data.get('author')
        cover_url = get_book_cover_url(title, author)
        serializer.save(cover_image_url=cover_url)
    
    # GÜNCELLEME: 'list' metodunu, gelen istekleri filtreleyecek şekilde güncelliyoruz.
    def list(self, request, *args, **kwargs):
        # 1. Önce, gelen isteğe göre filtrelenmiş queryset'i al.
        #    `self.filter_queryset` metodu, `filterset_class`'ı kullanarak
        #    ?status=bitti gibi parametreleri otomatik olarak uygular.
        queryset = self.filter_queryset(self.get_queryset())
        
        # 2. Filtrelenmiş kitap listesi verisini serializer ile hazırla.
        serializer = self.get_serializer(queryset, many=True)
        kitaplar_data = serializer.data
        
        # 3. İstatistikleri HESAPLAMA (Filtrelenmemiş toplam istatistikler)
        #    Kullanıcıya genel istatistikleri göstermeye devam etmek daha mantıklı olabilir.
        #    Bu yüzden burada `self.get_queryset()`'in tamamını kullanıyoruz.
        tum_kitaplar = Kitap.objects.all()
        bitirilen_kitap_sayisi = tum_kitaplar.filter(status='bitti').count()
        toplam_okunan_sayfa = sum(k.current_page for k in tum_kitaplar if k.current_page is not None)
        
        # 4. Streak bilgisini al (bu da genel bir istatistiktir).
        user = User.objects.first()
        streak = 0
        if user:
            profile, created = Profile.objects.get_or_create(user=user)
            today = date.today()
            if profile.son_okuma_tarihi and (today - profile.son_okuma_tarihi > timedelta(days=1)):
                profile.streak = 0
                profile.save()
            streak = profile.streak

        # 5. Tüm verileri tek bir JSON nesnesinde birleştir.
        #    'kitaplar' listesi filtrelenmiş, 'istatistikler' ise genel olacak.
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
        print(f"Google Books API'ye gidilecek URL: {url}")
        
        try:
            response = requests.get(url, timeout=10) # 10 saniye zaman aşımı ekleyelim
            print(f"Google Books API'den Gelen Durum Kodu: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            
             if data.get("totalItems", 0) > 0:
                print("Kitap bulundu, veriler işleniyor.")
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
                print("Google Books API kitap bulamadı.")
                return Response(
                    {"error": "Bu bilgilere sahip bir kitap bulunamadı."},
                    status=status.HTTP_404_NOT_FOUND
                )
        except requests.exceptions.RequestException as e:
            print(f"!!! Google Books API'ye erişirken KRİTİK HATA: {e} !!!")
            return Response(
                {"error": f"API'ye erişirken hata: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class KategoriListAPIView(generics.ListAPIView):
    queryset = Kategori.objects.all()
    serializer_class = KategoriSerializer

# YENİ VIEW: Tüm benzersiz yazarları listeler
class AuthorListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Veritabanındaki tüm kitaplardan, 'author' alanındaki
        # benzersiz (distinct) değerleri al ve alfabetik sırala.
        authors = Kitap.objects.values_list('author', flat=True).distinct().order_by('author')
        return Response(authors)

class SummaryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user = User.objects.first()
        if not user: return Response([])

        # URL'den parametreleri al
        metric = request.query_params.get('metric', 'page_count')
        group_by = request.query_params.get('group_by', 'month')

        # Hangi modele ve alana bakacağımızı seç
        if metric == 'book_count':
            model = Kitap
            date_field = 'finished_at'
            aggregation_function = Count('id')
        else: # Varsayılan 'page_count'
            model = OkumaGunu
            date_field = 'tarih'
            aggregation_function = Sum('okunan_sayfa_sayisi')

        # Gruplama periyodunu ve başlangıç tarihini seç
        if group_by == 'week':
            trunc_function = TruncWeek(date_field)
            start_date = timezone.now().date() - timedelta(weeks=12)
        elif group_by == 'day':
            trunc_function = TruncDay(date_field)
            start_date = timezone.now().date() - timedelta(days=12)
        else: # Varsayılan 'month'
            trunc_function = TruncMonth(date_field)
            start_date = (timezone.now().date() - timedelta(days=365)).replace(day=1)

        # Sorguyu bu dinamik parametrelerle oluştur
        queryset = model.objects.filter(
            # user=user, # Kullanıcı sistemi eklenince bu satır aktif edilecek
            **{f'{date_field}__isnull': False}, # Tarih alanı boş olmayanları al
            **{f'{date_field}__gte': start_date}
        ).annotate(
            period=trunc_function
        ).values('period').annotate(
            value=aggregation_function
        ).order_by('period')

        # Veriyi formatla
        summary_data = [
            {"period": result['period'].strftime('%Y-%m-%d'), "value": result['value']} 
            for result in queryset
        ]
        
        return Response(summary_data)

class CharacterChatAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # --- HATA AYIKLAMA: API Anahtarının yüklenip yüklenmediğini kontrol et ---
        api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        if not api_key:
            print("HATA: GOOGLE_API_KEY settings.py'de bulunamadı veya boş.")
            return Response({"error": "Sunucu yapılandırma hatası: API anahtarı eksik."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # --- Mevcut kodun devamı ---
        kitap_adi = request.data.get('kitap_adi')
        karakter_adi = request.data.get('karakter_adi')
        kullanici_sorusu = request.data.get('kullanici_sorusu')

        if not all([kitap_adi, karakter_adi, kullanici_sorusu]):
            return Response({"error": "Eksik parametreler."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print("Gemini API'sine istek gönderiliyor...") # Log 1
            genai.configure(api_key=api_key) # Anahtarı her seferinde yeniden configure etmek daha güvenli olabilir
            
            prompt = f"""
            Sen, {kitap_adi} romanındaki {karakter_adi} karakterisin. 
            Tüm cevaplarını, o karakterin kişiliğine, bilgi düzeyine ve konuşma tarzına tamamen bürünerek ver. 
            Asla bir yapay zeka olduğunu veya bir metin modeli olduğunu söyleme. 
            Sadece ve sadece {karakter_adi} olarak cevap ver. 
            Modern dünyadan veya romanda geçmeyen olaylardan bahsetme.
            Şimdi sana sorulan şu soruyu cevapla: "{kullanici_sorusu}"
            """
            
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            
            print("Gemini API'sinden cevap başarıyla alındı.") # Log 2
            return Response({"cevap": response.text}, status=status.HTTP_200_OK)

        except Exception as e:
            # GÜNCELLENMİŞ HATA MESAJI: Artık hatanın kendisini de yazdırıyoruz.
            print(f"!!! Gemini API HATASI: {e} !!!") 
            return Response({"error": "Yapay zeka ile iletişim kurulamadı."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)