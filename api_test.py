import requests
import json


token = "7f465dcb4aa080cf701057b66ae57cb040376af8"

headers = {
    "Authorization": f"Token {token}",
    "Accept": "application/json"
}

response = requests.get("http://127.0.0.1:8000/file_db/file_list", headers=headers)

print(response.request.headers)
print("Status:", response.status_code)
print("Raw response:")
print(response.text)

data = response.json()
print(json.dumps(data, indent=4))


url = f"http://127.0.0.1:8000/file_db/file_list/download/019d0bc2-acf5-7078-9e25-1bdb9ebca026/"
response = requests.get(url, headers=headers)

import pandas as pd
from io import BytesIO

df = pd.read_csv(BytesIO(response.content))

import matplotlib.pyplot as plt

df.plot(x="Time", y="data")
plt.show()




files = {
    "file": open("daten.csv", "rb")
}

data = {
    "description": "Uploaded via API",
    "tags": "experiment, test"
}

response = requests.post(
    "http://127.0.0.1:8000/file_db/upload/",
    headers=headers,
    files=files,
    data=data
)


print(response.json())