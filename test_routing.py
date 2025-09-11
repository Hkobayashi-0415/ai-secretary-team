import requests
import json

url = "http://localhost:8000/api/v1/routing/route"
data = {
    "prompt": "来月の売上を予測するための報告書を作成して",
    "assistant_id": "f01fc570-0eb9-48f0-98c5-bfb0b700fe56"
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")