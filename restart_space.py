import os
import json
import requests
import sys

def main():
    config_path = "config.json"
    if not os.path.exists(config_path):
        print("config.json not found.")
        sys.exit(1)
        
    with open(config_path, "r") as f:
        config = json.load(f)
        
    token = config.get("HF_TOKEN")
    username = config.get("HF_USERNAME")
    space_name = "devsuite-apis"
    
    url = f"https://huggingface.co/api/spaces/{username}/{space_name}/restart"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Sending restart request to {url}...")
    res = requests.post(url, headers=headers)
    print("Status code:", res.status_code)
    print("Response:", res.text)

if __name__ == "__main__":
    main()
