import time
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

app = Flask(__name__)

def scrape_google_maps(query):
    try:
        # Configure headless Chrome options
        options = Options()
        options.add_argument("--headless")  # Run without opening a browser window
        options.add_argument("--no-sandbox")  # Required for some hosting environments
        options.add_argument("--disable-dev-shm-usage")  # Avoids issues in containerized environments

        # Initialize the Chrome driver (assumes chromedriver is in PATH)
        driver = webdriver.Chrome(options=options)

        # Navigate to Google Maps with the search query
        driver.get(f"https://www.google.com/maps/search/{query}")

        # Wait for the page to load (adjust time as needed)
        time.sleep(5)

        # Find business listings (update selectors based on actual HTML)
        businesses = driver.find_elements(By.CLASS_NAME, "section-result")

        business_data = []
        for business in businesses:
            try:
                name = business.find_element(By.CLASS_NAME, "section-result-title").text.strip()
            except:
                name = "N/A"
            try:
                address = business.find_element(By.CLASS_NAME, "section-result-location").text.strip()
            except:
                address = "N/A"
            business_data.append({"name": name, "address": address})

        # Clean up
        driver.quit()

        # Return data or a message if no data is found
        return business_data if business_data else {"message": "No businesses found"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    # Example query; modify as needed
    query = "restaurants in New York"
    data = scrape_google_maps(query)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
