import binascii
import requests
from flask import Flask, jsonify, request
import threading
import time
import re
from datetime import datetime

app = Flask(__name__)
jwt_tokens = {}
jwt_lock = threading.Lock()
cache = {}
cache_lock = threading.Lock()

def convert_timestamp(release_time):
    return datetime.utcfromtimestamp(release_time).strftime('%Y-%m-%d %H:%M:%S')

def get_jwt_token_sync(region):
    global jwt_tokens
    
    # JWT API endpoints for different regions
    uid_map = {
        "IND": "3828066210",
        "BR": "3939493997",
        "US": "3939493997", 
        "SAC": "3939493997",
        "NA": "3939493997",
        "ME": "3939507748",
        "SG": "3939507748",
        "CIS": "3939507748",
        "BD": "3978695859", 
        "PK": "3978693645", 
        "VN": "3978690138",
        "RU": "3939507748", 
        "ID": "3978690138", 
        "TW": "3978690138", 
        "TH": "3978690138", 
        "EUROPE": "3939493997" ##same region uid not found##
    }
    
    password_map = {
        "IND": "C41B0098956AE7B79F752FCA873C747060C71D3C17FBE4794F5EB9BD71D4DA95",
        "BR": "D08775EC0CCCEA77B2426EBC4CF04C097E0D58822804756C02738BF37578EE17",
        "US": "D08775EC0CCCEA77B2426EBC4CF04C097E0D58822804756C02738BF37578EE17",
        "SAC": "D08775EC0CCCEA77B2426EBC4CF04C097E0D58822804756C02738BF37578EE17",
        "NA": "D08775EC0CCCEA77B2426EBC4CF04C097E0D58822804756C02738BF37578EE17",
        "ME": "55A6E86C5A338D133BAD02964EFB905C7C35A86440496BC210A682146DCE9F32",
        "SG": "55A6E86C5A338D133BAD02964EFB905C7C35A86440496BC210A682146DCE9F32",
        "CIS": "55A6E86C5A338D133BAD02964EFB905C7C35A86440496BC210A682146DCE9F32",
        "BD": "769EF167B05CC4B15B2E86A8197FA0581BF1B2DD74CC706D000E90E765E5608C", 
        "PK": "787DF9D0ECF31E1127DA99B47932382732BFF9A492909F1D5AC5B59A183A5953", 
        "VN": "DB98F58E07C248FAA82CB7FD4527DC37607CFF6C2DC48D1788F52238FFF4DA83", 
        "RU": "55A6E86C5A338D133BAD02964EFB905C7C35A86440496BC210A682146DCE9F32", 
        "ID": "DB98F58E07C248FAA82CB7FD4527DC37607CFF6C2DC48D1788F52238FFF4DA83", 
        "TW": "DB98F58E07C248FAA82CB7FD4527DC37607CFF6C2DC48D1788F52238FFF4DA83", 
        "TH": "DB98F58E07C248FAA82CB7FD4527DC37607CFF6C2DC48D1788F52238FFF4DA83", 
        "EUROPE": "D08775EC0CCCEA77B2426EBC4CF04C097E0D58822804756C02738BF37578EE17" ##same region password not found##
    }
    
    uid = uid_map.get(region, uid_map["IND"])
    password = password_map.get(region, password_map["IND"])
    
    url = f"https://100067.vercel.app/token?uid={uid}&password={password}"
    
    with jwt_lock:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    jwt_tokens[region] = token
                    print(f"JWT Token for {region} updated successfully: {token[:50]}...")
                    return token
                else:
                    print(f"Failed to extract token from response for {region}")
            else:
                print(f"Failed to get JWT token for {region}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Request error for {region}: {e}")   
    return None

def ensure_jwt_token_sync(region):
    global jwt_tokens
    if region not in jwt_tokens or not jwt_tokens[region]:
        print(f"JWT token for {region} is missing. Attempting to fetch a new one...")
        return get_jwt_token_sync(region)
    return jwt_tokens[region]

def jwt_token_updater():
    while True:
        for region in ["IND", "BR", "US", "SAC", "NA", "ME", "SG", "CIS", "BD", "PK", "VN", "RU", "ID", "TW", "TH", "EUROPE"]:
            get_jwt_token_sync(region)
        time.sleep(300)

def get_api_endpoint(region):
    endpoints = {
        "IND": "https://client.ind.freefiremobile.com/LoginGetSplash",
        "BR": "https://client.us.freefiremobile.com/LoginGetSplash",
        "US": "https://client.us.freefiremobile.com/LoginGetSplash",
        "SAC": "https://client.us.freefiremobile.com/LoginGetSplash",
        "NA": "https://client.us.freefiremobile.com/LoginGetSplash",
        "ME": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "CIS": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "SG": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "BD": "https://clientbp.ggblueshark.com/LoginGetSplash", 
        "PK": "https://clientbp.ggblueshark.com/LoginGetSplash", 
        "VN": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "RU": "https://clientbp.ggblueshark.com/LoginGetSplash",  
        "ID": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "TW": "https://clientbp.ggblueshark.com/LoginGetSplash",  
        "TH": "https://clientbp.ggblueshark.com/LoginGetSplash", 
        "EUROPE": "https://client.us.freefiremobile.com/LoginGetSplash" 
    }
    return endpoints.get(region, "")

def get_region_data(region):
    region_data = {
        "IND": "03f7f38095daae1bf887928b4f2c0eb4",
        "BR": "03f7f38095daae1bf887928b4f2c0eb4",
        "US": "03f7f38095daae1bf887928b4f2c0eb4",
        "SAC": "03f7f38095daae1bf887928b4f2c0eb4",
        "NA": "9223af2eab91b7a150d528f657731074",
        "BD": "9223af2eab91b7a150d528f657731074",
        "ME": "9223af2eab91b7a150d528f657731074",
        "CIS": "5b27f0869e37f92b6f84c3a739347db1",
        "SG": "9223af2eab91b7a150d528f657731074", 
        "PK": "03f7f38095daae1bf887928b4f2c0eb4",
        "VN": "03f7f38095daae1bf887928b4f2c0eb4",
        "RU": "5b27f0869e37f92b6f84c3a739347db1", 
        "ID": "03f7f38095daae1bf887928b4f2c0eb4",
        "TW": "03f7f38095daae1bf887928b4f2c0eb4", 
        "TH": "03f7f38095daae1bf887928b4f2c0eb4",
        "EUROPE": "9223af2eab91b7a150d528f657731074" 
    }
    return region_data.get(region, "")
    return region_data.get(region, region_data["IND"])

def apis(region):
    token = ensure_jwt_token_sync(region)
    if not token:
        raise Exception(f"Failed to get JWT token for region {region}")    
    endpoint = get_api_endpoint(region)    
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)',
        'Connection': 'Keep-Alive',
        'Expect': '100-continue',
        'Authorization': f'Bearer {token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB50',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    data_hex = get_region_data(region)
    
    try:
        data = bytes.fromhex(data_hex)
        response = requests.post(
            endpoint,
            headers=headers,
            data=data,
            timeout=10
        )
        response.raise_for_status()
        return response.content.hex()
    except requests.exceptions.RequestException as e:
        print(f"API request to {endpoint} failed: {e}")
        # Try with alternative endpoint for some regions
        if "ggblueshark" not in endpoint:
            alt_endpoint = endpoint.replace("freefiremobile", "ggblueshark")
            try:
                print(f"Trying alternative endpoint: {alt_endpoint}")
                response = requests.post(
                    alt_endpoint,
                    headers=headers,
                    data=data,
                    timeout=10
                )
                response.raise_for_status()
                return response.content.hex()
            except requests.exceptions.RequestException as alt_e:
                print(f"Alternative API request also failed: {alt_e}")
        raise

@app.route('/events', methods=['GET'])
def get_events():
    try:
        region = request.args.get('region', 'IND').upper()
        
        cache_key = f"{region}"
        with cache_lock:
            cached = cache.get(cache_key)
            if cached and (datetime.now() - cached['timestamp']).seconds < 300:
                return jsonify(cached['data'])
        
        response_hex = apis(region)
        if not response_hex:
            return jsonify({"error": "Failed to get response from API"}), 500
            
        response_text = binascii.unhexlify(response_hex).decode('utf-8', errors='ignore')
        
        # Enhanced pattern matching for event images
        patterns = [
            r'https?://[^\s]+\.png',
            r'https?://[^\s]+\.jpg',
            r'https?://[^\s]+\.jpeg',
            r'https?://[^\s]+_880x520[^\s]*',
            r'https?://[^\s]*event[^\s]*',
            r'https?://[^\s]*splash[^\s]*',
            r'https?://[^\s]*promo[^\s]*'
        ]
        
        urls = []
        for pattern in patterns:
            urls.extend(re.findall(pattern, response_text, re.IGNORECASE))
        
        # Remove duplicates
        urls = list(set(urls))
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        results = []
        for url in urls:
            clean_url = url.strip()
            # Clean up URL encoding issues
            clean_url = re.sub(r'[\\"].*$', '', clean_url)
            clean_url = re.sub(r'%..', '', clean_url)
            
            # Extract event name from URL
            event_name = clean_url.split('/')[-1]
            event_name = re.sub(r'(_880x520.*|\.png|\.jpg|\.jpeg)', '', event_name, flags=re.IGNORECASE)
            event_name = event_name.replace('_', ' ').title()
            
            results.append({
                "title": event_name,
                "image_url": clean_url
            })
        
        response_data = {
            "status": "success",
            "events": results,
            "count": len(results),
            "date": current_date,
            "time": current_time,
            "region": region
        }
        
        with cache_lock:
            cache[cache_key] = {
                'data': response_data,
                'timestamp': datetime.now()
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e), "region": region}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 404

if __name__ == "__main__":
    # Pre-fetch tokens for all regions
    for region in ["IND", "BR", "US", "SAC", "NA", "ME", "SG", "CIS", "BD", "PK", "VN", "RU", "ID", "TW", "TH", "EUROPE"]:
        ensure_jwt_token_sync(region)
    
    # Start token updater thread
    threading.Thread(target=jwt_token_updater, daemon=True).start()
    app.run(host="0.0.0.0", port=5552, debug=True)