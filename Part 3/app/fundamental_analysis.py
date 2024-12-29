import requests
from bs4 import BeautifulSoup
import pandas as pd
from textblob import TextBlob


def scrape_news():
    """
    Скрејпирање на вести од веб-сајтот https://seinet.com.mk/.
    """
    url = "https://seinet.com.mk/"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Грешка при преземање на вестите.")

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tbody tr")  # Проверете дали структурата е точна

    news = []
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 2:
            title = columns[1].text.strip()
            link = columns[1].a["href"] if columns[1].a else ""
            news.append({"Title": title, "Link": link})

    return pd.DataFrame(news)


def analyze_sentiment(news_df):
    """
    Анализа на сентимент за секоја вест во DataFrame.
    """
    def get_sentiment(text):
        analysis = TextBlob(text)
        return "Positive" if analysis.sentiment.polarity > 0 else "Negative"

    news_df["Sentiment"] = news_df["Title"].apply(get_sentiment)
    return news_df


def calculate_all_indicators(data):
    """
    Пресметај повеќе технички индикатори за даден DataFrame.
    """
    import pandas_ta as ta
    data["SMA"] = ta.sma(data["price"], length=5)
    data["EMA"] = ta.ema(data["price"], length=5)
    data["RSI"] = ta.rsi(data["price"], length=14)
    data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = ta.macd(data["price"])
    data["ADX"] = ta.adx(data["price"], data["price"], data["price"])["ADX_14"]
    return data


def get_fundamental_analysis():
    """
    Преземање вести и анализа на сентимент за фундаментална анализа.
    """
    try:
        news_df = scrape_news()
        news_with_sentiment = analyze_sentiment(news_df)
        return news_with_sentiment
    except Exception as e:
        print(f"Грешка при преземање или анализа на вестите: {e}")
        return pd.DataFrame(columns=["Title", "Link", "Sentiment"])
