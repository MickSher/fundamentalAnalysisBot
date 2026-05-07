import yfinance as yf
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import pandas as pd

# 1. Initialize the NLP Sentiment AI (Using a pre-trained FinBERT model designed for finance)
# Note: In a real environment, you might use OpenAI's API for deeper reasoning.
sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def get_fundamental_data(ticker_symbol):
    """Fetches key fundamental metrics using Yahoo Finance API."""
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    fundamentals = {
        'forwardPE': info.get('forwardPE', None),
        'priceToBook': info.get('priceToBook', None),
        'debtToEquity': info.get('debtToEquity', None),
        'profitMargins': info.get('profitMargins', None)
    }
    return fundamentals

def scrape_recent_news(ticker_symbol):
    """
    Crawls Google News for recent headlines. 
    (Note: For production, use a dedicated news API like NewsAPI or Alpaca to avoid being IP-blocked).
    """
    url = f"https://news.google.com/search?q={ticker_symbol}+stock"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract headlines (class names change frequently on Google News, this is conceptual)
    headlines = [h3.text for h3 in soup.find_all('h3')][:5] 
    return headlines

def analyze_sentiment(headlines):
    """Runs the AI sentiment model on scraped headlines."""
    if not headlines:
        return 0
        
    results = sentiment_analyzer(headlines)
    score = 0
    
    for result in results:
        if result['label'] == 'positive':
            score += 1
        elif result['label'] == 'negative':
            score -= 1
            
    # Return an average sentiment score between -1 and 1
    return score / len(headlines)

def get_technical_data(ticker_symbol):
    """Calculates a simple 50-day moving average for technical confirmation."""
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period="3mo")
    current_price = hist['Close'].iloc[-1]
    sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
    
    return current_price, sma_50

def decision_engine(ticker):
    """The core logic combining fundamentals, AI sentiment, and technicals."""
    print(f"--- Analyzing {ticker} ---")
    
    # Gather Data
    fundamentals = get_fundamental_data(ticker)
    news = scrape_recent_news(ticker)
    sentiment_score = analyze_sentiment(news)
    current_price, sma_50 = get_technical_data(ticker)
    
    # 1. Fundamental Rules (Example logic: Low P/E, Good Margins)
    pe = fundamentals['forwardPE']
    margin = fundamentals['profitMargins']
    
    fundamentally_sound = False
    if pe and margin:
        if pe < 25 and margin > 0.10: # P/E under 25, Profit Margin over 10%
            fundamentally_sound = True

    # 2. AI Sentiment Rules
    sentiment_positive = sentiment_score > 0.2 
    
    # 3. Technical Rules (Is it trading above its 50-day average?)
    technical_uptrend = current_price > sma_50
    
    # Final Decision Tree
    if fundamentally_sound and sentiment_positive and technical_uptrend:
        return "STRONG BUY"
    elif not fundamentally_sound and sentiment_score < -0.2:
        return "SELL"
    else:
        return "HOLD"

# --- Execute the AI ---
target_stock = "AAPL"
signal = decision_engine(target_stock)
print(f"Final Signal for {target_stock}: {signal}")