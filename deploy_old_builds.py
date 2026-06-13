import os
import json
import sys
from src.hf_deployer import HFDeployer

def main():
    # 1. Load Hugging Face configurations
    config_path = "config.json"
    if not os.path.exists(config_path):
        print("[MIGRATOR] ERROR: config.json not found! Please make sure your HF_TOKEN is configured.")
        sys.exit(1)
        
    with open(config_path, "r") as f:
        config = json.load(f)
        
    token = config.get("HF_TOKEN")
    username = config.get("HF_USERNAME")
    
    if not token or not username:
        print("[MIGRATOR] ERROR: HF_TOKEN or HF_USERNAME not set in config.json.")
        sys.exit(1)
        
    deployer = HFDeployer(token=token, username=username)
    
    # 2. Scan builds directory
    builds_dir = "builds"
    if not os.path.exists(builds_dir):
        print("[MIGRATOR] No builds directory found. Nothing to deploy!")
        sys.exit(0)
        
    folders = [d for d in os.listdir(builds_dir) if os.path.isdir(os.path.join(builds_dir, d))]
    
    if not folders:
        print("[MIGRATOR] No API folders found in builds directory.")
        sys.exit(0)
        
    print(f"[MIGRATOR] Found {len(folders)} old APIs to deploy: {folders}")
    
    # 3. Loop and deploy each folder
    for folder in folders:
        app_dir = os.path.join(builds_dir, folder)
        print(f"\n[MIGRATOR] Deploying {folder} to Hugging Face...")
        try:
            # Check if main.py exists in this directory before deploying
            if not os.path.exists(os.path.join(app_dir, "main.py")):
                print(f"[MIGRATOR] Skipping {folder} - main.py not found.")
                continue
                
            live_url = deployer.deploy_space(folder, app_dir)
            print(f"[MIGRATOR] Success! {folder} deployed.")
            print(f"-> Live URL: {live_url}")
            print(f"-> Space: https://huggingface.co/spaces/{username.lower()}/{folder.lower().replace('_', '-')}")
        except Exception as e:
            print(f"[MIGRATOR] ERROR deploying {folder}: {e}")

    print("\n[MIGRATOR] Migration process completed!")

if __name__ == "__main__":
    main()
