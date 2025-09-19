from fastapi import FastAPI
from app.services.scraper import fetch_listing_all
from app.db.supabase import supabase
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime

app = FastAPI()

# --- Dynamic defaults for check-in/out ---
def default_check_in() -> str:
    return (date.today() + timedelta(days=2)).isoformat()

def default_check_out() -> str:
    return (date.today() + timedelta(days=5)).isoformat()

# --- Request body ---
class ScrapeRequest(BaseModel):
    listing_id: str
    check_in: str = Field(default_factory=default_check_in)
    check_out: str = Field(default_factory=default_check_out)
    adults: int = 1
    currency: str = "USD"
    language: str = "en"

# --- Endpoint ---
@app.post("/scrape")
def scrape_listing(req: ScrapeRequest):
    room_url = f"https://www.airbnb.com/rooms/{req.listing_id}"

    # Step 1: ensure record exists with created_at (user request time)
    supabase.table("results").upsert({
        "listing_id": req.listing_id,
        "url": room_url,
        "created_at": datetime.utcnow().isoformat()
    }, on_conflict="listing_id").execute()

    # Step 2: run scraper
    result = fetch_listing_all(
        room_url, req.check_in, req.check_out,
        req.adults, req.currency, req.language
    )

    # Step 3: update with scraped data + inserted_at
    supabase.table("results").update({
        "data": result,
        "inserted_at": datetime.utcnow().isoformat()
    }).eq("listing_id", req.listing_id).execute()

    return result

