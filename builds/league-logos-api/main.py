from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

app = FastAPI(title="League Logos API", description="An API for fetching league logos from Dota 2 matches.")

# Mock data to simulate league logos URLs. In a real-world scenario, this could be fetched from an external source.
league_logos = {
    "12345": {"name": "The International 2022", "logo_url": "https://example.com/ti2022.png"},
    "67890": {"name": "Dota 2 Major League", "logo_url": "https://example.com/major-league.png"}
}

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/league-logos/{league_id}", summary="Get league logo by ID")
async def get_league_logo(league_id: str):
    if league_id not in league_logos:
        raise HTTPException(status_code=404, detail=f"League with ID {league_id} not found.")
    
    return {"name": league_logos[league_id]["name"], "logo_url": league_logos[league_id]["logo_url"]}

# For running the server locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)