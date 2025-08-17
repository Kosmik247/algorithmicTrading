import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time
from textblob import TextBlob

def fetch_gnews_headlines(api_key, query, start_date, end_date):
    
    all_headlines = []
    
    # GNews API requires a full datetime format for the time range
    time_from_iso = datetime.strptime(start_date, '%Y-%m-%d').isoformat() + 'Z'
    time_to_iso = datetime.strptime(end_date, '%Y-%m-%d').isoformat() + 'Z'

    url = 'https://gnews.io/api/v4/search'
    params = {
        'q': query,
        'from': time_from_iso,
        'to': time_to_iso,
        'token': api_key
    }
    
    page_size = 100
    params['max'] = page_size

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() 
        data = response.json()

        if 'articles' in data:
            for article in data['articles']:
                all_headlines.append({
                    'publishedAt': article['publishedAt'],
                    'title': article['title']
                })
        else:
            print(f"No articles found for {query} from {start_date} to {end_date}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GNews: {e}")
    
    df = pd.DataFrame(all_headlines)
    if not df.empty:
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        df.set_index('publishedAt', inplace=True)
    
    return df
def store_to_csv(df, filename):
    df.to_csv(filename)
    print(f"Data saved to {filename}")

def read_csv(filename):
    return pd.read_csv(filename, parse_dates=['publishedAt'], index_col='publishedAt')

def fetch_and_store_headlines(query, start_date, end_date):
    api_key = os.getenv("GNEWS_API_KEY")

    if not api_key:
        print("Error: GNEWS_API_KEY not found. Please check your .env file.")
    else:
        headlines_df = fetch_gnews_headlines(api_key, query, start_date, end_date)
        store_to_csv(headlines_df, f'{query}.csv')

def sentiment_analysis(TICKER_QUERY):
    df = read_csv(f'{TICKER_QUERY}.csv')
    if df.empty:
        print(f"No data found for {TICKER_QUERY}. Please check the CSV file.")
        return
    else:
        print(f"Data for {TICKER_QUERY} loaded successfully.")
    df['sentiment'] = df['title'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['sentiment_label'] = df['sentiment'].apply(lambda x: 'positive' if x > 0 else 'negative' if x < 0 else 'neutral')
    print(f"Sentiment analysis completed for {TICKER_QUERY}. Here are the results:")
    print(df[['title', 'sentiment', 'sentiment_label']].head(10))
    
    return df
def daily_sentiment(dataframe):
    if dataframe.empty:
        print("No data available for sentiment analysis.")
        return None
    
    daily_sentiment = dataframe.resample('D').mean()
    daily_sentiment['sentiment_label'] = daily_sentiment['sentiment'].apply(lambda x: 'positive' if x > 0 else 'negative' if x < 0 else 'neutral')
    print("Daily sentiment analysis completed.")
    print(daily_sentiment)
    return daily_sentiment
if __name__ == "__main__":
    load_dotenv()
    
    
    TICKER_QUERY = "NVDA stock"  
    START_DATE = '2024-01-01'
    END_DATE = '2024-04-30'

    if not os.path.exists(f'{TICKER_QUERY}.csv'):
        print(f"Fetching headlines for '{TICKER_QUERY}' from {START_DATE} to {END_DATE}...")
        fetch_and_store_headlines(TICKER_QUERY, START_DATE, END_DATE)
    else:
        print("Performing sentiment analysis...")
        sentiment_analysis(TICKER_QUERY)

    

    # headlines_df = read_csv(f'{TICKER_QUERY}.csv')
    
    # if not headlines_df.empty:
    #     print("\nSuccessfully fetched headlines. Here is a sample:")
    #     print(headlines_df)
    # else:
    #     print("No headlines found for the specified date range. Check your API key and query.")

