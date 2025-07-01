import time
import requests
import psutil

BASE_URL = "http://localhost:41184"
TOKEN = "08a64ca62261a0db5150e84650c1f6dfe81d8b25b88983f2e828d696bf1c4b59079fdc93109c97c56a6111e2787782750f826c0a22f18792c84774457e90b5a3"

test_results = []

# Performans Testleri
def log_result(test_id, description, success):
    test_results.append({
        "test_id": test_id,
        "description": description,
        "success": success
    })
    print(f"Test {test_id}: {description} - {'Basarili' if success else 'Basarisiz'}")
    
# TC014: Uygulama Baslangic Suresi
def test_application_start_time():
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/ping") 
        end_time = time.time()
        duration = end_time - start_time
        if response.status_code == 200 and duration <= 3:
            log_result("TC014", "Uygulama baslangic suresi", True)
        else:
            log_result("TC014", "Uygulama baslangic suresi", False)
    except Exception as e:
        log_result("TC014", f"Uygulama baslangic suresi hatasi: {str(e)}", False)

# TC015: Not Kaydetme Suresi
def test_note_save_time():
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/notes?token={TOKEN}", json={
            "title": "Performance Test Note",
            "body": "Bu bir performans testidir."
        })
        end_time = time.time()
        duration = end_time - start_time
        if response.status_code == 200 and duration <= 3:
            log_result("TC015", "Not kaydetme suresi", True)
        else:
            log_result("TC015", "Not kaydetme suresi", False)
    except Exception as e:
        log_result("TC015", f"Not kaydetme suresi hatasi: {str(e)}", False)

# TC016: Arama Sonuc Hizi
def test_search_response_time():
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/search?query=Performance&token={TOKEN}")
        end_time = time.time()
        duration = end_time - start_time
        if response.status_code == 200 and duration <= 3:
            log_result("TC016", "Arama sonuc hizi", True)
        else:
            log_result("TC016", "Arama sonuc hizi", False)
    except Exception as e:
        log_result("TC016", f"Arama sonuc hizi hatasi: {str(e)}", False)

# TC017: Buyuk Notlari Yukleme
def test_large_note_loading():
    try:
        note_body = "Lorem Ipsum " * 10000 
        response = requests.post(f"{BASE_URL}/notes?token={TOKEN}", json={
            "title": "Large Note",
            "body": note_body
        })
        if response.status_code == 200:
            note_id = response.json()["id"]
            start_time = time.time()
            load_response = requests.get(f"{BASE_URL}/notes/{note_id}?token={TOKEN}")
            end_time = time.time()
            duration = end_time - start_time
            if load_response.status_code == 200 and duration <= 3:
                log_result("TC017", "Buyuk notlari yukleme", True)
            else:
                log_result("TC017", "Buyuk notlari yukleme", False)
        else:
            log_result("TC017", "Buyuk not olusturma basarisiz", False)
    except Exception as e:
        log_result("TC017", f"Buyuk notlari yukleme hatasi: {str(e)}", False)

# TC018: Coklu Not Yukleme
def test_multiple_note_loading():
    try:
        for i in range(50):
            requests.post(f"{BASE_URL}/notes?token={TOKEN}", json={
                "title": f"Test Note {i}",
                "body": f"Bu Test Note {i} icin."
            })
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/notes?token={TOKEN}")
        end_time = time.time()
        duration = end_time - start_time
        if response.status_code == 200 and duration <= 3:
            log_result("TC018", "Coklu not yukleme", True)
        else:
            log_result("TC018", "Coklu not yukleme", False)
    except Exception as e:
        log_result("TC018", f"Coklu not yukleme hatasi: {str(e)}", False)
        
# TC019: Senkronizasyon Suresi
def test_sync_time():
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/sync?token={TOKEN}")
        end_time = time.time()
        duration = end_time - start_time
        if response.status_code == 200 and duration <= 5:
            log_result("TC019", "Senkronizasyon suresi", True)
        else:
            log_result("TC019", "Senkronizasyon suresi", False)
    except Exception as e:
        log_result("TC019", f"Senkronizasyon suresi hatasi: {str(e)}", False)

# TC020: Mobil Performans Testi
def test_mobile_performance():
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/notes?token={TOKEN}", json={
            "title": "Mobile Test Note",
            "body": "Bu bir mobil performans testidir."
        })
        end_time = time.time()
        duration = end_time - start_time
        if response.status_code == 200 and duration <= 1:
            log_result("TC020", "Mobil performans", True)
        else:
            log_result("TC020", "Mobil performans", False)
    except Exception as e:
        log_result("TC020", f"Mobil performans hatasi: {str(e)}", False)

def create_note():
    try:
        response = requests.post(f"{BASE_URL}/notes?token={TOKEN}", json={
            "title": "Test Note",
            "body": "Bu bir test notudur."
        })
        if response.status_code == 200:
            note_id = response.json()["id"]
            return note_id
        else:
            pass
    except Exception as e:
        pass

def get_application_usage(process_name):
    try:
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                cpu_usage = proc.info['cpu_percent'] 
                memory_usage = proc.info['memory_info'].rss / (1024 * 1024) 
                return cpu_usage, memory_usage
        return None, None 
    except Exception as e:
        print(f"Hata: {str(e)}")
        return None, None

# TC021: Uygulama CPU Kullanımı
def test_application_cpu_usage(process_name, max_cpu_percent=50):
    cpu_usage, _ = get_application_usage(process_name)
    if cpu_usage is not None:
        if cpu_usage <= max_cpu_percent:
            log_result("TC021", f"{process_name} CPU kullanimini test et", True)
        else:
            log_result("TC021", f"{process_name} CPU kullaniminda sinir asimi: %{cpu_usage}", False)
    else:
        log_result("TC021", f"{process_name} calismiyor veya bulunamadi", False)

# TC022: Uygulama Bellek Kullanımı
def test_application_memory_usage(process_name, max_memory_mb=100):
    _, memory_usage = get_application_usage(process_name)
    if memory_usage is not None:
        if memory_usage <= max_memory_mb:
            log_result("TC022", f"{process_name} bellek kullanimini test et", True)
        else:
            log_result("TC022", f"{process_name} bellek kullaniminda sinir asimi: {memory_usage} MB", False)
    else:
        log_result("TC022", f"{process_name} calismiyor veya bulunamadi", False)

def run_performance_tests():
    process_name = "Joplin" 
    test_application_start_time()
    test_note_save_time()
    test_search_response_time()
    test_large_note_loading()
    test_multiple_note_loading()
    test_sync_time()
    test_application_cpu_usage(process_name, max_cpu_percent=50)
    test_application_memory_usage(process_name, max_memory_mb=500)
    test_mobile_performance()

    print("\n--- Performans Test Sonuclari ---")
    for result in test_results:
        print(f"Test {result['test_id']}: {result['description']} - {'Basarili' if result['success'] else 'Basarisiz'}")

if __name__ == "__main__":
    run_performance_tests()

