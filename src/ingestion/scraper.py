import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# URLs to scrape based on project scope
URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-short-term-opportunities-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-bse-sensex-index-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-liquid-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-nifty-smallcap-250-index-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-multi-asset-allocation-fund-direct-growth"
]

def scrape_fund_data(url):
    print(f"Scraping: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for Next.js data blob
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        if next_data_script:
            data = json.loads(next_data_script.string)
            # The structure in Groww usually involves props -> pageProps -> schemeData
            # We will save the whole JSON for the processor to handle
            return {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "raw_data": data,
                "status": "success"
            }
        
        return {"url": url, "status": "error", "message": "Could not find __NEXT_DATA__"}
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {"url": url, "status": "error", "message": str(e)}

def main():
    results = []
    for url in URLS:
        data = scrape_fund_data(url)
        results.append(data)
    
    # Save to data/raw
    os.makedirs("data/raw", exist_ok=True)
    filename = f"data/raw/scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    print(f"Scraping complete. Data saved to {filename}")

if __name__ == "__main__":
    main()
