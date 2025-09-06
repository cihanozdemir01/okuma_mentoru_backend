# reading/forms.py
from django import forms
from .models import Book, Note

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # Kullanıcının formda görmesini istediğimiz alanları belirtiyoruz.
        # 'user' alanını buraya eklemiyoruz, çünkü onu arkaplanda biz atayacağız.
        fields = ['title', 'author' , 'total_pages', 'target_date']

        # Form alanlarının etiketlerini Türkçeleştirelim.
        labels = {
            'title': 'Kitabın Adı',
            'author': 'Yazar Adı',
            'total_pages': 'Toplam Sayfa Sayısı',
            'target_date': 'Hedeflenen Bitiş Tarihi',
        }
        
        # Tarih alanı için bir "widget" ekleyerek tarayıcının tarih seçici
        # göstermesini sağlayalım.
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['text']
        labels = {
            'text': 'Notunuz veya Alıntınız'
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Kitapla ilgili düşüncelerinizi veya sevdiğiniz bir alıntıyı buraya yazın...'}),
        }