#configs/settings.py
"""
Bu modül, uygulama için gerekli ayarları ve API anahtarlarını içerir.
Ayarlar, çevresel değişkenlerden alınır ve uygulama genelinde kullanılabilir.
"""
import os
from dotenv import load_dotenv

# .env değişkenlerini yükler
load_dotenv()

# Elastich Search İletişim Ayarları
ELASTIC_HOST = os.getenv('ELASTIC_HOST')
ELASTIC_PORT = os.getenv('ELASTIC_PORT')
ELASTIC_PASSWORD =  os.getenv('ELASTIC_PASSWORD')