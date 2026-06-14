import os
import sys
import json
import subprocess
from typing import Tuple
from src.hf_deployer import HFDeployer

CONFIG_PATH = "d:/Money_making/config.json"

def load_hf_config() -> Tuple[str, str]:
    """Loads HF token and username from the config file."""
    config_path = "config.json"
    if not os.path.exists(config_path):
        config_path = CONFIG_PATH
        
    if not os.path.exists(config_path):
        raise FileNotFoundError("config.json not found in workspace or fallback path.")
        
    with open(config_path, "r") as f:
        config = json.load(f)
        
    token = config.get("HF_TOKEN")
    username = config.get("HF_USERNAME")
    return token, username

def publish_api(api_name: str, folder_name: str) -> Tuple[bool, str]:
    """
    Publishes only the newly created API to:
    1. GitHub (stages only builds/[folder_name] and commits/pushes)
    2. Hugging Face Spaces (deploys builds/[folder_name] as a standalone space)
    """
    app_dir = os.path.join("builds", folder_name)
    if not os.path.exists(app_dir):
        return False, f"API directory not found: {app_dir}"

    # 1. Hugging Face standalone deployment
    hf_msg = ""
    try:
        token, username = load_hf_config()
        if token and username:
            deployer = HFDeployer(token=token, username=username)
            space_name = folder_name.lower().replace("_", "-")
            live_url = deployer.deploy_space(space_name, app_dir)
            hf_msg = f"Hugging Face: Deployed to Space '{space_name}' ({live_url})."
        else:
            hf_msg = "Hugging Face: Skipped (credentials missing)."
    except Exception as e:
        hf_msg = f"Hugging Face Deployment failed: {e}"

    # 2. Git Publish (Only stage the new folder)
    git_msg = ""
    try:
        # Stage only the specific builds/[folder_name] directory
        subprocess.run(["git", "add", app_dir], check=True, capture_output=True)
        
        # Commit changes
        commit_res = subprocess.run(
            ["git", "commit", "-m", f"Publish JIT API: {api_name}"],
            capture_output=True,
            text=True
        )
        
        if "nothing to commit" in commit_res.stdout or "nothing added to commit" in commit_res.stdout:
            git_msg = "GitHub: No new changes to commit."
        else:
            # Push changes to main
            push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            if push_res.returncode == 0:
                git_msg = "GitHub: Pushed folder builds/{} to remote.".format(folder_name)
            else:
                git_msg = f"GitHub Push failed: {push_res.stderr}"
    except Exception as e:
        git_msg = f"GitHub Publish failed: {e}"

    return True, f"{git_msg}\n{hf_msg}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python publish_new_api.py [api_name] [folder_name]")
        sys.exit(1)
    success, message = publish_api(sys.argv[1], sys.argv[2])
    print(message)
