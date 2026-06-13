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
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. List all spaces for the user
    url = f"https://huggingface.co/api/spaces?author={username}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"Failed to list spaces: {res.status_code} - {res.text}")
        sys.exit(1)
        
    spaces = res.json()
    print(f"Found {len(spaces)} spaces:")
    for space in spaces:
        print(f" - {space['id']} (runtime: {space.get('runtime', {}).get('stage', 'unknown')})")
        
    # 2. Pause all spaces except 'devsuite-apis'
    target_space = f"{username}/devsuite-apis".lower()
    for space in spaces:
        space_id = space['id'].lower()
        if space_id != target_space:
            stage = space.get('runtime', {}).get('stage', '')
            if stage not in ['PAUSED', 'STOPPED']:
                print(f"Pausing space {space_id}...")
                pause_url = f"https://huggingface.co/api/spaces/{space['id']}/pause"
                pause_res = requests.post(pause_url, headers=headers)
                print(f"Response: {pause_res.status_code} - {pause_res.text}")
                
    # 3. Now restart 'devsuite-apis'
    restart_url = f"https://huggingface.co/api/spaces/{username}/devsuite-apis/restart"
    print(f"Restarting target space: {target_space}...")
    restart_res = requests.post(restart_url, headers=headers)
    print(f"Response: {restart_res.status_code} - {restart_res.text}")

if __name__ == "__main__":
    main()
