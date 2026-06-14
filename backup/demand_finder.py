import os
import json
import requests
from datetime import datetime

REGISTRY_PATH = "registry.json"

# Search terms to query GitHub Issues
GITHUB_QUERIES = [
    '"is there an api for"',
    '"looking for an api"',
    '"need an api for"'
]

def load_registry():
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"ideas": [], "apis": []}

def save_registry(registry):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

def search_github_demand():
    headers = {
        "User-Agent": "APIFactoryFinder/2.0",
        "Accept": "application/vnd.github+json"
    }
    
    found_ideas = []
    
    for query in GITHUB_QUERIES:
        url = f"https://api.github.com/search/issues?q={query}+state:open+type:issue"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
            
            data = response.json()
            items = data.get("items", [])
            
            for item in items:
                title = item.get("title", "")
                body = item.get("body", "") or ""
                html_url = item.get("html_url", "")
                created_at = item.get("created_at", "")
                issue_id = str(item.get("id", ""))
                
                # Exclude pull requests (they also appear in issues search)
                if "pull_request" in item:
                    continue
                
                # Truncate description
                desc = body[:500] + ("..." if len(body) > 500 else "")
                
                found_ideas.append({
                    "id": f"gh_{issue_id}",
                    "title": title,
                    "description": desc,
                    "source": "GitHub",
                    "url": html_url,
                    "timestamp": created_at,
                    "status": "pending"
                })
        except Exception:
            pass
            
    # Load and update registry
    registry = load_registry()
    existing_ids = {idea["id"] for idea in registry.get("ideas", []) if "id" in idea}
    
    new_count = 0
    for idea in found_ideas:
        if idea["id"] not in existing_ids:
            registry["ideas"].append(idea)
            new_count += 1
            
    save_registry(registry)
    return new_count, len(found_ideas)

# Alias for compatibility with factory_ui.py
def search_reddit_demand():
    return search_github_demand()

if __name__ == "__main__":
    print("Scanning GitHub Issues for API demands...")
    new_ideas, total = search_github_demand()
    print(f"Scan complete. Found {total} matches. Added {new_ideas} new ideas to registry.")
