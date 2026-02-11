from pddiktipy import api
from pprint import pprint

def log_to_file(message):
    with open("student_result.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)

def check_student():
    # Clear previous result
    with open("student_result.txt", "w", encoding="utf-8") as f:
        f.write("")

    name = "Raynaldo Ananta Wijaya"
    log_to_file(f"Searching for student: {name}...")
    
    try:
        with api() as client:
            # Search for the student
            results = client.search_mahasiswa(name)
            
            students = []
            if isinstance(results, list):
                students = results
            elif isinstance(results, dict) and results.get('data'):
                students = results['data']
            
            if students:
                log_to_file(f"\nFound {len(students)} student(s):")
                for i, mhs in enumerate(students):
                    log_to_file(f"\n[{i+1}] Name: {mhs['nama']}")
                    log_to_file(f"    NIM: {mhs['nim']}")
                    log_to_file(f"    University: {mhs['nama_pt']}")
                    log_to_file(f"    Program: {mhs['nama_prodi']}")
                    
                    # Fetch detailed info for the first match or all?
                    # Let's fetch detail for all found to be sure it's the right person
                    log_to_file("    Fetching details...")
                    detail = client.get_detail_mhs(mhs['id'])
                    if detail:
                         log_to_file(f"    Status: {detail.get('status_saat_ini')}")
                         log_to_file(f"    Entry Year: {detail.get('tahun_masuk')}")
                    else:
                        log_to_file("    Could not retrieve details.")
            else:
                log_to_file("\nStudent not found.")
                
    except Exception as e:
        log_to_file(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    check_student()
