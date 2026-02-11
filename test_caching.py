import requests
import time

BASE_URL = "http://127.0.0.1:8001"

def log(msg):
    with open("caching_result.txt", "a") as f:
        f.write(msg + "\n")
    print(msg)

def test_caching():
    # Clear log file
    with open("caching_result.txt", "w") as f:
        f.write("")

    log("Testing API Caching...")
    
    # Wait for server
    time.sleep(2)
    
    keyword = "Raynaldo"
    url = f"{BASE_URL}/search/mahasiswa/{keyword}"
    
    session = requests.Session()
    
    log(f"\n1. First Request (Cold Cache) to {url}")
    t0 = time.time()
    try:
        r1 = session.get(url)
        t1 = time.time()
        time_cold = t1 - t0
        log(f"Status: {r1.status_code}")
        log(f"Time: {time_cold:.4f}s")
    except Exception as e:
        log(f"First request failed: {e}")
        return
    
    log(f"\n2. Second Request (Warm Cache) to {url}")
    t0 = time.time()
    try:
        r2 = session.get(url)
        t1 = time.time()
        time_warm = t1 - t0
        log(f"Status: {r2.status_code}")
        log(f"Time: {time_warm:.4f}s")
        
        if time_warm < 0.5: 
            log("\nSUCCESS: Second request was fast!")
            improvement = time_cold / time_warm if time_warm > 0 else 0
            log(f"Speed improvement: {improvement:.1f}x faster")
        else:
            log("\nWARNING: Caching might not be working as expected.")
            
    except Exception as e:
        log(f"Second request failed: {e}")

if __name__ == "__main__":
    test_caching()
