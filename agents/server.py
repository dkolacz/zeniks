from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from .graph import graph  # import your LangGraph workflow

app = FastAPI()

class ListingInput(BaseModel):
    listing_json: Dict[str, Any]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/optimize")
def optimize(input_data: ListingInput):
    result = graph.invoke({"listing_json": input_data.listing_json})
    return {"report": result.get("report", {})}
