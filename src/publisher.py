import requests
from typing import Dict, Any

class Publisher:
    def __init__(self, rapidapi_key: str = None):
        self.api_key = rapidapi_key
        # RapidAPI Platform/Provider API Headers
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "Content-Type": "application/json"
        } if self.api_key else {}

    def publish_to_rapidapi(self, api_name: str, description: str, live_url: str, openapi_spec: Dict[str, Any]) -> str:
        """
        Creates an API listing on RapidAPI using the OpenAPI spec of our deployed service.
        Returns the API Hub URL.
        """
        if not self.api_key:
            raise ValueError("RapidAPI Developer Key is required to register APIs.")

        # 1. Create the API definition on RapidAPI
        # Reference: https://docs.rapidapi.com/reference/createapi
        url = "https://platform-api.p.rapidapi.com/v1/apis"
        
        payload = {
            "name": api_name,
            "description": description,
            "category": "Utilities",
            "visibility": "PUBLIC",
            "targetUrl": live_url,
            "schema": openapi_spec
        }

        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        result = response.json()
        
        api_id = result.get("id")
        rapidapi_hub_url = f"https://rapidapi.com/hub/api/{api_id}"

        # 2. Add pricing plan (free/basic and a low premium tier)
        # In a real environment, you would call additional endpoints to attach subscriptions.
        
        return rapidapi_hub_url
