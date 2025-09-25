from fastapi import FastAPI
from app.main import app as scraper_app   # correct import
from agents.server import app as agent_app

app = FastAPI(title="Zeniks")

# Mount both apps
app.mount("/scraper", scraper_app)
app.mount("/agent", agent_app)

@app.get("/health")
def health():
    return {"status": "ok"}
