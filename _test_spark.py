"""Direct Spark API test."""
import httpx
import hashlib
import hmac
import base64
import json
import time
from urllib.parse import urlparse

app_id = 'a2658974'
api_key = 'YOUR-SPARK-API-KEY'
api_secret = 'YOUR-SPARK-API-SECRET'
url = 'https://spark-api.xf-yun.com/v3.5/chat'

# Generate auth
parsed = urlparse(url)
host = parsed.netloc
date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
origin = f'host: {host}\ndate: {date}\nGET {parsed.path} HTTP/1.1'
sig = hmac.new(api_secret.encode(), origin.encode(), digestmod=hashlib.sha256).digest()
auth = base64.b64encode(
    f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{base64.b64encode(sig).decode()}"'.encode()
).decode()

headers = {
    'Content-Type': 'application/json',
    'Authorization': auth,
    'Host': host,
    'Date': date,
}

payload = {
    'header': {'app_id': app_id, 'uid': 'test'},
    'parameter': {'chat': {'domain': 'generalv3.5', 'temperature': 0.5, 'max_tokens': 50}},
    'payload': {'message': {'text': [{'role': 'user', 'content': 'Say hello in one word'}]}}
}

print(f'Testing Spark API at {url}...')
try:
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(url, json=payload, headers=headers)
        print(f'Status: {resp.status_code}')
        print(f'Response: {resp.text[:500]}')
except Exception as e:
    print(f'Error: {e}')
