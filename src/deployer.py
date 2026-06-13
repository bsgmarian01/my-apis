import requests
import time
from typing import Dict, Any

class Deployer:
    def __init__(self, render_api_key: str = None):
        self.api_key = render_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        } if self.api_key else {}

    def deploy_to_render(self, github_repo_url: str, service_name: str) -> str:
        """
        Deploys the generated web service to Render via their REST API.
        Returns the public URL of the live service.
        Note: You will need to provide a Render API Key and ensure your code is pushed to a Github repo.
        """
        if not self.api_key:
            raise ValueError("Render API Key is required to perform automated deployments.")

        # 1. Create a Web Service
        # We specify Python environment, start command, and link it to the GitHub repository.
        url = "https://api.render.com/v1/services"
        payload = {
            "type": "web_service",
            "name": service_name,
            "ownerId": self._get_owner_id(),
            "repo": github_repo_url,
            "autoDeploy": "yes",
            "serviceDetails": {
                "env": "python",
                "envSpecificDetails": {
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
                },
                "plan": "free", # Deploys directly to Render Free tier
                "region": "oregon"
            }
        }

        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code != 201 and response.status_code != 200:
            raise RuntimeError(f"Render Service Creation Failed: {response.status_code} - {response.text}")
        
        service_data = response.json()
        
        # Render sometimes returns a dictionary directly or wraps the dict inside a list
        if isinstance(service_data, list) and len(service_data) > 0:
            service_data = service_data[0]
            
        try:
            # Check if key is 'service' or top level dictionary
            actual_data = service_data.get("service", service_data)
            service_id = actual_data["id"]
            live_url = actual_data["serviceDetails"]["url"]
        except (KeyError, TypeError) as e:
            raise RuntimeError(f"Unexpected response format from Render service creation: {service_data}. Error: {e}")

        # 2. Trigger initial deployment (if not automatic)
        deploy_url = f"https://api.render.com/v1/services/{service_id}/deploys"
        requests.post(deploy_url, json={}, headers=self.headers)

        return live_url

    def _get_owner_id(self) -> str:
        """
        Retrieves the owner ID associated with the Render token.
        """
        url = "https://api.render.com/v1/owners"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        owners = response.json()
        if not owners:
            raise RuntimeError("No Render owners found for this API token.")
        try:
            return owners[0]["owner"]["id"]
        except (KeyError, TypeError) as e:
            raise RuntimeError(f"Unexpected response structure from Render owners API: {owners}. Error: {e}")
