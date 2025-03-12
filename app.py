from flask import Flask, request, jsonify
import os
import logging
import requests
from bs4 import BeautifulSoup
import re  # For email extraction (if you want to try to scrape emails from business websites)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_Google Maps_no_api_key(query, location=""):
    """
    Attempts to scrape Google Maps business data without using an API key.
    This is unreliable and may break. Use with caution and respect Google's terms of service.
    """
    base_url = "https://www.google.com/maps/search/"
    search_query = f"{query} in {location}" if location else query
    search_url = base_url + search_query.replace(" ", "+")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' # Mimic a browser
    }

    try:
        logging.info(f"Fetching Google Maps search results page: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=10) # Increased timeout, added headers
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')

        businesses = []
        # **IMPORTANT: This is a VERY basic and brittle parsing example.**
        # Google Maps HTML structure is complex and changes frequently.
        # This parsing logic is likely to break and needs to be adapted
        # based on the current Google Maps HTML.

        business_elements = soup.find_all('div', class_='V67aGc') # Example class - INSPECT Google Maps HTML in browser!

        if not business_elements:
            logging.info("No business elements found with current parsing logic. Google Maps HTML might have changed.")
            return businesses # Return empty list if no businesses found with current logic

        for element in business_elements:
            name_element = element.find('div', class_='fontHeadlineSmall') # Example class - INSPECT Google Maps HTML
            address_element = element.find('div', class_='W4Efsd') # Example class - INSPECT Google Maps HTML
            rating_element = element.find('span', class_='MW4rle') # Example class - INSPECT Google Maps HTML
            review_count_element = element.find('span', class_='UY7Too') # Example class - INSPECT Google Maps HTML
            website_link_element = element.find('a', class_='app-view-link') # Example class - INSPECT Google Maps HTML


            business_name = name_element.text.strip() if name_element else "N/A"
            business_address = address_element.text.strip() if address_element else "N/A"
            business_rating = rating_element.text.strip() if rating_element else "N/A"
            business_review_count_str = review_count_element.text.strip().strip('()') if review_count_element else "0" # Remove parentheses
            business_review_count = int(business_review_count_str) if business_review_count_str.isdigit() else 0
            business_website = website_link_element['href'] if website_link_element and 'href' in website_link_element.attrs else "N/A"


            business_data = {
                "name": business_name,
                "address": business_address,
                "rating": business_rating,
                "review_count": business_review_count,
                "website": business_website
            }
            businesses.append(business_data)

        return businesses

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return [] # Return empty list in case of request errors
    except Exception as e:
        logging.error(f"Scraping error: {e}")
        return [] # Return empty list in case of parsing or other errors


@app.route('/scrape-businesses-no-api-key', methods=['GET'])
def api_scrape_businesses_no_api_key():
    """
    Endpoint to scrape Google Maps businesses without API key (UNRELIABLE).
    """
    query = request.args.get('query')
    location = request.args.get('location')

    if not query:
        return jsonify({"error": "Missing 'query' parameter. Please provide a search term (e.g., 'restaurants')."}), 400

    logging.info(f"Endpoint '/scrape-businesses-no-api-key' called with query='{query}', location='{location}'")
    businesses_data = scrape_Google Maps_no_api_key(query, location)

    return jsonify({
        "query": query,
        "location": location,
        "businesses": businesses_data,
        "disclaimer": "This API endpoint scrapes Google Maps without using an official API key. It is unreliable, may break at any time, and might violate Google's Terms of Service. Use with extreme caution and for ethical purposes only."
    })


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Google Maps Business Scraper API (No API Key - Unreliable) is running.",
        "endpoints": [
            "/scrape-businesses-no-api-key?query=<search_term>&location=<optional_location> (scrape Google Maps businesses - unreliable)"
        ],
        "warning": "The '/scrape-businesses-no-api-key' endpoint is unreliable and might break. Consider using the official Google Maps Places API for production use (which requires an API key and billing).",
        "ethical_note": "Use this API responsibly and ethically. Respect website terms of service and robots.txt if you attempt to scrape further data from business websites."
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
