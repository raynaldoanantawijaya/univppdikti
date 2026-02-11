from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from pddiktipy import api
import uvicorn
import logging
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pddikti-api")

app = FastAPI(
    title="PDDIKTI API Service",
    description="REST API wrapper for pddiktipy library",
    version="1.0.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Helper function to normalize list vs dict responses
def normalize_response(response: Any) -> Optional[Dict[str, Any]]:
    if not response:
        return None
    
    if isinstance(response, list):
        if len(response) > 0:
            return response[0]
        return None
        
    if isinstance(response, dict):
        # Check if it's a wrapper dict with 'data' key which contains a list
        if 'data' in response and isinstance(response['data'], list):
             if len(response['data']) > 0:
                 return response['data'][0]
             return None
        return response
        
    return None

def normalize_list_response(response: Any) -> List[Dict[str, Any]]:
    if not response:
        return []
        
    if isinstance(response, list):
        return response
        
    if isinstance(response, dict):
        if 'data' in response and isinstance(response['data'], list):
            return response['data']
        return []
        
    return []

# --- Cached & Retried Functions ---

# Retry configuration: 3 attempts, wait 2 seconds between attempts
retry_config = {
    "stop": stop_after_attempt(3),
    "wait": wait_fixed(2),
    "retry": retry_if_exception_type(Exception),
    "reraise": True
}

@lru_cache(maxsize=128)
@retry(**retry_config)
def cached_search_mahasiswa(keyword: str):
    logger.info(f"Cache miss - Searching student: {keyword}")
    with api() as client:
        return client.search_mahasiswa(keyword)

@lru_cache(maxsize=128)
@retry(**retry_config)
def cached_get_detail_mhs(id: str):
    logger.info(f"Cache miss - Getting student detail: {id}")
    with api() as client:
        return client.get_detail_mhs(id)

@lru_cache(maxsize=128)
@retry(**retry_config)
def cached_search_dosen(keyword: str):
    logger.info(f"Cache miss - Searching lecturer: {keyword}")
    with api() as client:
        return client.search_dosen(keyword)

@lru_cache(maxsize=128)
@retry(**retry_config)
def cached_get_dosen_profile(id: str):
    logger.info(f"Cache miss - Getting lecturer profile: {id}")
    with api() as client:
        return client.get_dosen_profile(id)

@lru_cache(maxsize=128)
@retry(**retry_config)
def cached_search_pt(keyword: str):
    logger.info(f"Cache miss - Searching university: {keyword}")
    with api() as client:
        results = client.search_pt(keyword)
        
        # FIX: The API returns the Name in the 'id' field for some reason.
        # We need to extract the REAL ID from 'website_link' if possible.
        # Structure: "website_link": "/data_pt/REAL_ID"
        if results:
            data_list = []
            if isinstance(results, list):
                data_list = results
            elif isinstance(results, dict) and 'data' in results and isinstance(results['data'], list):
                data_list = results['data']
            
            for item in data_list:
                if 'website_link' in item and '/data_pt/' in item['website_link']:
                    real_id = item['website_link'].split('/data_pt/')[-1]
                    item['id'] = real_id # Overwrite with real ID
        
        return results

@lru_cache(maxsize=128)
@retry(**retry_config)
def cached_get_detail_pt(id: str):
    logger.info(f"Cache miss - Getting university detail: {id}")
    with api() as client:
        try:
            # Try the standard endpoint first
            detail = client.get_detail_pt(id)
            if detail:
                return detail
                
            # If standard endpoint fails (e.g. 404), build a fallback object
            logger.warning(f"Standard detail endpoint failed for {id}, attempting fallback...")
            
            # 1. Fetch Stats (works)
            stats = client.get_mahasiswa_pt(id) or {}
            
            # 2. Fetch Logo (works)
            logo = client.get_logo_pt(id)
            
            # Construct a "Partial" detail object
            fallback_detail = {
                "id": id,
                "nama_pt": "Data Universitas (Limited)", # We don't have the name unless we pass it, but generic is fine or we rely on frontend
                "kode_pt": stats.get('kode_pt', '-'),
                "status_pt": "Aktif", # Assumption or missing
                "alamat": "Alamat tidak tersedia (Endpoint utama bermasalah)",
                "website": "-",
                "email": "-",
                "jumlah_mahasiswa": stats.get('mean_jumlah_baru', 0), # Not exact but something
                "logo_base64": logo,
                "fallback_mode": True
            }
            return fallback_detail
            
        except Exception as e:
            logger.error(f"Error fetching university details: {e}")
            return None


# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to PDDIKTI API Service. Visit /docs for documentation."}

@app.get("/search/mahasiswa/{keyword}")
def search_mahasiswa(keyword: str):
    try:
        results = cached_search_mahasiswa(keyword)
        normalized = normalize_list_response(results)
        return {"data": normalized, "count": len(normalized)}
    except Exception as e:
        logger.error(f"Error searching student: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/detail/mahasiswa/{id}")
def get_detail_mahasiswa(id: str):
    try:
        result = cached_get_detail_mhs(id)
        if not result:
            raise HTTPException(status_code=404, detail="Student not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/dosen/{keyword}")
def search_dosen(keyword: str):
    try:
        results = cached_search_dosen(keyword)
        normalized = normalize_list_response(results)
        return {"data": normalized, "count": len(normalized)}
    except Exception as e:
        logger.error(f"Error searching lecturer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/detail/dosen/{id}")
def get_detail_dosen(id: str):
    try:
        profile = cached_get_dosen_profile(id)
        return profile if profile else {}
    except Exception as e:
        logger.error(f"Error getting lecturer detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/university/{keyword}")
def search_university(keyword: str):
    try:
        results = cached_search_pt(keyword)
        normalized = normalize_list_response(results)
        return {"data": normalized, "count": len(normalized)}
    except Exception as e:
        logger.error(f"Error searching university: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/detail/university/{id}")
def get_detail_university(id: str):
    try:
        detail = cached_get_detail_pt(id)
        return detail if detail else {}
    except Exception as e:
        logger.error(f"Error getting university detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("pddikti_service:app", host="0.0.0.0", port=8000, reload=True)

