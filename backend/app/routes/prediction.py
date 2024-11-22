from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.services.data_fetcher import fetch_stock_data
from app.services.data_analyzer import StockAnalyzer
from app.services.predictor import UnsupervisedStrategyAnalyzer, StockPredictor
from app.services.visualizer import StockVisualizer

router = APIRouter()

def calculate_strategy_metrics(predictions: pd.Series, returns: pd.Series) -> Dict:
    """Calculate strategy performance metrics with proper return scaling"""
    # Get returns only for days we traded
    strategy_returns = returns[predictions == 1]
    total_trades = len(strategy_returns)
    
    if total_trades == 0:
        return {
            "sharpe_ratio": "None",
            "annual_return": "None",
            "win_rate": "None",
            "max_drawdown": "None",
            "total_trades": 0,
            "winning_trades": 0,
            "strategy_status": "HOLD - No trading signals produced in the last 20 trading days"
        }
    
    # Calculate win rate
    winning_trades = (strategy_returns > 0).sum()
    win_rate = winning_trades / total_trades

    # Calculate Sharpe ratio - adjusted for actual trading frequency
    if total_trades > 1:
        daily_mean = strategy_returns.mean()
        daily_std = strategy_returns.std()
        if daily_std != 0:
            # Adjust Sharpe ratio for actual trading frequency
            trading_days_ratio = total_trades / len(returns)
            sharpe = (daily_mean / daily_std) * np.sqrt(252 * trading_days_ratio)
        else:
            sharpe = 0.0
    else:
        sharpe = 0.0

    # Calculate annual return - adjusted for actual trading frequency
    try:
        # Calculate cumulative return from all trades
        cumulative_return = (1 + strategy_returns).prod() - 1
        
        # Annualize based on the proportion of year we're trading
        days_in_period = (returns.index[-1] - returns.index[0]).days
        if days_in_period > 0:
            years = days_in_period / 365.25
            annual_return = (1 + cumulative_return) ** (1 / years) - 1
        else:
            annual_return = 0.0
    except:
        annual_return = 0.0

    # Calculate max drawdown
    try:
        cumulative_returns = (1 + strategy_returns).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min()
    except:
        max_drawdown = 0.0

    return {
        "sharpe_ratio": float(sharpe),
        "annual_return": float(annual_return),
        "win_rate": float(win_rate),
        "max_drawdown": float(max_drawdown),
        "total_trades": int(total_trades),
        "winning_trades": int(winning_trades)
    }

def calculate_baseline_metrics(returns: pd.Series) -> Dict:
    """Calculate buy and hold metrics"""
    if len(returns) == 0:
        return {
            "accuracy": 0.0,
            "sharpe_ratio": 0.0,
            "annual_return": 0.0
        }
    
    accuracy = (returns > 0).mean()
    
    if len(returns) > 1:
        daily_mean = returns.mean()
        daily_std = returns.std()
        if daily_std != 0:
            sharpe = (daily_mean / daily_std) * np.sqrt(252)
        else:
            sharpe = 0.0
        
        if daily_mean > -1:
            annual_return = ((1 + daily_mean) ** 252) - 1
        else:
            annual_return = -1
    else:
        sharpe = 0.0
        annual_return = 0.0

    return {
        "accuracy": float(accuracy),
        "sharpe_ratio": float(sharpe),
        "annual_return": float(annual_return)
    }

@router.get("/{ticker}/predict")
async def get_stock_prediction(
    ticker: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    n_clusters: int = Query(5, ge=2, le=10),
    min_cluster_size: int = Query(5, ge=3),
    lookback_window: int = Query(252, ge=60)
):
    """Generate stock predictions using unsupervised clustering strategy."""
    try:
        # Date handling
        end_dt = pd.to_datetime(end_date) if end_date else datetime.now()
        start_dt = pd.to_datetime(start_date) if start_date else end_dt - timedelta(days=365)
        calc_start = start_dt - timedelta(days=lookback_window + 50)
        
        # Fetch and validate data
        data = fetch_stock_data(ticker, calc_start, end_dt)
        if data is None or data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
            
        # Prepare features
        analyzer = StockAnalyzer(data)
        features = analyzer.prepare_features_for_clustering()
        features = features.loc[start_dt:end_dt]
        
        if len(features) < max(20, n_clusters * min_cluster_size):
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data points ({len(features)})"
            )
            
        # Generate predictions
        strategy = UnsupervisedStrategyAnalyzer(features, n_clusters=n_clusters)
        strategy.train()
        
        predictor = StockPredictor(analyzer)
        predictor.add_strategy("unsupervised", strategy)
        result = predictor.predict("unsupervised")
        
        # Convert predictions to series
        predictions = pd.Series(result['predictions'], index=features.index)
        returns = features['return_1d']
        
        # Calculate metrics
        strategy_metrics = calculate_strategy_metrics(predictions, returns)
        baseline_metrics = calculate_baseline_metrics(returns)
        
        # Calculate recent performance
        recent_preds = predictions[-20:]
        recent_returns = returns[-20:]
        recent_metrics = calculate_strategy_metrics(recent_preds, recent_returns)

        # Generate clustering visualization
        visualizer = StockVisualizer(analyzer)
        clustering_viz = visualizer.plot_clustering_analysis(
            clusters=strategy.clusters,
            returns=features['return_1d'],
            features=features
        )
        
        def clean_nan(obj):
            if isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(x) for x in obj]
            elif isinstance(obj, float):
                return 0.0 if np.isnan(obj) else obj
            return obj
        
        # Prepare response
        response = {
            "success": True,
            "data": {
                "overview": {
                    "ticker": ticker,
                    "analysis_period": {
                        "start": start_dt.strftime('%Y-%m-%d'),
                        "end": end_dt.strftime('%Y-%m-%d'),
                        "trading_days": len(features)
                    },
                    "current_prediction": {
                        "date": features.index[-1].strftime('%Y-%m-%d'),
                        "signal": "BUY" if predictions.iloc[-1] == 1 else "HOLD/SELL",
                        "confidence": "High" if strategy_metrics["win_rate"] > 0.5 else "Low"
                    }
                },
                "strategy_performance": {
                    "metrics": strategy_metrics,
                    "explanations": {
                        "sharpe_ratio": "Risk-adjusted returns (>1 is good, >2 is very good)",
                        "annual_return": f"Expected yearly return based on {strategy_metrics['total_trades']} trades",
                        "win_rate": f"Won {strategy_metrics['winning_trades']} out of {strategy_metrics['total_trades']} trades",
                        "max_drawdown": "Largest peak-to-trough decline",
                        "total_trades": "Number of trade signals generated"
                    }
                },
                "baseline_comparison": {
                    "buy_hold_metrics": baseline_metrics,
                    "strategy_vs_baseline": "Better" if strategy_metrics["sharpe_ratio"] > baseline_metrics["sharpe_ratio"] else "Worse",
                    "recommendation": (
                        "Follow strategy signals" if strategy_metrics["sharpe_ratio"] > baseline_metrics["sharpe_ratio"]
                        else "Consider buy & hold instead"
                    )
                },
                "recent_performance": {
                    "metrics": recent_metrics,
                    "period": "Last 20 trading days"
                },
                "clusters": {
                    str(k): {
                        "mean_return": float(v["mean_return"]),
                        "sharpe": float(v["sharpe"]),
                        "size": int(v["size"])
                    }
                    for k, v in result['metrics']['cluster_performance'].items()
                },
                "technical_indicators": {
                    "current_values": {
                        "rsi": float(features['rsi'].iloc[-1]),
                        "volatility": float(features['vol'].iloc[-1]),
                        "momentum": float(features['momentum_20d'].iloc[-1])
                    },
                    "interpretations": {
                        "rsi": "Relative Strength Index (0-100, >70 overbought, <30 oversold)",
                        "volatility": "Market volatility (higher values indicate more risk)",
                        "momentum": "20-day price momentum (positive values indicate upward trend)"
                    }
                },
                "clustering_visualization": clustering_viz 

            }
        }
        
        cleaned_response = clean_nan(response)

        return cleaned_response
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))