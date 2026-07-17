import yaml
from datetime import datetime
import os
import requests
import random
from dotenv import load_dotenv 

load_dotenv()

def fetch_real_cloud_pricing():
    """
    Primary Architecture: Attempts to fetch real-time spot pricing from a public API.
    In real-world FinOps, APIs often fail due to rate limits or endpoint deprecation.
    """
    
    api_url = "https://computeprices.com/api/v1/gpu-prices"
    api_key = os.getenv("COMPUTE_PRICES_API_KEY")
    print(f"API Key Loaded: {'YES' if api_key else 'NO (Check .env file)'}")
    if not api_key:
        return None
    headers = {
            "Authorization": f"Bearer {api_key}"
    }
    try:
        print("Sending request to API...")
        response = requests.get(api_url,headers = headers,timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f" API Response Snapshot: {str(data)[:200]}")
            if isinstance(data, dict):
                return data.get('data', data)
            elif isinstance(data, list):
                return data
        else:
            print(f" API Error Response: {response.text}")
            return None
    except Exception as e:
        print(f" Request Exception: {e}")
        return None

def extract_price_from_list(api_list, target_provider, target_gpu):
    provider_map = {
            "aws": ['aws', 'amazon'], 
            "deepinfra": ['deep infra', 'deepinfra'] 
        }    
    allowed_provs = provider_map.get(target_provider.lower(), [target_provider.lower()])
    gpu_keyword = target_gpu.replace("nvidia_", '').lower()
    
    for item in api_list:
        if not isinstance(item, dict): continue
        
        api_provs = str(item.get("provider_slug", '')) + " " + str(item.get('provider', ''))
        api_gpu = str(item.get("gpu_slug", '')) + " " + str(item.get('gpu', ''))
        
        if gpu_keyword in api_gpu.lower() and any(p in api_provs.lower() for p in allowed_provs):
            for key, val in item.items():
                if 'price' in str(key).lower() or 'cost' in str(key).lower() or 'rate' in str(key).lower():
                    try:
                        current_price = float(val)
                        if current_price > 0:
                            return current_price
                    except (ValueError, TypeError):
                        continue
    return None


def simulate_stochastic_pricing(base_rate):
    """
    Fallback Architecture: Uses a Gaussian (Normal) distribution to mathematically 
    simulate spot market volatility if the primary live API fails. 
    """
    mean_discount = 0.70
    std_dev = 0.05

    random_discount = random.gauss(mean_discount,std_dev)
    final_discount = max(0.50,min(random_discount,0.90))

    new_spot = base_rate * (1-final_discount)
    return round(new_spot,2)

def update_pricing_pipeline(file_path):
    """
    The main ETL pipeline function. It merges Data Engineering (API extraction) 
    with Quantitative Statistics (Fail-safe generation).
    """
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        
    config['meta']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    live_api_data = fetch_real_cloud_pricing()
    
    for provider, instances in config['providers'].items():
        for gpu, rates in instances.items():
            base_rate = rates['on_demand_rate']
            
            if live_api_data:
                new_spot_price = extract_price_from_list(live_api_data, provider, gpu)
            else:
                new_spot_price = None
            
            if new_spot_price is None:
                new_spot_price = simulate_stochastic_pricing(base_rate)
                status = "STATISTICAL FALLBACK"
            else:
                status = "LIVE API FETCH"
                
            config['providers'][provider][gpu]['spot_rate_baseline'] = new_spot_price
            print(f"[{provider.upper()} {gpu.upper()}] Status: {status} | Spot Rate: ${new_spot_price}")
    with open(file_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

if __name__ == "__main__":
    yaml_path = "src/cloud_pricing.yaml"
    
    if os.path.exists(yaml_path):
        print(f"--- Starting Daily ETL Pipeline: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        update_pricing_pipeline(yaml_path)
        print("--- Pipeline Execution Complete ---")
    else:
        print("CRITICAL ERROR: cloud_pricing.yaml configuration file missing.")
