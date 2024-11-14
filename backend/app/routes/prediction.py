from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.services.data_fetcher import fetch_stock_data
from app.services.data_analyzer import StockAnalyzer
from app.services.predictor import UnsupervisedStrategyAnalyzer, StockPredictor

router = APIRouter()

def safe_calculation(func):
    """Decorator to handle NaN values in calculations"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return 0.0 if pd.isna(result) else float(result)
        except:
            return 0.0
    return wrapper

@router.get("/{ticker}/predict")
async def get_stock_prediction(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    n_clusters: int = 5,
    min_cluster_size: int = 5,
    lookback_window: int = 252
):
    try:
        end_dt = pd.to_datetime(end_date) if end_date else datetime.now()
        start_dt = pd.to_datetime(start_date) if start_date else end_dt - timedelta(days=365)
        calc_start = start_dt - timedelta(days=lookback_window + 50)
        
        data = fetch_stock_data(ticker, calc_start, end_dt)
        if data is None or data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
            
        # Initialize analyzer and calculate features
        analyzer = StockAnalyzer(data)
        
        # Calculate features explicitly
        features = pd.DataFrame(index=data.index)
        features['return_1d'] = analyzer.daily_returns
        features['vol'] = analyzer.calculate_volatility()[1]
        features['momentum_20d'] = data['Close'].pct_change(20)
        features['rsi'] = analyzer.calculate_rsi()
        
        bb = analyzer.calculate_bollinger_bands()
        features['bb_position'] = (data['Close'] - bb['BB_Lower']) / (bb['BB_Upper'] - bb['BB_Lower'])
        
        features['dollar_volume'] = analyzer.calculate_dollar_volume()
        features['relative_volume'] = analyzer.calculate_relative_volume()
        features['garman_klass_vol'] = analyzer.calculate_garman_klass_volatility()
        
        # Clean and align data
        features = features.dropna()
        features = features.loc[start_dt:end_dt]
        
        if len(features) < max(20, n_clusters * min_cluster_size):
            raise HTTPException(status_code=400, detail=f"Insufficient data points ({len(features)})")
            
        # Try multiple initializations to find best clustering
        best_strategy = None
        best_metric = -np.inf
        
        for _ in range(20):  # Try 20 different initializations
            strategy = UnsupervisedStrategyAnalyzer(features, n_clusters=n_clusters)
            strategy.train()
            
            # Check cluster sizes
            sizes = pd.Series(strategy.clusters).value_counts()
            if sizes.min() >= min_cluster_size:
                # Calculate strategy performance
                predictor = StockPredictor(analyzer)
                predictor.add_strategy("unsupervised", strategy)
                result = predictor.predict("unsupervised")
                
                predictions = pd.Series(result['predictions'], index=features.index)
                strategy_returns = predictions * features['return_1d']
                sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
                
                # Score based on sharpe ratio and cluster balance
                size_balance = -np.std(sizes)  # Penalize uneven clusters
                score = sharpe + size_balance
                
                if score > best_metric:
                    best_metric = score
                    best_strategy = strategy
        
        if best_strategy is None:
            raise HTTPException(status_code=400, detail="Could not find valid clustering configuration")
            
        # Get predictions using best strategy
        predictor = StockPredictor(analyzer)
        predictor.add_strategy("unsupervised", best_strategy)
        result = predictor.predict("unsupervised")
        
        # Calculate final metrics
        predictions = pd.Series(result['predictions'], index=features.index)
        strategy_returns = predictions * features['return_1d']
        
        response = {
            "success": True,
            "data": {
                "predictions": {
                    "signals": predictions.astype(int).tolist(),
                    "dates": features.index.strftime('%Y-%m-%d').tolist(),
                },
                "metrics": {
                    "strategy": {
                        "sharpe_ratio": float(strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)),
                        "annual_return": float(((1 + strategy_returns.mean()) ** 252) - 1),
                        "win_rate": float((strategy_returns > 0).mean()),
                        "max_drawdown": float((1 + strategy_returns).cumprod().div(
                            (1 + strategy_returns).cumprod().cummax()).min() - 1)
                    },
                    "clusters": {
                        str(k): {
                            "mean_return": float(v["mean_return"]),
                            "sharpe": float(v["sharpe"]),
                            "size": int(v["size"])
                        }
                        for k, v in result['metrics']['cluster_performance'].items()
                    }
                },
                "feature_stats": features.describe().to_dict()
            }
        }
        
        return response
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))