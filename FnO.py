"""
Streamlit app: F&O Stocks News (1m / 3m / 6m) using Google News via the `gnews` package.

Save as: fno_news_streamlit.py
Run:    streamlit run fno_news_streamlit.py
"""

import streamlit as st
from gnews import GNews
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser

# -----------------------
# Config / FnO stock list
# -----------------------
# You can expand this list or replace with a live NSE F&O list if needed.
FNO_STOCKS = [
    "Reliance Industries", "TCS", "Infosys", "HDFC Bank", "ICICI Bank",
    "Kotak Mahindra Bank", "State Bank of India", "Bharti Airtel",
    "Hindustan Unilever", "Axis Bank", "ITC", "Larsen & Toubro",
    "Wipro", "Bajaj Finance", "HCL Technologies", "ONGC", "NTPC",
    "Tata Steel", "Maruti Suzuki", "Tech Mahindra", "Adani Enterprises",
    "Tata Motors", "Power Grid Corporation", "IndusInd Bank",
    "UltraTech Cement", "Sun Pharma", "Grasim Industries", "JSW Steel",
    "BPCL", "Coal India", "Eicher Motors", "HDFC Life", "SBI Life",
    "Dr Reddy's Laboratories"
]

# --------------
# Helper methods
# --------------
def period_to_gnews_period(period_label: str) -> str:
    """Map human label to gnews 'period' string or return None to use dates."""
    mapping = {
        "1 Month": "1m",
        "3 Months": "3m",
        "6 Months": "6m"
    }
    return mapping.get(period_label, "1m")

@st.cache_data(show_spinner=False)
def fetch_news_for_stock(stock: str, period_label: str, max_results: int = 30):
    """
    Use GNews to fetch news for a stock for a period_label (1 Month / 3 Months / 6 Months)
    Returns a list of dicts with keys: title, url, published date, publisher, description
    """
    gnews_period = period_to_gnews_period(period_label)
    # Initialize GNews for India and English results
    google_news = GNews(language='en', country='IN', period=gnews_period, max_results=max_results)
    try:
        # query: include "stock" to bias results toward finance articles, but keep primary keyword
        query = f"{stock} stock"
        raw = google_news.get_news(query)

        results = []
        for item in raw:
            # item usually contains: title, url, published date, publisher, description
            # published date sometimes missing or in different formats; parse if possible
            published = item.get("published date") or item.get("published")
            # normalize published date to ISO if parseable
            try:
                if published:
                    parsed = parser.parse(published)
                    published_iso = parsed.isoformat()
                else:
                    published_iso = None
            except Exception:
                published_iso = published

            results.append({
                "stock": stock,
                "title": item.get("title"),
                "url": item.get("url"),
                "publisher": item.get("publisher"),
                "published": published_iso,
                "description": item.get("description")
            })
        return results

    except Exception as e:
        # Return an empty list but let caller know via a single-item error entry
        return [{"stock": stock, "title": f"ERROR: {e}", "url": "", "publisher": "", "published": "", "description": ""}]


# ----------------------
# Streamlit UI + control
# ----------------------
st.set_page_config(page_title="India F&O Stocks - Google News", layout="wide")
st.title("📰 F&O Stocks — Google News (1m / 3m / 6m)")

st.markdown(
    """
    This app searches Google News (via the `gnews` package) for news about Indian F&O stocks.
    Select a time window (1, 3 or 6 months), choose stocks, and click **Fetch News**.
    """
)

# choose period
period = st.radio("Select period", options=["1 Month", "3 Months", "6 Months"], index=0)

# date hint (computed from today)
today = datetime.utcnow().date()
period_days = {"1 Month": 30, "3 Months": 90, "6 Months": 180}[period]
start_date_hint = today - timedelta(days=period_days)
st.caption(f"Searching Google News results roughly between {start_date_hint} and {today} (GNews 'period' used).")

# stock selection (multiselect)
selected = st.multiselect("Select F&O Stocks to fetch news for", options=FNO_STOCKS, default=FNO_STOCKS[:6])

# results controls
max_results = st.number_input("Max results per stock (gnews max_results)", min_value=5, max_value=100, value=30, step=5)

if st.button("Fetch News"):
    if not selected:
        st.warning("Please select at least one stock.")
    else:
        placeholder = st.empty()
        progress_bar = st.progress(0)
        all_results = []
        total = len(selected)
        for idx, stock in enumerate(selected):
            placeholder.info(f"Fetching news for: {stock}  ({idx+1}/{total})")
            items = fetch_news_for_stock(stock, period, max_results=int(max_results))
            # extend results
            all_results.extend(items)
            progress_bar.progress(int(((idx + 1) / total) * 100))

        progress_bar.empty()
        placeholder.empty()

        # Build DataFrame, drop possible duplicates by URL/title
        df = pd.DataFrame(all_results)
        if df.empty:
            st.info("No news found for the selected stocks/time range.")
        else:
            # drop rows that are clearly error placeholders (optional)
            df = df[~df["title"].str.startswith("ERROR:", na=False)]
            # de-duplicate by url if present else by title
            if "url" in df.columns and df["url"].notnull().any():
                df = df.drop_duplicates(subset=["url"], keep="first")
            else:
                df = df.drop_duplicates(subset=["title"], keep="first")

            # sort by published date (newest first) where possible
            try:
                df["published_parsed"] = pd.to_datetime(df["published"], utc=True, errors="coerce")
                df = df.sort_values(by="published_parsed", ascending=False).drop(columns=["published_parsed"])
            except Exception:
                pass

            # show table
            st.write(f"### Found {len(df)} unique articles")
            st.dataframe(df[["stock", "title", "publisher", "published", "url", "description"]].reset_index(drop=True), use_container_width=True)

            # CSV download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", data=csv, file_name="fno_news.csv", mime="text/csv")


# Footer / notes
st.markdown(
    """
    ---
    **Notes**
    - This app uses the `gnews` package to query Google News RSS. Google does not provide a free official public "Google News API". 
    - `gnews` scrapes RSS results and may occasionally be rate-limited or return fewer results than a commercial API.
    - If you want more robust commercial-grade news coverage, consider `newsapi.org`, `serpapi.com` (Google News engine), or a paid GNews API service.
    """
)
