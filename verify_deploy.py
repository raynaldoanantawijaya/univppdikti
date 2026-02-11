import requests
import time
from pprint import pprint

BASE_URL = "https://univppdikti.vercel.app"

def test_api():
    print(f"Testing Live API at {BASE_URL}...")
    
    try:
        # Test Root
        print("\n[GET] /")
        r = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"Status: {r.status_code}")
        print(r.json())

        # Test Search Student
        print("\n[GET] /search/mahasiswa/Raynaldo")
        t0 = time.time()
        r = requests.get(f"{BASE_URL}/search/mahasiswa/Raynaldo", timeout=15)
        print(f"Status: {r.status_code}")
        print(f"Time: {time.time() - t0:.2f}s")
        data = r.json()
        print(f"Count: {data.get('count')}")
        if data.get('data'):
             print(f"Name: {data['data'][0]['nama']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
