import yfinance as yf
from datetime import datetime, timedelta

def fetch_stock_data(ticker, start_date, end_date, extra_days=30):
    # Convert string dates to datetime objects for extra input flexibility
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Calculate the adjusted start date for extra historical data
    adjusted_start = start_date - timedelta(days=extra_days)
    
    try:
        # Fetch the data
        data = yf.download(ticker, start=adjusted_start, end=end_date)
        
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker} in the specified date range.")
        
        return data
    except Exception as e:
        print(f"An error occurred while fetching data for {ticker}: {str(e)}")
        return None