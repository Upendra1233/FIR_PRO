# direct_calls/services.py
import requests
import logging
from datetime import datetime, timedelta
from django.core.cache import cache


logger = logging.getLogger(__name__)

def get_ialert_token():
    """Cached token retrieval for IAlert API."""
    cached_token = cache.get('ialert_token')
    if cached_token:
        return cached_token
    
    token_url = "https://ialertuat.ashokleyland.com/operationuat/admin/api/login/generate-token"
    token_header = {"token": "YjhhNjBlYmU4NDA3M2RhM2I0YzRhNDMxMzc1NjQxYTM="}
    try:
        resp = requests.get(token_url, headers=token_header, timeout=15)
        resp.raise_for_status()
        token = resp.json().get('token') or resp.text.strip()
        # Cache token for 23 hours
        cache.set('ialert_token', token, 82800)
        return token
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to get IAlert token: %s", e)
        return None

def post_update_to_ialert(ticket_id, remarks, comments, engineer_name, token):
    """Post update to IAlert API."""
    update_url = "https://ialertuat.ashokleyland.com/operationuat/admin/api/supportticket/support-ticket-status"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {"ticket_id": ticket_id, "remarks": remarks, "comments": comments, "engineer_name": engineer_name}
    
    try:
        resp = requests.post(update_url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        return True, resp.status_code, resp.json()
    except requests.exceptions.RequestException as e:
        logger.exception("IAlert update failed: %s", e)
        return False, getattr(e.response, 'status_code', None), str(e)

def fetch_darby_asset_data(vin):
    """Fetch asset info from Darby API with caching."""
    cache_key = f'darby_asset_{vin}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    api_url = "https://api.al.drivewithdarby.com/v1/assets/dynamic/search"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzM4NCJ9...",  # Use env var in production
        "Content-Type": "application/json"
    }
    payload = {"assetType": "DEVICE", "filters": {"vin": [vin]}}
    
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        assets = resp.json().get("results", [])
        asset = next((a for a in assets if a.get("vin", "").strip().upper() == vin), None)
        
        # Cache for 1 hour
        cache.set(cache_key, asset, 3600)
        return asset
    except requests.exceptions.RequestException as e:
        logger.exception("Darby asset fetch failed: %s", e)
        return None

def fetch_darby_analytics(asset_id, days=7):
    """Fetch analytics from Darby API."""
    cache_key = f'darby_analytics_{asset_id}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=days-1)
    startTime = start_dt.strftime('%Y-%m-%dT00:00:00Z')
    endTime = end_dt.strftime('%Y-%m-%dT23:59:59Z')
    
    api_url = f"https://web.al.drivewithdarby.com/v1/messages/asset/{asset_id}/analytics-daily-summary?startTime={startTime}&endTime={endTime}"
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzM4NCJ9..."}
    
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cache.set(cache_key, data, 3600)
        return data
    except requests.exceptions.RequestException as e:
        logger.exception("Darby analytics fetch failed: %s", e)
        return None