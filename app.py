from flask import Flask, request, jsonify
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/search-businesses', methods=['GET'])
def api_search_businesses():
    """
    Searches Google Maps for businesses based on a query and location.
    """
    query = request.args.get('query')
    location = request.args.get('location')

    if not query:
        return jsonify({"error": "Missing 'query' parameter. Please provide a search term (e.g., 'restaurants')."}), 400

    search_queries = [query] # Google Maps API expects a list of queries
    location_bias = location if location else "Sialkot, Punjab, Pakistan" # Default location if not provided

    try:
        logging.info(f"Searching Google Maps for '{query}' in '{location_bias}'")
        places_result = Google Maps( # Corrected function name to Google Maps
            query=search_queries,
            location_bias=location_bias
        )

        if isinstance(places_result, str): # Handle error string response
            logging.error(f"Google Maps API error: {places_result}")
            return jsonify({"error": "Google Maps API Error", "details": places_result}), 500

        if places_result and places_result.places:
            businesses_data = []
            for place in places_result.places:
                business_info = {
                    "name": place.name,
                    "address": place.address,
                    "map_url": place.map_url,
                    "website": place.url,
                    "rating": place.rating,
                    "user_rating_count": place.user_rating_count,
                    "description": place.description
                    # Add other relevant fields from the Place object if needed (e.g., phone_number, opening_hours)
                }
                businesses_data.append(business_info)
            logging.info(f"Found {len(businesses_data)} businesses for query '{query}'")
            return jsonify({"query": query, "location": location_bias, "businesses": businesses_data})
        else:
            logging.info(f"No businesses found for query '{query}' in '{location_bias}'")
            return jsonify({"query": query, "location": location_bias, "businesses": [], "message": "No businesses found matching your query."})


    except Exception as e:
        logging.error(f"API Error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Google Maps Business Scraper API is running.",
        "endpoints": [
            "/search-businesses?query=<search_term>&location=<optional_location> (search for businesses on Google Maps)"
        ]
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
