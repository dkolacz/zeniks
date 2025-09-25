from fastapi import FastAPI
#from scraper.app.main import app as scraper_app
from app.main import app as scraper_app
from agents.server import app as agent_app

app = FastAPI(title="Zeniks")

# Include scraper routes
for route in scraper_app.routes:
    app.router.routes.append(route)

# Include agent routes
for route in agent_app.routes:
    app.router.routes.append(route)

@app.get("/health")
def health():
    return {"status": "ok"}