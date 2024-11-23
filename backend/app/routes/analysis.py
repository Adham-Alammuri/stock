from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.services.data_fetcher import fetch_stock_data
from app.services.data_analyzer import StockAnalyzer

router = APIRouter(
    prefix="/api/analysis",
    tags=["analysis"]
)

def clean_data_for_json(data):
    """Convert pandas objects to JSON-serializable format, handling NaN values"""
    if isinstance(data, pd.Series):
        return data.replace([np.inf, -np.inf, np.nan], None).to_dict()
    elif isinstance(data, pd.DataFrame):
        return data.replace([np.inf, -np.inf, np.nan], None).to_dict()
    return data

@router.get("/{ticker}")
async def get_stock_analysis(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    try:
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        original_start = pd.to_datetime(start_date)
        
        data = fetch_stock_data(ticker, start_date, end_date, extra_days=365)
        
        if data is None:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker {ticker}"
            )
            
        analyzer = StockAnalyzer(data)
        
        sma = analyzer.calculate_sma(20)
        rsi = analyzer.calculate_rsi()
        bollinger = analyzer.calculate_bollinger_bands()
        
        _, volatility = analyzer.calculate_volatility(window=252)
        
        # Trim data to match requested time period
        sma = sma[sma.index >= original_start]
        rsi = rsi[rsi.index >= original_start]
        bollinger = bollinger[bollinger.index >= original_start]
        volatility = volatility[volatility.index >= original_start]
        
        return {
            "success": True,
            "data": {
                "sma": clean_data_for_json(sma),
                "rsi": clean_data_for_json(rsi),
                "bollinger": clean_data_for_json(bollinger),
                "volatility": clean_data_for_json(volatility)
            }
        }
        
    except Exception as e:
        print(f"Error details: {str(e)}")  
        raise HTTPException(status_code=500, detail=str(e))