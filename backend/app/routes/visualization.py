from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import pandas as pd
from app.services.data_fetcher import fetch_stock_data
from app.services.data_analyzer import StockAnalyzer
from app.services.visualizer import StockVisualizer

class ChartResponse(BaseModel):
    success: bool
    data: dict

router = APIRouter()

@router.get("/{ticker}/chart", response_model=ChartResponse)
async def get_chart_data(
    ticker: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    chart_type: Optional[str] = Query("candlestick", description="Chart type (candlestick or technical)"),
    indicators: Optional[List[str]] = Query(
        default=['sma', 'bb', 'rsi'],
        description="Technical indicators (sma, bb, rsi)"
    )
):
    """Get chart data with technical indicators"""
    try:
        # Handle dates
        if not end_date:
            end_dt = datetime.now()
        else:
            end_dt = pd.to_datetime(end_date)
        if not start_date:
            start_dt = end_dt - timedelta(days=30)
        else:
            start_dt = pd.to_datetime(start_date)
            
        # Get extra data for calculations (50 days before requested start)
        calc_start = start_dt - timedelta(days=50)
        data = fetch_stock_data(ticker, calc_start, end_dt)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
            
        # Process data with full range for calculations
        analyzer = StockAnalyzer(data)
        visualizer = StockVisualizer(analyzer)
        
        # Get data with indicators calculated
        if chart_type == "technical":
            chart_data = visualizer.prepare_technical_data(indicators)
        else:
            chart_data = visualizer.prepare_candlestick_data(indicators)
            
        # Slice data to requested date range
        requested_mask = (
            pd.to_datetime(chart_data['dates']) >= start_dt
        ) & (
            pd.to_datetime(chart_data['dates']) <= end_dt
        )
        
        chart_data['dates'] = [d for i, d in enumerate(chart_data['dates']) if requested_mask[i]]
        chart_data['ohlc'] = [d for i, d in enumerate(chart_data['ohlc']) if requested_mask[i]]
        chart_data['volume'] = [d for i, d in enumerate(chart_data['volume']) if requested_mask[i]]
        
        # Slice indicators
        if 'indicators' in chart_data:
            for indicator_type in chart_data['indicators']:
                if isinstance(chart_data['indicators'][indicator_type], dict):
                    for key in chart_data['indicators'][indicator_type]:
                        chart_data['indicators'][indicator_type][key] = [
                            d for i, d in enumerate(chart_data['indicators'][indicator_type][key])
                            if requested_mask[i]
                        ]
            
        return {
            "success": True,
            "data": chart_data
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/performance", response_model=ChartResponse)
async def get_performance_data(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get performance metrics and analysis"""
    try:
        if not end_date:
            end_dt = datetime.now()
        else:
            end_dt = pd.to_datetime(end_date)
        if not start_date:
            start_dt = end_dt - timedelta(days=30)
        else:
            start_dt = pd.to_datetime(start_date)
            
        # Get extra data for better calculations
        calc_start = start_dt - timedelta(days=30)  # Extra month for calculations
        data = fetch_stock_data(ticker, calc_start, end_dt)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        
        # Calculate metrics using full dataset
        analyzer = StockAnalyzer(data)
        daily_returns = analyzer.daily_returns
        
        # Slice to requested date range
        mask = (daily_returns.index >= start_dt) & (daily_returns.index <= end_dt)
        returns_slice = daily_returns[mask]
        
        metrics = {
            'mean_return': float(returns_slice.mean()),
            'sharpe_ratio': float(returns_slice.mean() / returns_slice.std()) if returns_slice.std() != 0 else 0,
            'win_rate': float((returns_slice > 0).mean()),
            'max_drawdown': float((returns_slice.cumsum() - returns_slice.cumsum().expanding().max()).min()),
            'return_series': returns_slice,
            'cumulative_returns': (1 + returns_slice).cumprod() - 1
        }
        
        visualizer = StockVisualizer(analyzer)
        return {
            "success": True,
            "data": visualizer.generate_performance_dashboard(metrics)
        }
        
    except Exception as e:
        print(f"Performance calculation error: {str(e)}")  
        raise HTTPException(status_code=500, detail="Error calculating performance metrics")