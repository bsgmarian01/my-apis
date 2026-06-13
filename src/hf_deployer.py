import os
import subprocess
import requests

class HFDeployer:
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username.lower()

    def deploy_space(self, space_name: str, app_dir: str) -> str:
        """
        Creates a Hugging Face Space (Docker SDK) and pushes the codebase to it.
        Returns the public URL of the live Space.
        """
        space_name = space_name.lower().replace("_", "-")
        repo_id = f"{self.username}/{space_name}"
        
        # 1. Create the Space repository via Hugging Face API if it doesn't exist
        url = "https://huggingface.co/api/repos/create"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "name": space_name,
            "type": "space",
            "sdk": "docker",  # We deploy as Docker container (FastAPI)
            "private": False
        }
        
        create_res = requests.post(url, json=payload, headers=headers)
        # 200/201 = Created/Ok, 409 = Conflict (already exists)
        if create_res.status_code not in [200, 201, 409]:
            raise RuntimeError(f"Failed to create Hugging Face Space: {create_res.status_code} - {create_res.text}")

        # 2. Write Dockerfile into the app directory so Hugging Face knows how to run it
        dockerfile_content = """FROM python:3.11-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
"""
        with open(os.path.join(app_dir, "Dockerfile"), "w", encoding="utf-8") as f:
            f.write(dockerfile_content)

        # Write README.md with Hugging Face metadata frontmatter
        readme_content = f"""---
title: {space_name.capitalize()}
emoji: 🚀
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# {space_name.capitalize()} API
Auto-deployed micro-API with Stripe key verification and rate limiting.
"""
        with open(os.path.join(app_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)

        # 3. Setup git and push to Hugging Face
        # Format remote URL with token for passwordless authentication
        hf_remote_url = f"https://{self.username}:{self.token}@huggingface.co/spaces/{self.username}/{space_name}"
        
        subprocess.run(["git", "init"], cwd=app_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "remote", "remove", "origin"], cwd=app_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "remote", "add", "origin", hf_remote_url], cwd=app_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "add", "."], cwd=app_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "Auto-deploy to Space"], cwd=app_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "branch", "-M", "main"], cwd=app_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        push_res = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=app_dir, capture_output=True, text=True)
        if push_res.returncode != 0:
            raise RuntimeError(f"Failed to push code to Hugging Face Space: {push_res.stderr}")

        # Return the embeddable direct web URL of the running Space
        return f"https://{self.username}-{space_name}.hf.space"
