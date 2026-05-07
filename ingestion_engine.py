import requests
from bs4 import BeautifulSoup
import json
import re

# The SEC requires you to identify yourself. Replace with your actual name and email.
HEADERS = {
    ###"User-Agent": "YourName YourProject (your.email@university.edu)"
}

def get_cik_from_ticker(ticker):
    """Fetches the CIK number for a given ticker symbol."""
    print(f"Translating {ticker} to CIK...")
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception("Failed to fetch tickers from SEC.")
        
    tickers_data = response.json()
    
    # Search the JSON for our target ticker
    for key, company in tickers_data.items():
        if company['ticker'].upper() == ticker.upper():
            # SEC CIKs must be exactly 10 digits, padded with leading zeros
            return str(company['cik_str']).zfill(10)
            
    raise ValueError(f"Ticker {ticker} not found.")

def get_latest_filing_url(cik, filing_type="10-K"):
    """Finds the URL of the most recent 10-K or 10-Q filing."""
    print(f"Finding latest {filing_type} for CIK: {cik}...")
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception("Failed to fetch company submissions.")
        
    data = response.json()
    recent_filings = data['filings']['recent']
    
    # Loop through recent filings to find the first match for our type
    for i in range(len(recent_filings['form'])):
        if recent_filings['form'][i] == filing_type:
            accession_number = recent_filings['accessionNumber'][i]
            primary_document = recent_filings['primaryDocument'][i]
            
            # The SEC formats document URLs using the accession number without dashes
            accession_no_dashes = accession_number.replace("-", "")
            
            document_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primary_document}"
            return document_url
            
    return None

def extract_text_from_filing(url):
    """Downloads the HTML filing and extracts clean readable text."""
    print(f"Downloading and parsing filing from: {url}")
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception("Failed to download the document.")
        
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract text and remove excessive whitespace/newlines
    raw_text = soup.get_text(separator=' ')
    clean_text = re.sub(r'\s+', ' ', raw_text).strip()
    
    return clean_text

# --- Execute the Engine ---
if __name__ == "__main__":
    target_ticker = "AAPL"
    
    try:
        # Step 1: Get CIK
        cik = get_cik_from_ticker(target_ticker)
        
        # Step 2: Get URL for the latest Annual Report (10-K)
        filing_url = get_latest_filing_url(cik, "10-K")
        
        if filing_url:
            # Step 3: Extract the text
            filing_text = extract_text_from_filing(filing_url)
            
            print("\n--- Success! ---")
            print(f"Extracted {len(filing_text)} characters of fundamental data.")
            print("Preview of first 500 characters:\n")
            print(filing_text[:500])
            
            # Here is where you would pass `filing_text` to your Gemini sentiment engine:
            # decision = analyze_sentiment_with_gemini(filing_text, target_ticker)
            
        else:
            print("No 10-K found for this company.")
            
    except Exception as e:
        print(f"An error occurred: {e}")