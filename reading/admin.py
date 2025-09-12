# reading/admin.py

from django.contrib import admin
from .models import Kitap, Not, Profile, OkumaGunu, Kategori  # Modelimizin adı 'Kitap' olduğu için onu import ediyoruz.

# Kitap admin panelini özelleştirmek için bu sınıfı tanımlıyoruz
class KitapAdmin(admin.ModelAdmin):
    # Admin listesinde hangi sütunların görüneceğini belirtir
    list_display = ('title', 'author', 'status', 'is_featured')
    
    # Listeden ayrılmadan doğrudan düzenlenebilecek alanlar
    list_editable = ('is_featured',)
    
    # Sağ tarafta filtreleme seçenekleri oluşturur
    list_filter = ('status', 'is_featured', 'kategoriler')
    
    # Üstte bir arama çubuğu ekler
    search_fields = ('title', 'author')
    
    # ManyToMany alanlarını (kategoriler gibi) çok daha kullanışlı bir
    # çift-listeli arayüz ile gösterir
    filter_horizontal = ('kategoriler',)

    # Eğer daha önce basit bir kayıt varsa (admin.site.register(Kitap)),
# onu kaldırıp, yerine özelleştirilmiş olanı kaydetmemiz gerekir.
# Bir hata oluşursa (NotRegistered), görmezden gel.
try:
    admin.site.unregister(Kitap)
except admin.sites.NotRegistered:
    pass

admin.site.register(Kitap, KitapAdmin)
admin.site.register(Kategori) # Yeni modeli kaydet
admin.site.register(Not)
admin.site.register(Profile)
admin.site.register(OkumaGunu)

