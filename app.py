from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

def scrape_google_maps(query):
    # Set up Chrome options for headless mode
    options = Options()
    options.add_argument("--headless")  # Run without opening a browser window
    options.add_argument("--no-sandbox")  # Required for Render's environment
    options.add_argument("--disable-dev-shm-usage")  # Avoids shared memory issues
    options.binary_location = "/usr/bin/google-chrome"  # Chrome binary location
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=options)
    
    try:
        # Navigate to Google Maps with the search query
        driver.get(f"https://www.google.com/maps/search/{query}")
        
        # Wait for business listings to load (up to 10 seconds)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))
        
        # Find all business listing elements
        businesses = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        business_data = []
        
        # Extract name and address from each listing
        for business in businesses:
            try:
                name = business.find_element(By.CLASS_NAME, "hfpxzc").text.strip()
            except:
                name = "N/A"
            try:
                address = business.find_element(By.CLASS_NAME, "Io6YTe").text.strip()
            except:
                address = "N/A"
            business_data.append({"name": name, "address": address})
        
        # Return results or a message if no data is found
        return business_data if business_data else {"message": "No businesses found"}
    
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        driver.quit()  # Always close the browser

@app.route('/scrape')
def scrape():
    # Get the query parameter from the URL
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    # Scrape data and return it as JSON
    data = scrape_google_maps(query)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
