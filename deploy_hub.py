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
    
    # We deploy ONLY APIHub
    app_dir = os.path.join("builds", "APIHub")
    space_name = "devsuite-apis"  # Let's call it devsuite-apis or apihub or similar
    
    print(f"\n[MIGRATOR] Deploying APIHub as {space_name} to Hugging Face...")
    try:
        # Check if main.py exists in this directory before deploying
        if not os.path.exists(os.path.join(app_dir, "main.py")):
            print(f"[MIGRATOR] Error - APIHub main.py not found in {app_dir}.")
            sys.exit(1)
            
        live_url = deployer.deploy_space(space_name, app_dir)
        print(f"[MIGRATOR] Success! APIHub deployed.")
        print(f"-> Live URL: {live_url}")
        print(f"-> Space: https://huggingface.co/spaces/{username.lower()}/{space_name.lower().replace('_', '-')}")
    except Exception as e:
        print(f"[MIGRATOR] ERROR deploying APIHub: {e}")

if __name__ == "__main__":
    main()
