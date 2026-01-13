from fastapi import APIRouter
from pathlib import Path
import importlib.util

from app.scanner.metadata_functions.folder_collection_config import find_folder_collection_config
router = APIRouter(prefix="/api/test")

@router.get("/scraper/{query}")
async def get_collections(query: str):
    
    folder_collection_configs = await find_folder_collection_config(Path("/Volumes/GoettePool/Porn/Studios/LegalPorno/"))
    scraper_spec = importlib.util.spec_from_file_location("scraper", "/Volumes/GoettePool/Porn/Studios/LegalPorno/__wannawatch.py")
    if scraper_spec and scraper_spec.loader:
        scraper = importlib.util.module_from_spec(spec=scraper_spec)
        scraper_spec.loader.exec_module(scraper)

        search_results = scraper.search(title=query)
        if len(search_results) > 0 and len(folder_collection_configs) > 0:
            
            return scraper.fetch_metadata(search_result=search_results[1], potential_collections=folder_collection_configs[0].data.potential_collections)
    
    return "No results"
