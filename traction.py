import requests
import json
import os
from urllib.parse import urljoin

def send_message(conn_id, content):
    base_url = os.environ.get("TRACTION_BASE_URL")
    token = os.environ.get("TRACTION_AUTH_TOKEN")
    endpoint = f"/connections/{conn_id}/send-message"
    url = urljoin(base_url, endpoint)
    headers = {"Content-Type": "application/json", "accept": "application/json", "Authorization": f"Bearer {token}"}  
    data = {"content": content}

    print(f"Sending message to {conn_id}, message = {content}")

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Error sending message: {response.status_code}")
