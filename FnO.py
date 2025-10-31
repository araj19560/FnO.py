import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# =====================
# CONFIGURATION SECTION
# =====================
API_KEY = "YOUR_GOOGLE_API_KEY"
CSE_ID = "YOUR_CUSTOM_SEARCH_ENGINE_ID"

# List of major FnO stocks (you can expand or fetch dynamically)
FNO_STOCKS = [
    "Reliance Industries", "TCS", "Infosys", "HDFC Bank", "ICICI Bank", "Kotak Mahindra Bank",
    "State Bank of India", "Bharti Airtel", "Hindustan Unilever", "Axis Bank", "ITC",
    "Larsen & Toubro", "Wipro", "Bajaj Finance", "HCL Technologies", "ONGC", "NTPC", "Tata Steel",
    "Maruti Suzuki", "Tech Mahindra", "Adani Enterprises", "Tata Motors", "Power Grid Corporation",
    "IndusInd Bank", "UltraTech Cement", "Sun Pharma", "Grasim Industries", "JSW Steel",
    "BPCL", "Coal India", "Eicher Motors", "HDFC Life", "SBI Life", "Dr Reddy’s Labs"
]

# =====================
# FUNCTION TO GET NEWS
# =====================
def get_news(stock, start_date, end_date):
    """Fetches news for a stock from Google Custom Search API."""
    query = f"{stock} stock news site:moneycontrol.com OR site:economictimes.indiatimes.com OR site:business-standard.com"
    url = (
        f"https://www.googleapis.com/customsearch/v1?"
        f"key={API_KEY}&cx={CSE_ID}&q={query}&sort=date"
    )

    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        news_items = []
        if "items" in data:
            for item in data["items"]:
                news_items.append({
                    "Stock": stock,
                    "Title": item.get("title"),
                    "Link": item.get("link"),
                    "Snippet": item.get("snippet")
                })
        return news_items
    except Exception as e:
        st.warning(f"Error fetching news for {stock}: {e}")
        return []

# =====================
# STREAMLIT UI
# =====================
st.set_page_config(page_title="F&O Stocks News App", layout="wide")
st.title("📈 F&O Stocks News Aggregator (India)")

# Date range options
period = st.radio("Select Period", ["1 Month", "3 Months", "6 Months"])
period_days = {"1 Month": 30, "3 Months": 90, "6 Months": 180}[period]

end_date = datetime.today()
start_date = end_date - timedelta(days=period_days)

st.markdown(f"### Showing News from **{start_date.date()}** to **{end_date.date()}**")

selected_stocks = st.multiselect("Select F&O Stocks", FNO_STOCKS, default=FNO_STOCKS[:5])

if st.button("Fetch News"):
    all_news = []
    progress = st.progress(0)
    
    for i, stock in enumerate(selected_stocks):
        news = get_news(stock, start_date, end_date)
        all_news.extend(news)
        progress.progress((i+1)/len(selected_stocks))
    
    if all_news:
        df = pd.DataFrame(all_news)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download as CSV", csv, "fno_stock_news.csv", "text/csv")
    else:
        st.info("No news found for the selected stocks and time period.")
