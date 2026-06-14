import json
from typing import Dict, Any
from .llm_client import LLMClient

class Planner:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_api_idea(self, niche_keyword: str = None) -> Dict[str, Any]:
        """
        Queries the LLM to generate a unique microservice API idea, excluding already built ones.
        """
        import os
        # Scan builds directory to prevent duplicate generations
        builds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "builds")
        existing_apis = []
        if os.path.exists(builds_dir):
            existing_apis = [d for d in os.listdir(builds_dir) if os.path.isdir(os.path.join(builds_dir, d))]

        system_prompt = (
            "You are a business strategist specializing in high-margin API microservices sold on RapidAPI. "
            "Your goal is to propose simple, utilities-focused API microservices that solve a single developer task "
            "reliably (e.g. specialized text parsers, file format converters, data validators, mockup generators). "
            "Provide your response in raw JSON format matching this schema:\n"
            "{\n"
            "  \"name\": \"CamelCaseName\",\n"
            "  \"title\": \"Human Readable Title\",\n"
            "  \"description\": \"Detailed description of the API\",\n"
            "  \"category\": \"Developer Tools / Data / Utility\",\n"
            "  \"endpoints\": [\n"
            "    {\n"
            "      \"path\": \"/endpoint\",\n"
            "      \"method\": \"POST/GET\",\n"
            "      \"summary\": \"Brief purpose of this endpoint\",\n"
            "      \"sample_request_body\": {},\n"
            "      \"sample_response_body\": {}\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        
        prompt = "Propose one unique high-utility API microservice."
        if niche_keyword:
            prompt += f" Focus on the niche: {niche_keyword}."
            
        prompt += (
            " Structure the API to focus on data validation, text processing, format conversion, or mathematical calculations "
            "(e.g. IBAN/Swift validator, password strength analyzer, markdown parser, unit converter). "
            "Avoid complex image processing, heavy external binary dependencies, or external web scraping, "
            "ensuring the API relies on standard python packages and can be easily tested locally with 100% reliability."
        )

        if existing_apis:
            prompt += f" Do NOT propose any of the following APIs, as they have already been built: {', '.join(existing_apis)}."

        response_text = self.llm.generate(prompt=prompt, system_prompt=system_prompt, json_mode=True)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback parsing in case model adds surrounding text
            import re
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise RuntimeError(f"Could not parse JSON response from Planner: {response_text}")
