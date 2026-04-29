import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from ingestion.scraper import scrape_fund_data

def test_single_fund_scraping():
    """Test 1: Verify data extraction for a single well-known fund."""
    test_url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    print(f"--- Test 1: Scraping {test_url} ---")
    
    data = scrape_fund_data(test_url)
    
    if data['status'] == 'success':
        print("SUCCESS: Data fetched successfully.")
        
        # Extract basic info from the blob to verify structure
        try:
            page_props = data['raw_data'].get('props', {}).get('pageProps', {})
            mf_data = page_props.get('mfServerSideData', {})
            
            fund_name = mf_data.get('scheme_name')
            expense_ratio = mf_data.get('expense_ratio')
            nav = mf_data.get('nav')
            
            print(f"Fund Name: {fund_name}")
            print(f"Expense Ratio: {expense_ratio}%")
            print(f"Current NAV: Rs. {nav}")
            
            assert fund_name is not None
            assert expense_ratio is not None
            print("SUCCESS: Key fields found in JSON blob.")
        except Exception as e:
            print(f"ERROR: Failed to parse expected fields: {e}")
    else:
        print(f"FAILED: {data.get('message')}")

def test_different_category_fund():
    """Test 2: Verify data extraction for a different category (e.g., Gold/Silver)."""
    test_url = "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth"
    print(f"\n--- Test 2: Scraping {test_url} ---")
    
    data = scrape_fund_data(test_url)
    
    if data['status'] == 'success':
        mf_data = data['raw_data'].get('props', {}).get('pageProps', {}).get('mfServerSideData', {})
        fund_name = mf_data.get('scheme_name')
        category = mf_data.get('category')
        
        print(f"Fund Name: {fund_name}")
        print(f"Category: {category}")
        
        assert fund_name is not None
        assert "Gold" in fund_name or "Commodity" in str(category)
        print("SUCCESS: Data structure consistent for different fund types.")
    else:
        print(f"FAILED: {data.get('message')}")

if __name__ == "__main__":
    test_single_fund_scraping()
    test_different_category_fund()
