import json
import logging
import os

import requests
from base64 import b64encode
import time

url_main_back = os.environ.get("BACKEND_MAIN_VALIDATE_DEVICE", "")
 
def validate_device_on_main_back(id, token):
    url = url_main_back +str(id) + "/"  
    print("url", url) 
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "cache-control": "no-cache",
        "Authorization": f"Bearer {token}",  # Add JWT token to Authorization header
    }
    print(f"token  {token}")
    resp = requests.post(url, headers=headers) 
    logging.debug('Response: %s', resp.text)
    print("Response: ", resp.status_code)
    print("Response: ", resp.text)
    return resp
