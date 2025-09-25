from fastapi import FastAPI
from scraper.app.main import app as scraper_app
from agents.server import app as agent_app

app = FastAPI()

app.mount("/scraper", scraper_app)
app.mount("/agent", agent_app)
