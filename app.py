import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

BASE_URL = "https://www.yellowpages.com/search?search_terms=restaurants&geo_location_terms=New+York%2C+NY"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.yellowpages.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def scrape_businesses(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        businesses = soup.find_all("div", class_="info")

        business_data = []
        for business in businesses:
            name = business.find("a", class_="business-name")
            name = name.text.strip() if name else "N/A"
            address = business.find("div", class_="street-address")
            address = address.text.strip() if address else "N/A"
            phone = business.find("div", class_="phones")
            phone = phone.text.strip() if phone else "N/A"
            business_data.append({"name": name, "address": address, "phone": phone})
        return business_data if business_data else {"message": "No data found, but request succeeded"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    data = scrape_businesses(BASE_URL)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
