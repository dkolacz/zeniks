import pyairbnb
from pyairbnb import details, price

def fetch_listing_all(room_url: str, check_in: str, check_out: str,
                      adults: int = 1, currency: str = "USD", language: str = "en",
                      proxy_url: str = "") -> dict:
    """
    Fetch listing details, reviews, and price from Airbnb using pyairbnb.
    """

    # Reviews
    reviews_data = pyairbnb.get_reviews(room_url, language, proxy_url)

    # Details
    data_formatted, price_input, cookies = details.get(room_url, language, proxy_url)

    # Extract required keys for pricing
    product_id = price_input["product_id"]
    api_key = price_input["api_key"]
    impression_id = price_input["impression_id"]

    # Price
    price_data = price.get(
        api_key, cookies, impression_id, product_id,
        check_in, check_out, adults, currency, language, proxy_url
    )

    return {
        "listing_id": product_id,
        "details": data_formatted,
        "reviews": reviews_data,
        "price": price_data
    }
