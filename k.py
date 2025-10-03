import requests
import os

# Replace with your API key (or set it in environment as GEMINI_API_KEY)
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAw2ZdBX4UGnJscJA8VnMSb_p2IgcJHab8")

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

data = {
    "contents": [
        {"role": "user", "parts": [{"text": "Hello Gemini, are you working?"}]}
    ]
}

response = requests.post(url, headers=headers, json=data)

print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception as e:
    print("Error decoding JSON:", e)
    print("Raw Response:", response.text)
