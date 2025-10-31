import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------
# CONFIGURATION
# ---------------------------
GOOGLE_NEWS_API_KEY = "YOUR_GOOGLE_NEWS_API_KEY"  # Replace with your API key
API_URL = "https://newsapi.org/v2/everything"

# List of F&O Stocks (You can add more)
FNO_STOCKS = [
    "Reliance Industries", "Tata Motors", "Infosys", "HDFC Bank", "ICICI Bank",
    "State Bank of India", "Tata Steel", "Larsen & Toubro", "Axis Bank",
    "Adani Enterprises", "Hindustan Unilever", "ITC", "Wipro", "Tech Mahindra",
    "Power Grid Corporation", "Coal India", "ONGC", "NTPC", "Bharti Airtel",
    "Bajaj Finance", "Asian Paints", "Tata Consultancy Services"
]

# ---------------------------
# FUNCTION TO FETCH NEWS
# ---------------------------
def fetch_news(query, from_date, to_date):
    """Fetch news for a given stock using Google News API"""
    params = {
        'q': query,
        'from': from_date,
        'to': to_date,
        'language': 'en',
        'sortBy': 'publishedAt',
        'apiKey': GOOGLE_NEWS_API_KEY,
        'pageSize': 5  # limit to 5 articles per stock
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    if data.get("status") == "ok":
        return data["articles"]
    return []

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="F&O Stocks News App", layout="wide")

st.title("📰 F&O Stocks News Dashboard (Past 1 Month)")
st.write("Get the latest news for all Futures & Options (F&O) listed stocks in India.")

# Date range for 1 month
to_date = datetime.today().date()
from_date = to_date - timedelta(days=30)

# Allow user to select specific stock
selected_stock = st.selectbox("Select Stock", ["All Stocks"] + FNO_STOCKS)

if st.button("Fetch News"):
    st.info(f"Fetching news from {from_date} to {to_date}...")

    if selected_stock == "All Stocks":
        for stock in FNO_STOCKS:
            st.subheader(f"📈 {stock}")
            articles = fetch_news(stock, from_date, to_date)
            if not articles:
                st.write("No news found.")
                continue
            for a in articles:
                st.markdown(f"**[{a['title']}]({a['url']})**")
                st.write(a['description'])
                st.caption(f"🗓 {a['publishedAt'][:10]} | 📰 {a['source']['name']}")
                st.write("---")
    else:
        st.subheader(f"📈 {selected_stock}")
        articles = fetch_news(selected_stock, from_date, to_date)
        if not articles:
            st.write("No news found.")
        for a in articles:
            st.markdown(f"**[{a['title']}]({a['url']})**")
            st.write(a['description'])
            st.caption(f"🗓 {a['publishedAt'][:10]} | 📰 {a['source']['name']}")
            st.write("---")

st.sidebar.header("About")
st.sidebar.write("""
This Streamlit app fetches financial news for Indian F&O stocks  
using the **Google News API** for the past 1 month.
""")


