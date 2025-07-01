import requests
import time

BASE_URL = "http://localhost:41184"
TOKEN = "08a64ca62261a0db5150e84650c1f6dfe81d8b25b88983f2e828d696bf1c4b59079fdc93109c97c56a6111e2787782750f826c0a22f18792c84774457e90b5a3"

test_results = []

# secuirty testleri

def log_result(test_id, description, success):
    test_results.append({
        "test_id": test_id,
        "description": description,
        "success": success
    })
    print(f"Test {test_id}: {description} - {'Basarili' if success else 'Basarisiz'}")
    
# TC023: Hatali Sifre Girisi
def test_incorrect_password():
    try:
        response = requests.post(f"{BASE_URL}/auth", json={
            "username": "testuser",
            "password": "truepassword"
        })
        if response.status_code == 200:  
            log_result("TC023", "Hatali sifre girisi engellendi", True)
        else:
            log_result("TC023", "Hatali sifre girisi engellenemedi", False)
    except Exception as e:
        log_result("TC023", f"Hatali sifre testi hatasi: {str(e)}", False)

# TC024: SQL Enjeksiyonu Korumasi
def test_sql_injection():
    try:
        malicious_payload = "' OR '1'='1"
        response = requests.post(f"{BASE_URL}/notes?token={TOKEN}", json={
            "title": malicious_payload,
            "body": "SQL injection test"
        })
        if response.status_code != 200 or malicious_payload in response.text:
            log_result("TC024", "SQL enjeksiyonu engellendi", True)
        else:
            log_result("TC024", "SQL enjeksiyonu engellenemedi", False)
    except Exception as e:
        log_result("TC024", f"SQL enjeksiyonu testi hatasi: {str(e)}", False)

# TC025: Bos Sifre Uyarisinin Goruntulenmesi
def test_empty_password():
    try:
        response = requests.post(f"{BASE_URL}/auth", json={
            "username": "testuser",
            "password": ""
        })
        if response.status_code == 400:  # Hatalı istek
            log_result("TC025", "Bos sifre uyarisinin goruntulenmesi", True)
        else:
            log_result("TC025", "Bos sifre uyarisinin goruntulenememesi", False)
    except Exception as e:
        log_result("TC025", f"Bos sifre testi hatasi: {str(e)}", False)

# TC026: XSS Korumasi
def test_xss_protection():
    try:
        malicious_script = "<script>alert('XSS');</script>"
        response = requests.post(f"{BASE_URL}/notes?token={TOKEN}", json={
            "title": "XSS Test",
            "body": malicious_script
        })
        if response.status_code == 200 and malicious_script not in response.text:
            log_result("TC026", "XSS korumasi etkin", True)
        else:
            log_result("TC026", "XSS korumasi etkin degil", False)
    except Exception as e:
        log_result("TC026", f"XSS testi hatasi: {str(e)}", False)

# TC027: Oturum Suresi
def test_session_timeout():
    try:
        time.sleep(900)  # 15 dakika sürüyor
        response = requests.get(f"{BASE_URL}/notes?token={TOKEN}")
        if response.status_code == 401:
            log_result("TC027", "Oturum suresi doldu", True)
        else:
            log_result("TC027", "Oturum suresi dolmadi", False)
    except Exception as e:
        log_result("TC027", f"Oturum suresi testi hatasi: {str(e)}", False)

# TC028: Sifreleme Kontrolu
def test_encryption():
    try:
        response = requests.get(f"{BASE_URL}/notes?token={TOKEN}")
        if response.status_code == 200 and "encrypted" in response.text:
            log_result("TC028", "Sifreleme kontrolu basarili", True)
        else:
            log_result("TC028", "Sifreleme kontrolu basarisiz", False)
    except Exception as e:
        log_result("TC028", f"Sifreleme testi hatasi: {str(e)}", False)

# TC029: Yetkisiz Erisim
def test_unauthorized_access():
    try:
        response = requests.get(f"{BASE_URL}/notes/unauthorized_note_id?token=INVALID_TOKEN")
        if response.status_code == 403: 
            log_result("TC030", "Yetkisiz erisim engellendi", True)
        else:
            log_result("TC030", "Yetkisiz erisim engellenemedi", False)
    except Exception as e:
        log_result("TC030", f"Yetkisiz erisim testi hatasi: {str(e)}", False)

# TC030: Guvenlik Gunluklerinin Dogrulanmasi
def test_security_logs():
    try:
        response = requests.get(f"{BASE_URL}/logs?token={TOKEN}")
        if response.status_code == 200 and "failed_login_attempts" in response.json():
            log_result("TC031", "Guvenlik gunlukleri dogrulandi", True)
        else:
            log_result("TC031", "Guvenlik gunlukleri dogrulanamadi", False)
    except Exception as e:
        log_result("TC031", f"Guvenlik gunlukleri testi hatasi: {str(e)}", False)

# TC031: Senkronizasyon Guvenligi
def test_sync_security():
    try:
        response = requests.post(f"{BASE_URL}/sync?token={TOKEN}")
        if response.status_code == 200 and "encrypted" in response.text:
            log_result("TC031", "Senkronizasyon guvenligi dogrulandi", True)
        else:
            log_result("TC031", "Senkronizasyon guvenligi saglanamadi", False)
    except Exception as e:
        log_result("TC031", f"Senkronizasyon guvenligi testi hatasi: {str(e)}", False)

# TC032: Dogrulama Mesaji
def test_confirmation_message():
    try:
        response = requests.delete(f"{BASE_URL}/notes/some_note_id?token={TOKEN}")
        if response.status_code == 200 and "Are you sure?" in response.text:
            log_result("TC033", "Dogrulama mesaji goruntulendi", True)
        else:
            log_result("TC033", "Dogrulama mesaji goruntulenemedi", False)
    except Exception as e:
        log_result("TC033", f"Dogrulama mesaji testi hatasi: {str(e)}", False)

def run_security_tests():

    test_incorrect_password()
    test_sql_injection()
    test_empty_password()
    test_xss_protection()
    test_session_timeout()
    test_encryption()
    test_unauthorized_access()
    test_security_logs()
    test_sync_security()
    test_confirmation_message()

    print("\n--- Guvenlik Test Sonuclari ---")
    for result in test_results:
        print(f"Test {result['test_id']}: {result['description']} - {'Basarili' if result['success'] else 'Basarisiz'}")

if __name__ == "__main__":
    run_security_tests()
