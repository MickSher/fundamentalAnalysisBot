# main.py

import time

# --- Import Custom Engines ---
# These assume you have defined these functions in their respective files
from ingestion_engine import scrape_recent_news, get_fundamental_data
from nlp_engine import analyze_sentiment
from technical_engine import get_technical_data

def decision_engine(ticker):
    """
    The core logic orchestrator. 
    Calls external modules to gather data, weighs parameters, and outputs a signal.
    """
    print(f"\n--- Initiating Autonomous Analysis for {ticker} ---")
    
    # 1. Gather Fundamental & Qualitative Data (Ingestion Engine)
    print(f"Gathering fundamental metrics and recent news...")
    fundamentals = get_fundamental_data(ticker)
    news_headlines = scrape_recent_news(ticker)
    
    # 2. Analyze Qualitative Data (NLP Engine)
    print(f"Running NLP sentiment analysis on recent news...")
    sentiment_score = analyze_sentiment(news_headlines)
    print(f" -> Sentiment Score: {sentiment_score:.2f}")
    
    # 3. Gather Technical Confirmation (Technical Engine)
    print(f"Checking technical trend indicators...")
    current_price, sma_50 = get_technical_data(ticker)
    
    # ==========================================
    # DECISION LOGIC & PARAMETERS
    # ==========================================
    
    # Parameter A: Fundamental Rules
    pe = fundamentals.get('forwardPE')
    margin = fundamentals.get('profitMargins')
    
    fundamentally_sound = False
    if pe is not None and margin is not None:
        if pe < 25 and margin > 0.10: # P/E under 25, Profit Margin over 10%
            fundamentally_sound = True

    # Parameter B: AI Sentiment Rules
    sentiment_positive = sentiment_score > 0.2 
    
    # Parameter C: Technical Rules
    technical_uptrend = False
    if current_price is not None and sma_50 is not None:
        technical_uptrend = current_price > sma_50
    
    # ==========================================
    # FINAL SIGNAL GENERATION
    # ==========================================
    print(f"\nWeighing parameters for {ticker}...")
    
    if fundamentally_sound and sentiment_positive and technical_uptrend:
        return "STRONG BUY - Fundamentals, sentiment, and trend align."
    
    elif not fundamentally_sound and sentiment_score < -0.2:
        return "SELL / AVOID - Poor fundamentals and negative sentiment."
    
    else:
        return "HOLD - Mixed signals detected. Awaiting better setup."

# --- Execute the System ---
if __name__ == "__main__":
    target_stock = "AAPL"
    
    try:
        final_signal = decision_engine(target_stock)
        print(f"\n=====================================")
        print(f"FINAL DECISION FOR {target_stock}: \n{final_signal}")
        print(f"=====================================")
        
    except Exception as e:
        print(f"System Failure: {e}")