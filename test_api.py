from pddiktipy import api
from pprint import pprint

# Menggunakan context manager (recommended)
with api() as client:
    print("Searching for 'Unika Soegijapranata'...")
    # Cari semua data dengan keyword
    hasil = client.search_all('Unika Soegijapranata')
    pprint(hasil)
    
    print("\nSearching for student 'Ilham Riski Wibowo'...")
    # Cari mahasiswa spesifik
    mahasiswa = client.search_mahasiswa('Ilham Riski Wibowo')
    pprint(mahasiswa)
