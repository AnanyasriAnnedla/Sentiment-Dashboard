# Trend Sentinel

A real-time sentiment dashboard for marketers to track public opinion 
around any brand or topic — and decide if a trend is worth riding.

## Live Demo
👉 [Try it here](sentiment-dashboard-an.streamlit.app)

## What it does
- Search any brand or topic (e.g. "Nike", "ChatGPT", "Zomato")
- Fetches live news headlines + YouTube comments
- Runs sentiment analysis on both sources
- Gives a Green / Yellow / Red verdict for marketers
- Shows a Google Trends graph for the last 7 days

## Why it's useful
Marketers use trend-jacking to associate their brand with viral moments.
This tool tells you if the sentiment around a trend is safe enough to 
jump on — before your competitors do.

## Tech Stack
Python · Streamlit · NewsAPI · YouTube Data API v3 · VADER · Plotly · pytrends

## Known Limitations
- Google Trends data is occasionally unavailable due to pytrends 
  rate limiting by Google.
- VADER is optimized for English — non-English comments may be 
  misclassified.
- NewsAPI free tier is limited to 100 requests/day.

## How to Run
1. Clone the repository
   git clone https://github.com/AnanyasriAnnedla/SentimentDashboard

2. Install dependencies
   pip install -r requirements.txt

3. Create a .env file with your API keys
   NEWSAPI_KEY=your_key
   YOUTUBE_API_KEY=your_key

4. Run the app
   streamlit run app.py