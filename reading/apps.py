# reading/apps.py

from django.apps import AppConfig

class ReadingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reading'

    # Bu metot, Django'nun sinyalleri (signals) yüklemesini sağlıyordu.
    # Profile modelini kullanmadığımız için şimdilik bu metoda ihtiyacımız yok.
    # def ready(self):
    #     import reading.signals