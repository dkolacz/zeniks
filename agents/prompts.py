def analyzer_prompt(listing_context: str) -> str:
    return f"""
You are an expert Airbnb listing auditor.
You will receive the full listing JSON data as context.
Your task is to evaluate every aspect of the listing and produce a structured JSON audit.

Listing JSON:
{listing_context}

Follow this schema strictly:
{{
  "title": {{
    "score": int (0-10),
    "issues": [string],
    "recommendations": [string]
  }},
  "description": {{
    "score": int (0-10),
    "issues": [string],
    "recommendations": [string]
  }},
  "amenities": {{
    "score": int (0-10),
    "issues": [string],
    "recommendations": [string]
  }},
  "pricing": {{
    "score": int (0-10),
    "issues": [string],
    "recommendations": [string]
  }},
  "images": {{
    "score": int (0-10),
    "issues": [string],
    "recommendations": [string]
  }},
  "reviews": {{
    "score": int (0-10),
    "issues": [string],
    "recommendations": [string]
  }}
}}
"""


def improver_prompt(listing_context: str, analysis: dict) -> str:
    return f"""
You are an expert Airbnb listing optimizer.
You will receive the full listing JSON and the analysis results.
Based on both, propose improvements.

Listing JSON:
{listing_context}

Analysis:
{analysis}

Follow this schema strictly:
{{
  "new_title": "string",
  "new_description": "string",
  "amenities_suggestions": [string],
  "pricing_suggestions": [string],
  "image_suggestions": [string],
  "review_response_tips": [string]
}}
"""
