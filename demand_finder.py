import os
import json
import requests
from datetime import datetime

REGISTRY_PATH = "registry.json"

# Broadened queries with chronological constraints to ensure we always capture data without getting blocked
GITHUB_QUERIES = [
    '"is there an api for"',
    '"looking for an api"',
    '"need an api for"'
]

SYSTEM_BLACKLIST = [
    "uart", "dma", "usb", "addon", "extension", "plugin", "driver", 
    "key request", "access request", "hardware", "register", "matrix",
    "jenkins", "vert.x", "database encryption", "sparse", "mod pack",
    "forgot password", "login", "logout", "auth token", "credential",
    "about:addons", "classnames", "overrides", "private api"
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

def should_exclude(title: str, body: str) -> bool:
    """Evaluates text strings against the noise blacklist to protect pipeline integrity."""
    combined_text = f"{title.lower()} {body.lower()}"
    return any(word in combined_text for word in SYSTEM_BLACKLIST)

def search_github_demand():
    """Scrapes GitHub Issues for active API market gaps from 2025 onward."""
    headers = {
        "User-Agent": "APIFactoryFinder/2.5",
        "Accept": "application/vnd.github+json"
    }
    
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    found_ideas = []
    date_cutoff = "created:>2025-01-01"
    
    for query in GITHUB_QUERIES:
        # We query the entire issue but sort strictly by newest first to ensure fresh data coverage
        url = f"https://api.github.com/search/issues?q={query}+{date_cutoff}+state:open+type:issue&sort=created&order=desc"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 403:
                print("⚠ GitHub Search API hit rate-limiting (403). Consider adding a GITHUB_TOKEN.")
                continue
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
                
                if "pull_request" in item:
                    continue
                
                if should_exclude(title, body):
                    continue
                
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
        except Exception as e:
            print(f"Error executing GitHub query [{query}]: {e}")
            pass
            
    registry = load_registry()
    existing_ids = {idea["id"] for idea in registry.get("ideas", []) if "id" in idea}
    
    new_count = 0
    for idea in found_ideas:
        if idea["id"] not in existing_ids:
            registry["ideas"].append(idea)
            new_count += 1
            
    save_registry(registry)
    return new_count, len(found_ideas)

def _execute_reddit_scan_internal():
    """Internal helper to execute the masked session-based Reddit crawl layer."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "python:research-utility-project:v2.5 (by /u/marian_dev_stream)",
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    })
    
    query = '("is there an api for" OR "looking for an api" OR "need an api for")'
    url = f"https://www.reddit.com/search.json?q={query}&sort=new&limit=50"
    
    found_ideas = []
    try:
        response = session.get(url, timeout=15)
        if response.status_code != 200:
            print(f"⚠ Reddit Search API returned status code {response.status_code}")
            return 0, 0
            
        data = response.json()
        posts = data.get("data", {}).get("children", [])
        
        for post in posts:
            post_data = post.get("data", {})
            title = post_data.get("title", "")
            body = post_data.get("selftext", "") or ""
            permalink = post_data.get("permalink", "")
            created_utc = post_data.get("created_utc", 0)
            post_id = post_data.get("id", "")
            
            if created_utc < 1735689600:  # Cutoff Jan 1, 2025
                continue
                
            if should_exclude(title, body):
                continue
                
            desc = body[:500] + ("..." if len(body) > 500 else "")
            
            found_ideas.append({
                "id": f"rd_{post_id}",
                "title": title,
                "description": desc,
                "source": "Reddit",
                "url": f"https://www.reddit.com{permalink}",
                "timestamp": datetime.fromtimestamp(created_utc).isoformat(),
                "status": "pending"
            })
    except Exception as e:
        print(f"Error executing Reddit search: {e}")
        return 0, 0

    registry = load_registry()
    existing_ids = {idea["id"] for idea in registry.get("ideas", []) if "id" in idea}
    
    new_count = 0
    for idea in found_ideas:
        if idea["id"] not in existing_ids:
            registry["ideas"].append(idea)
            new_count += 1
            
    save_registry(registry)
    return new_count, len(found_ideas)

# MASTER WRAPPER FUNCTION CALLED BY FACTORY_UI.PY
def search_reddit_demand():
    """Intercepts the dashboard call to execute both engine sweeps sequentially."""
    print("\nExecuting Hardened GitHub Crawler Sweep...")
    gh_new, gh_total = search_github_demand()
    print(f"→ GitHub Results: Matches Found: {gh_total} | Saved to Registry: {gh_new}")
    
    print("\nExecuting Session-Masked Reddit Crawler Sweep...")
    rd_new, rd_total = _execute_reddit_scan_internal()
    print(f"→ Reddit Results: Matches Found: {rd_total} | Saved to Registry: {rd_new}")
    
    combined_new = gh_new + rd_new
    combined_total = gh_total + rd_total
    return combined_new, combined_total

if __name__ == "__main__":
    print("⚡ Manual Test Initialization... ⚡")
    search_reddit_demand()