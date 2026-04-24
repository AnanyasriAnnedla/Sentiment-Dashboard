import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px
import pandas as pd
from pytrends.request import TrendReq
from dotenv import load_dotenv
import os
import html

load_dotenv()
NEWS_API_KEY = st.secrets.get("NEWSAPI_KEY") or os.getenv("NEWSAPI_KEY")
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY") or os.getenv("YOUTUBE_API_KEY")

analyzer = SentimentIntensityAnalyzer()

def get_news(topic):
    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize=30&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get("articles", [])
    return [a["title"] for a in articles if a["title"]]

def get_youtube_comments(topic):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "snippet",
        "q": topic,
        "type": "video",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY
    }
    search_response = requests.get(search_url, params=search_params).json()
    video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

    comments = []
    for video_id in video_ids:
        comments_url = "https://www.googleapis.com/youtube/v3/commentThreads"
        comments_params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": 20,
            "key": YOUTUBE_API_KEY
        }
        comments_response = requests.get(comments_url, params=comments_params).json()
        for item in comments_response.get("items", []):
            comment = html.unescape(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
            comments.append(comment)

    return comments

def analyze_sentiment(texts, source):
    results = []
    for text in texts:
        score = analyzer.polarity_scores(text)["compound"]
        if score >= 0.05:
            label = "Positive"
        elif score <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"
        results.append({"text": text, "score": score, "sentiment": label, "source": source})
    return pd.DataFrame(results)

def get_trends(topic):
    try:
        pytrends = TrendReq()
        pytrends.build_payload([topic], timeframe="now 7-d")
        data = pytrends.interest_over_time()
        if not data.empty:
            return data[topic].reset_index()
    except:
        return None

st.set_page_config(page_title="Trend Sentinel", layout="wide")
st.title("😎Trend Sentinel")
st.markdown("*Is this trend worth riding? Find out before your competitors do.*")

topic = st.text_input("Enter a brand or topic", placeholder="e.g. Nike, ChatGPT, Zomato")

if topic:
    with st.spinner("🥱Fetching data..."):
        headlines = get_news(topic)
        comments = get_youtube_comments(topic)

        news_df = analyze_sentiment(headlines, "News")
        youtube_df = analyze_sentiment(comments, "YouTube")
        df = pd.concat([news_df, youtube_df], ignore_index=True)

    if df.empty:
        st.warning("No data found for this topic. Try a different keyword.")
    else:
        st.markdown("---")

        # Overall verdict based on combined sentiment
        positive_pct = (df["sentiment"] == "Positive").sum() / len(df) * 100
        negative_pct = (df["sentiment"] == "Negative").sum() / len(df) * 100

        if positive_pct >= 50:
            st.success(f"🟢 **Green Light** — {positive_pct:.0f}% positive sentiment. Good time to associate your brand with this trend.")
        elif negative_pct >= 50:
            st.error(f"🔴 **Red Light** — {negative_pct:.0f}% negative sentiment. Risky to jump on this trend right now.")
        else:
            st.warning(f"🟡 **Yellow Light** — Mixed sentiment. Proceed with caution.")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📰 News Sentiment")
            news_counts = news_df["sentiment"].value_counts().reset_index()
            news_counts.columns = ["Sentiment", "Count"]
            fig1 = px.pie(news_counts, names="Sentiment", values="Count",
                         color="Sentiment",
                         color_discrete_map={"Positive": "#2ecc71", "Neutral": "#f39c12", "Negative": "#e74c3c"})
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("🎥 YouTube Public Opinion")
            yt_counts = youtube_df["sentiment"].value_counts().reset_index()
            yt_counts.columns = ["Sentiment", "Count"]
            fig2 = px.pie(yt_counts, names="Sentiment", values="Count",
                         color="Sentiment",
                         color_discrete_map={"Positive": "#2ecc71", "Neutral": "#f39c12", "Negative": "#e74c3c"})
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        st.subheader("📈 Google Trends (Last 7 Days)")
        trends_df = get_trends(topic)
        if trends_df is not None:
            fig3 = px.line(trends_df, x="date", y=topic, labels={topic: "Search Interest"})
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("😅Trends data unavailable for this topic.")

        st.markdown("---")

        st.subheader("Raw Data")
        source_filter = st.radio("Filter by source", ["All", "News", "YouTube"], horizontal=True)
        if source_filter != "All":
            filtered_df = df[df["source"] == source_filter]
        else:
            filtered_df = df

        st.dataframe(filtered_df[["source", "text", "sentiment", "score"]].rename(columns={
            "source": "Source", "text": "Text", "sentiment": "Sentiment", "score": "Score"
        }), use_container_width=True)