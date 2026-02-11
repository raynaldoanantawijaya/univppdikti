import requests
import time
from pprint import pprint

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing PDDIKTI REST API...")
    
    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(5):
        try:
            r = requests.get(f"{BASE_URL}/")
            if r.status_code == 200:
                print("Server is up!")
                break
        except:
            time.sleep(2)
    else:
        print("Server failed to start.")
        return

    # Test 1: Search Student
    print("\n[GET] /search/mahasiswa/Raynaldo")
    r = requests.get(f"{BASE_URL}/search/mahasiswa/Raynaldo")
    data = r.json()
    print(f"Status: {r.status_code}")
    print(f"Count: {data.get('count')}")
    if data.get('data'):
        first_student = data['data'][0]
        print(f"First result: {first_student['nama']}")
        
        # Test 2: Student Detail
        student_id = first_student['id']
        print(f"\n[GET] /detail/mahasiswa/{student_id}")
        r = requests.get(f"{BASE_URL}/detail/mahasiswa/{student_id}")
        print(f"Status: {r.status_code}")
        pprint(r.json())

    # Test 3: Search University
    print("\n[GET] /search/university/Gadjah Mada")
    r = requests.get(f"{BASE_URL}/search/university/Gadjah Mada")
    data = r.json()
    print(f"Status: {r.status_code}")
    print(f"Count: {data.get('count')}")
    
if __name__ == "__main__":
    test_api()
