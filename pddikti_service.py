from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List, Dict, Any
from pddiktipy import api
import uvicorn
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pddikti-api")

app = FastAPI(
    title="PDDIKTI API Service",
    description="REST API wrapper for pddiktipy library",
    version="1.0.0"
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

# --- Cached Functions ---

@lru_cache(maxsize=128)
def cached_search_mahasiswa(keyword: str):
    logger.info(f"Cache miss - Searching student: {keyword}")
    with api() as client:
        return client.search_mahasiswa(keyword)

@lru_cache(maxsize=128)
def cached_get_detail_mhs(id: str):
    logger.info(f"Cache miss - Getting student detail: {id}")
    with api() as client:
        return client.get_detail_mhs(id)

@lru_cache(maxsize=128)
def cached_search_dosen(keyword: str):
    logger.info(f"Cache miss - Searching lecturer: {keyword}")
    with api() as client:
        return client.search_dosen(keyword)

@lru_cache(maxsize=128)
def cached_get_dosen_profile(id: str):
    logger.info(f"Cache miss - Getting lecturer profile: {id}")
    with api() as client:
        return client.get_dosen_profile(id)

@lru_cache(maxsize=128)
def cached_search_pt(keyword: str):
    logger.info(f"Cache miss - Searching university: {keyword}")
    with api() as client:
        return client.search_pt(keyword)

@lru_cache(maxsize=128)
def cached_get_detail_pt(id: str):
    logger.info(f"Cache miss - Getting university detail: {id}")
    with api() as client:
        return client.get_detail_pt(id)


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

