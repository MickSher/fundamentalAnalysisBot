import time

# --- Import Custom Engines ---
from ingestion_engine import get_cik_from_ticker, get_latest_filing_url, extract_text_from_filing
from nlp_engine import analyze_sentiment_with_gemini
from technical_engine import get_hard_metrics

def decision_engine(ticker):
    print(f"\n--- Initiating Autonomous Analysis for {ticker} ---")
    
    # ==========================================
    # 1. INGESTION ENGINE (SEC Data)
    # ==========================================
    print(f"[{ticker}] Fetching SEC 10-K Data...")
    try:
        cik = get_cik_from_ticker(ticker)
        filing_url = get_latest_filing_url(cik, "10-K")
        if not filing_url:
            return "ERROR: Could not locate 10-K filing."
        
        full_text = extract_text_from_filing(filing_url)
        # Truncate text to fit within standard API limits 
        # (Increase this if using a paid tier)
        truncated_text = full_text[:60000] 
    except Exception as e:
        return f"ERROR in Data Ingestion: {e}"

    # ==========================================
    # 2. NLP ENGINE (Gemini Sentiment)
    # ==========================================
    print(f"[{ticker}] Running Gemini AI Sentiment Analysis on SEC Text...")
    ai_analysis = analyze_sentiment_with_gemini(truncated_text, ticker)
    print(f"   -> AI Says: {ai_analysis.get('sentiment', 'ERROR')} (Confidence: {ai_analysis.get('confidence_score', 0)})")
    print(f"   -> Reasoning: {ai_analysis.get('reasoning', 'No reasoning provided.')}")
    
    # ==========================================
    # 3. TECHNICAL ENGINE (yfinance Math)
    # ==========================================
    print(f"[{ticker}] Fetching Technicals & Valuation Metrics...")
    metrics = get_hard_metrics(ticker)
    time.sleep(1) # Polite delay for Yahoo APIs
    
    # ==========================================
    # 4. DECISION LOGIC & PARAMETERS
    # ==========================================
    print(f"[{ticker}] Weighing Parameters...")
    
    pe = metrics.get('forwardPE')
    margin = metrics.get('profitMargins')
    price = metrics.get('current_price')
    sma = metrics.get('sma_50')
    
    # Check A: Fundamental Valuation
    math_is_good = False
    if pe and margin:
        if pe < 30 and margin > 0.05:
            math_is_good = True
            
    # Check B: Technical Trend
    trend_is_good = False
    if price and sma:
        if price > sma:
            trend_is_good = True
            
    # Check C: NLP Sentiment
    sentiment = ai_analysis.get('sentiment')
    
    # Final Output Logic
    if sentiment == "POSITIVE" and math_is_good and trend_is_good:
        return "STRONG BUY - SEC text sentiment, fundamental valuation, and technical trend align."
    elif sentiment == "NEGATIVE" or not math_is_good:
        return "SELL / AVOID - High risk detected in SEC filings or poor valuation."
    else:
        return "HOLD - Mixed signals. Wait for a better setup."

# --- Execute the System ---
if __name__ == "__main__":
    target_stock = "AAPL"
    
    final_signal = decision_engine(target_stock)
    print(f"\n=====================================")
    print(f"FINAL DECISION FOR {target_stock}: \n{final_signal}")
    print(f"=====================================")