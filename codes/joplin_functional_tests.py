from joplin_api import JoplinTestClient

api = JoplinTestClient()

test_results = []

def create_standart_note():
    response = api.post("/notes", json={
        "title": "Standart Note Olusturma",
        "body": "Bu testler icin olusturulmus standart bir test notudur."
    })
    return response.json()["id"]
        
def log_result(test_id, description, success):
    test_results.append({
        "test_id": test_id,
        "description": description,
        "success": success
    })
    print(f"Test {test_id}: {description} - {'Basarili' if success else 'Basarisiz'}")

# TC001: Note Olusturma
def create_note():
    try:
        response = api.post("/notes", json={
            "title": "Test Note",
            "body": "Bu bir test notudur."
        })
        if response.status_code == 200:
            note_id = response.json()["id"]
            log_result("TC001", "Note olusturma", True)
            return note_id
        else:
            log_result("TC001", "Note olusturma", False)
    except Exception as e:
        log_result("TC001", f"Note olusturma hatasi: {str(e)}", False)

# TC002: Note Guncelleme
def update_note(note_id):
    try:
        response = api.put(f"/notes/{note_id}", json={
            "body": "Bu note guncellendi."
        })
        if response.status_code == 200:
            log_result("TC002", "Note guncelleme", True)
        else:
            log_result("TC002", "Note guncelleme", False)
    except Exception as e:
        log_result("TC002", f"Note guncelleme hatasi: {str(e)}", False)

# TC003: Note Silme
def delete_note(note_id):
    try:
        response = api.delete(f"/notes/{note_id}")
        if response.status_code == 200:
            log_result("TC003", "Note silme", True)
        else:
            log_result("TC003", "Note silme", False)
    except Exception as e:
        log_result("TC003", f"Note silme hatasi: {str(e)}", False)

# TC004: Etiket Ekleme
def add_tag(note_id):
    try:
        response = api.post("/tags", json={
            "title": "Test Tag"+str(note_id)
        })
        if response.status_code == 200:
            tag_id = response.json()["id"]
            api.post(f"/tags/{tag_id}/notes", json={
                "id": note_id
            })
            log_result("TC004", "Etiket ekleme", True)
            return tag_id
        else:
            log_result("TC004", "Etiket ekleme", False)
    except Exception as e:
        log_result("TC004", f"Etiket ekleme hatasi: {str(e)}", False)

# TC005: Etiket Kaldirma
def remove_tag(tag_id):
    try:
        response = api.delete(f"/tags/{tag_id}")
        if response.status_code == 200:
            log_result("TC005", "Etiket kaldirma", True)
        else:
            log_result("TC005", "Etiket kaldirma", False)
    except Exception as e:
        log_result("TC005", f"Etiket kaldirma hatasi: {str(e)}", False)

# TC006: Markdown Formatinda Disa Aktarma
def export_note_md(note_id):
    try:
        response = api.get(f"/notes/{note_id}/export", params={"format": "md"})
        if response.status_code == 200:
            log_result("TC006", "Disa aktarma (Markdown)", True)
        else:
            log_result("TC006", "Disa aktarma (Markdown)", False)
    except Exception as e:
        log_result("TC006", f"Disa aktarma (Markdown) hatasi: {str(e)}", False)

# TC007: PDF Formatinda Disa Aktarma
def export_note_pdf(note_id):
    try:
        response = api.get(f"/notes/{note_id}/export", params={"format": "pdf"})
        if response.status_code == 200:
            log_result("TC007", "Disa aktarma (PDF)", True)
        else:
            log_result("TC007", "Disa aktarma (PDF)", False)
    except Exception as e:
        log_result("TC007", f"Disa aktarma (PDF) hatasi: {str(e)}", False)

# TC008: Note Arama
def search_notes(query):
    try:
        response = api.get("/search", params={"query": query})
        if response.status_code == 200 and len(response.json()["items"]) > 0:
            log_result("TC008", f"Note arama ('{query}')", True)
        else:
            log_result("TC008", f"Note arama ('{query}')", False)
    except Exception as e:
        log_result("TC008", f"Note arama hatasi: {str(e)}", False)

# TC009: Notlari Siralama
def sort_notes():
    try:
        response = api.get("/notes", params={"order_by": "updated_time"})
        if response.status_code == 200 and len(response.json()) > 0:
            log_result("TC009", "Notlari siralama", True)
        else:
            log_result("TC009", "Notlari siralama", False)
    except Exception as e:
        log_result("TC009", f"Notlari siralama hatasi: {str(e)}", False)

# TC010: Cop Kutusundan Geri Yukleme
def restore_from_trash(note_id):
    try:
        delete_response = api.delete(f"/notes/{note_id}")
        if delete_response.status_code == 200:
            restore_response = api.post(f"/notes/{note_id}/restore")
            if restore_response.status_code == 200:
                log_result("TC010", "Cop kutusundan geri yukleme", True)
            else:
                log_result("TC010", "Cop kutusundan geri yukleme basarisiz", False)
        else:
            log_result("TC010", "Note silme basarisiz (geri yukleme testi yapilamadi)", False)
    except Exception as e:
        log_result("TC010", f"Cop kutusundan geri yukleme hatasi: {str(e)}", False)

# TC011: Notu favorilere ekleme
def add_to_favorites(note_id):
    try:
        response = api.put(f"/notes/{note_id}", json={
            "is_favorite": True
        })
        if response.status_code == 200:
            log_result("TC011", "Notu favorilere ekleme", True)
        else:
            log_result("TC011", "Notu favorilere ekleme", False)
    except Exception as e:
        log_result("TC011", f"Notu favorilere ekleme hatasi: {str(e)}", False)

# TC012: Notu favorilerden cikarma
def remove_from_favorites(note_id):
    try:
        response = api.put(f"/notes/{note_id}", json={
            "is_favorite": False
        })
        if response.status_code == 200:
            log_result("TC012", "Notu favorilerden cikarma", True)
        else:
            log_result("TC012", "Notu favorilerden cikarma", False)
    except Exception as e:
        log_result("TC012", f"Notu favorilerden cikarma hatasi: {str(e)}", False)

# TC013: Notu sifre korumali hale getirme
def make_note_password_protected(note_id, password):
    try:
        response = api.put(f"/notes/{note_id}", json={
            "encryption_cipher_text": password
        })
        if response.status_code == 200:
            log_result("TC013", "Notu sifre korumali hale getirme", True)
        else:
            log_result("TC013", "Notu sifre korumali hale getirme", False)
    except Exception as e:
        log_result("TC013", f"Notu sifre korumali hale getirme hatasi: {str(e)}", False)
        
def run_tests():
    note_id = create_note()
    note_id_2 = create_note()
    #standart_note_id = create_standart_note()
    #print(standart_note_id)
    if note_id:
        update_note(note_id)
        
        tag_id = add_tag(note_id)
        if tag_id:
            remove_tag(tag_id)
        export_note_md(note_id)
        export_note_pdf(note_id)
        search_notes("Test Note")
        sort_notes()
        add_to_favorites(note_id)
        remove_from_favorites(note_id)
        make_note_password_protected(note_id, "123456")
        delete_note(note_id)
    
    if note_id_2:
        restore_from_trash(note_id_2)
        
    print("\n--- Test Sonuclari ---")
    for result in test_results:
        print(f"Test {result['test_id']}: {result['description']} - {'Basarili' if result['success'] else 'Basarisiz'}")

if __name__ == "__main__":
    run_tests()