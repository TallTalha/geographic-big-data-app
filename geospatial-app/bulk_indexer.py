# geospatial-app/bulk_indexer.py
"""
Bu modül, coğrafi verileri, sunucudaki elastichsearch aracına gönderir.  
"""
from elasticsearch import Elasticsearch
from utils.logger import setup_logger
from configs.settings import ELASTIC_HOST, ELASTIC_PORT, ELASTIC_USER, ELASTIC_PASSWORD
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
JSON_FILE = os.path.join(PROJECT_ROOT, "data", "istanbul_siteler.json")

LOG = setup_logger("bulk_indexer")

def get_es_client() -> Elasticsearch | None:
    """
    Elasticsearch'e bağlanır ve  istemci nesnesini döndürür.
        Args:
            None
        Returns

    """
    try:
        LOG.info("Elastichsearch aracına bağlanılıyor...")

        # SSH Tüneli kullandığımız için localhost'a bağlanıyoruz
        # ve -k bayrağının yaptığı gibi SSL sertifika doğrulamasını atlıyoruz.
        client = Elasticsearch(
            hosts=[
                  {
                    "host": str(ELASTIC_HOST),
                    "port": str(ELASTIC_PORT),
                    "scheme":"https"
                   }
            ],
            basic_auth=( str(ELASTIC_USER), str(ELASTIC_PASSWORD) ),
            verify_certs=False,
            request_timeout=60
        )
        if client.ping():
            LOG.info("Elastichsearch bağlantısı başarılı.")
            return client
        else:
            LOG.error("Elastichsearch (ping) bağlantı başarısız.")
            return None
    except Exception as e:
        LOG.critical(f"Elastichsearch bağlantısı sırasında hata: {e}", exc_info=True)
        return None
    
def create_index_and_mapping(client: Elasticsearch, index_name:str, mapping: dict):
    """
    Belirtilen mapping ve index_name ile bir indeks oluşturur. Varsa, hata vermez.
        Args:
            client(Elastichsearch): Elastichsearch bağlantısı için gerekli istemci nesnesi.
            index_name(str): OLuşturulacak index adı.
            mapping(dict): Index altında saklanacak kayıtların yapısı.
        Returns:
            None
    """
    if not mapping or "mappings" not in mapping:
        error_message = "Geçersiz veya boş mapping şeması sağlandı. Şema, 'mappings' anahtarını içermelidir."
        LOG.error(error_message)
        raise ValueError(error_message)
    
    try:
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name, body=mapping)
            LOG.info(f"{index_name} indeksi başarıyla oluşturuldu ve mapping uygulandı.")
        else:
            LOG.warning(f"{index_name} indeksi zaten mevcut. Oluşturma adımı ATLANDI.")
    except Exception as e:
        LOG.error(f"{index_name} indeksi oluşturulurken hata: {e}", exc_info=True)

def generate_actions_from_json(json_file_path: str, index_name:str):
    """
    JSON dosyasını satır satır okur ve Elasticsearch bulk API'sinin
    anlayacağı formatta "action" objeleri üretir.
    Bu bir generator fonksiyonudur, tüm dosyayı hafızaya yüklemez. (Scalable)
        Args:
            json_file_path(str): İşlenecek olan JSON dosyasının yolu.
            index_name(str): Verilerin yazılacağı indeks 
        Returns:
            None
    """
    LOG.info(f"JSON dosyasından veriler okunuyor ve bulk actions hazırlanıyor...")
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for doc in data:
            yield {
                "_index": index_name,
                "_source": doc
            }

def main():
    """
    Ana iş akışını yönetir.
    """
    INDEX_NAME = "siteler" 

    es_client = get_es_client()
    if not es_client:
        sys.exit(1) # ÇIKIŞ -> 
    



