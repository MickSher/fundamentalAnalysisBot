import google.generativeai as genai
import json

# 1. Configure the Gemini API (You get this key from Google AI Studio)
genai.configure(api_key="YOUR_GEMINI_API_KEY")

def analyze_sentiment_with_gemini(scraped_text, ticker):
    """
    Uses Gemini to analyze scraped news or earnings reports and returns 
    a structured JSON response that your code can easily read.
    """
    # Choose the model (Gemini 1.5 Flash is great for fast text processing)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # We instruct Gemini exactly how to behave and how to format its answer
    prompt = f"""
    You are an expert financial quantitative analyst. 
    Read the following recent news headlines/snippets regarding {ticker}.
    
    Determine the overall sentiment as it relates to the stock's short-term price action.
    Respond ONLY with a valid JSON object using this exact structure:
    {{
        "sentiment": "POSITIVE", "NEGATIVE", or "NEUTRAL",
        "confidence_score": a float between 0.0 and 1.0,
        "reasoning": "A brief one-sentence explanation."
    }}
    
    Here is the data to analyze:
    {scraped_text}
    """
    
    try:
        # Send the prompt to Gemini
        response = model.generate_content(prompt)
        
        # Clean the response to ensure it's pure JSON
        cleaned_response = response.text.replace('```json', '').replace('```', '').strip()
        
        # Parse the JSON string back into a Python dictionary
        analysis = json.loads(cleaned_response)
        return analysis
        
    except Exception as e:
        print(f"Error during Gemini analysis: {e}")
        return {"sentiment": "NEUTRAL", "confidence_score": 0.0, "reasoning": "Error processing."}

# --- Example Execution ---
apple_news = """
- Apple announces record-breaking iPhone 15 sales in Asia.
- Supply chain issues might slightly delay the new iPad release.
- Analysts upgrade AAPL stock to 'Strong Buy' citing service revenue growth.
"""

decision = analyze_sentiment_with_gemini(apple_news, "AAPL")

print(f"Sentiment: {decision['sentiment']}")
print(f"Confidence: {decision['confidence_score']}")
print(f"Why?: {decision['reasoning']}")