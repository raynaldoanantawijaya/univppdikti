import time
import json
from pddiktipy import api
from pprint import pprint, pformat

def log_to_file(message):
    with open("scraper_report.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)

def print_section(title):
    log_to_file(f"\n{'='*20} {title} {'='*20}")

def test_scraper():
    # Clear previous report
    with open("scraper_report.txt", "w", encoding="utf-8") as f:
        f.write("")

    log_to_file("Starting PDDIKTI API Scraper Test...")
    start_time = time.time()

    try:
        with api() as client:
            # 1. Global Statistics
            print_section("Global Statistics")
            t0 = time.time()
            dosen_count = client.get_dosen_count_active()
            mhs_count = client.get_mahasiswa_count_active()
            log_to_file(f"Active Lecturers: {dosen_count}")
            log_to_file(f"Active Students: {mhs_count}")
            log_to_file(f"Time taken: {time.time() - t0:.2f}s")

            # 2. University Search & Detail
            try:
                print_section("University Data")
                uni_keyword = "Universitas Gadjah Mada"
                log_to_file(f"Searching for: {uni_keyword}")
                t0 = time.time()
                uni_results = client.search_pt(uni_keyword)
                
                uni_data = None
                if isinstance(uni_results, list) and uni_results:
                    uni_data = uni_results[0]
                elif isinstance(uni_results, dict) and uni_results.get('data'):
                    uni_data = uni_results['data'][0]

                if uni_data:
                    log_to_file(f"Found: {uni_data['nama']} (ID: {uni_data['id']})")
                    
                    # Get Detail
                    log_to_file("Fetching details...")
                    uni_detail = client.get_detail_pt(uni_data['id'])
                    if uni_detail:
                        log_to_file(f"Address: {uni_detail.get('alamat')}")
                        log_to_file(f"Website: {uni_detail.get('website')}")
                    else:
                        log_to_file("University details returned None.")
                    
                    # Get Study Programs (Limit to 5)
                    log_to_file("Fetching study programs...")
                    prodi_results = client.get_prodi_pt(uni_data['id'], 20241)
                    
                    prodi_list = []
                    if isinstance(prodi_results, list):
                        prodi_list = prodi_results
                    elif isinstance(prodi_results, dict) and prodi_results.get('data'):
                        prodi_list = prodi_results['data']

                    if prodi_list:
                        log_to_file(f"Total Study Programs: {len(prodi_list)}")
                        for p in prodi_list[:5]:
                            log_to_file(f"- {p['nama_prodi']} ({p['jenjang_prodi']})")
                else:
                    log_to_file("University not found.")
                log_to_file(f"Time taken: {time.time() - t0:.2f}s")
            except Exception as e:
                log_to_file(f"Error in University Data section: {e}")

            # 3. Student Search & Detail
            try:
                print_section("Student Data")
                mhs_keyword = "Siti"
                log_to_file(f"Searching for student keyword: {mhs_keyword}")
                t0 = time.time()
                mhs_results = client.search_mahasiswa(mhs_keyword)
                
                mhs_data = None
                if isinstance(mhs_results, list) and mhs_results:
                    mhs_data = mhs_results[0]
                elif isinstance(mhs_results, dict) and mhs_results.get('data'):
                    mhs_data = mhs_results['data'][0]

                if mhs_data:
                    log_to_file(f"Found: {mhs_data['nama']} ({mhs_data['nim']}) at {mhs_data['nama_pt']}")
                    
                    # Get Detail
                    log_to_file("Fetching student details...")
                    mhs_detail = client.get_detail_mhs(mhs_data['id'])
                    log_to_file(pformat(mhs_detail))
                else:
                    log_to_file("Student not found.")
                log_to_file(f"Time taken: {time.time() - t0:.2f}s")
            except Exception as e:
                log_to_file(f"Error in Student Data section: {e}")

            # 4. Lecturer Search & Detail
            try:
                print_section("Lecturer Data")
                dosen_keyword = "Budi"
                log_to_file(f"Searching for lecturer keyword: {dosen_keyword}")
                t0 = time.time()
                dosen_results = client.search_dosen(dosen_keyword)
                
                dosen_data = None
                if isinstance(dosen_results, list) and dosen_results:
                    dosen_data = dosen_results[0]
                elif isinstance(dosen_results, dict) and dosen_results.get('data'):
                    dosen_data = dosen_results['data'][0]

                if dosen_data:
                    log_to_file(f"Found: {dosen_data['nama']} ({dosen_data['nidn']}) at {dosen_data['nama_pt']}")
                    
                    # Get Profile
                    log_to_file("Fetching lecturer profile...")
                    dosen_profile = client.get_dosen_profile(dosen_data['id'])
                    log_to_file(pformat(dosen_profile))
                    
                    # Get Research (Penelitian)
                    log_to_file("Fetching research history...")
                    penelitian = client.get_dosen_penelitian(dosen_data['id'])
                    
                    penelitian_list = []
                    if isinstance(penelitian, list):
                        penelitian_list = penelitian
                    elif isinstance(penelitian, dict) and penelitian.get('data'):
                        penelitian_list = penelitian['data']

                    if penelitian_list:
                        log_to_file(f"Found {len(penelitian_list)} research items.")
                        for p in penelitian_list[:3]:
                            log_to_file(f"- {p['judul_kegiatan']} ({p['tahun_kegiatan']})")
                    else:
                        log_to_file("No research history found.")
                else:
                    log_to_file("Lecturer not found.")
                log_to_file(f"Time taken: {time.time() - t0:.2f}s")
            except Exception as e:
                log_to_file(f"Error in Lecturer Data section: {e}")

    except Exception as e:
        log_to_file(f"\nERROR OCCURRED: {e}")

    print_section("Test Completed")
    log_to_file(f"Total execution time: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    test_scraper()
