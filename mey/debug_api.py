import os
import requests
from dotenv import load_dotenv

# Try to load .env from project root (parent of current dir)
# current dir is .../mey, so parent is .../budongsan3_project
env_path = os.path.join(os.path.dirname(os.getcwd()), '.env')
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

API_KEY = os.getenv('PUBLIC_API_KEY')
print(f"API_KEY loaded: {'Yes' if API_KEY else 'No'}")
if API_KEY:
    print(f"API_KEY (first 5 chars): {API_KEY[:5]}...")
else:
    print("API_KEY is None")

# Construct URL
# If API_KEY is None, correct URL structure implies we might be sending 'None' literally or it fails before.
# Let's test what the notebook executes:
# BASE_URL = f'http://openapi.seoul.go.kr:8088/{API_KEY}/json/tbLnOpendataRtmsV'
if API_KEY is None:
    # Simulating what happens in the notebook if env var is missing
    # In python: f"{None}" becomes "None" string
    request_key = "None"
else:
    request_key = API_KEY

base_url = f'http://openapi.seoul.go.kr:8088/{request_key}/json/tbLnOpendataRtmsV/1/5/2024/11680'
print(f"Testing URL: {base_url}")

try:
    res = requests.get(base_url)
    print(f"Status Code: {res.status_code}")
    print(f"Response Content (first 200 chars):\n{res.text[:200]}")
    
    # Try parsing JSON
    data = res.json()
    print("JSON decode successful")
except Exception as e:
    print(f"JSON decode failed: {e}")
