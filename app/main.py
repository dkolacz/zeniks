from fastapi import FastAPI
from pydantic import BaseModel
from app.services.scraper import fetch_listing_all

app = FastAPI()

class ScrapeRequest(BaseModel):
    listing_id: str
    check_in: str = None
    check_out: str = None
    adults: int = 1
    currency: str = "USD"
    language: str = "en"

@app.post("/scrape")
def scrape_listing(req: ScrapeRequest):
    # build URL from listing_id
    url = f"https://www.airbnb.com/rooms/{req.listing_id}"

    result = fetch_listing_all(
        url,
        req.check_in or "2025-10-10",
        req.check_out or "2025-10-15",
        req.adults,
        req.currency,
        req.language
    )

    return {"listing_id": req.listing_id, "data": result}


