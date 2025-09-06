# reading/views.py

from rest_framework import generics
from .models import Kitap, Not, Profile # Profile'ı import et
from .serializers import KitapSerializer, NotSerializer
from django.contrib.auth.models import User # User modelini import et
from datetime import date, timedelta # date ve timedelta'yı import et
from rest_framework.response import Response

class KitapListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = KitapSerializer
    
    def get_queryset(self):
        # Şimdilik kullanıcıya göre filtreleme yapmadan TÜM kitapları döndür.
        return Kitap.objects.all()

    def perform_create(self, serializer):
        # Şimdilik kullanıcı olmadan kaydet
        serializer.save()
    
    def list(self, request, *args, **kwargs):
        # 1. Standart kitap listesi verisini al.
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        kitaplar_data = serializer.data
        
        # 2. İstatistikleri hesapla.
        bitirilen_kitap_sayisi = queryset.filter(status='bitti').count()
        # Toplam okunan sayfayı hesaplarken None durumunu kontrol et
        toplam_okunan_sayfa = sum(k.current_page for k in queryset if k.current_page is not None)
        
        # 3. Streak bilgisini al.
        user = User.objects.first()
        streak = 0
        if user:
            # Kullanıcının profilini al, yoksa oluştur.
            profile, created = Profile.objects.get_or_create(user=user)
            # Serinin güncel olup olmadığını kontrol et
            today = date.today()
            if profile.son_okuma_tarihi and (today - profile.son_okuma_tarihi > timedelta(days=1)):
                # Seri kırılmışsa, sıfırla.
                profile.streak = 0
                profile.save()
            streak = profile.streak

        # 4. Tüm verileri tek bir JSON nesnesinde birleştir.
        data = {
            'kitaplar': kitaplar_data,
            'istatistikler': {
                'bitirilen_kitap_sayisi': bitirilen_kitap_sayisi,
                'toplam_okunan_sayfa': toplam_okunan_sayfa,
                'gunluk_seri': streak
            }
        }
        
        # Özel formatımızdaki bu veriyi Response olarak döndür.
        return Response(data)

class KitapDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = KitapSerializer

    def get_queryset(self):
        # Şimdilik kullanıcıya bakmadan tüm kitapları getir.
        return Kitap.objects.all()
    
    def update(self, request, *args, **kwargs):
        # Önce varsayılan güncelleme işlemini yap (sayfa sayısı güncellensin)
        response = super().update(request, *args, **kwargs)
        
        # Güncelleme başarılı olduysa (200 OK), streak mantığını çalıştır
        if response.status_code == 200:
            # Şimdilik, sistemdeki ilk kullanıcıyı (admin) hedef alıyoruz.
            # Gerçek kullanıcı sistemi olduğunda burası 'request.user' olacak.
            user = User.objects.first()
            if not user: return response # Kullanıcı yoksa devam etme

            # Kullanıcının profilini al veya yoksa oluştur.
            profile, created = Profile.objects.get_or_create(user=user)
            
            today = date.today()
            
            # Eğer kullanıcı daha önce hiç okuma yapmadıysa veya
            # en son dünden daha önce okuma yaptıysa, seriyi 1'e ayarla.
            if profile.son_okuma_tarihi is None or (today - profile.son_okuma_tarihi > timedelta(days=1)):
                profile.streak = 1
            # Eğer kullanıcı en son dün okuma yaptıysa, seriyi bir artır.
            elif (today - profile.son_okuma_tarihi == timedelta(days=1)):
                profile.streak += 1
            # (Eğer bugün zaten okuma yaptıysa, seriyi değiştirmeye gerek yok)

            # Son okuma tarihini bugüne güncelle.
            profile.son_okuma_tarihi = today
            profile.save()

        return response

class NotListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NotSerializer

    def get_queryset(self):
        """
        Bu metot, sadece URL'de belirtilen kitaba ait notları
        getirecek şekilde queryset'i filtreler.
        Örn: /api/kitaplar/5/notlar/ adresine gelen istek için
        sadece 5 ID'li kitaba ait notları döndürür.
        """
        kitap_id = self.kwargs['kitap_pk']
        return Not.objects.filter(kitap_id=kitap_id)

    def perform_create(self, serializer):
        """
        Yeni bir not oluşturulurken, 'kitap' alanını dışarıdan gelen
        veriyle değil, doğrudan URL'den alınan kitap ID'si ile doldurur.
        Bu, bir nota yanlışlıkla başka bir kitap atamayı önler.
        """
        kitap_id = self.kwargs['kitap_pk']
        kitap = Kitap.objects.get(pk=kitap_id)
        serializer.save(kitap=kitap)