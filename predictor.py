from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, List
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class BasePredictor(ABC):
    """Base class"""
    
    @abstractmethod
    def train(self) -> None:
        """Train the prediction model"""
        pass
        
    @abstractmethod
    def predict(self) -> pd.Series:
        """Generate predictions"""
        pass
        
    @abstractmethod
    def evaluate(self) -> Dict:
        """Evaluate model performance"""
        pass

class UnsupervisedStrategyAnalyzer(BasePredictor):
    """
    Implements unsupervised learning based trading strategy using clustering.
    """
    def __init__(self, data: pd.DataFrame, n_clusters: int = 4):
        """
        Initialize the unsupervised strategy analyzer.
        
        Args:
            data: DataFrame with features from StockAnalyzer
            n_clusters: Number of clusters for K-means
        """
        self.data = data
        self.n_clusters = n_clusters
        self.feature_cols = [
            'return_1d', 'vol', 'momentum_20d',
            'rsi', 'bb_position', 'dollar_volume',
            'relative_volume', 'garman_klass_vol'
        ]
        
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.clusters = None
        self.cluster_performance = {}
        
    def train(self) -> None:
        """Train the clustering model on the current data."""
        # Scale features
        features = self.data[self.feature_cols]
        scaled_features = self.scaler.fit_transform(features)
        
        # Fit clustering model
        self.clusters = self.model.fit_predict(scaled_features)
        
        # Analyze cluster performance
        self.data['cluster'] = self.clusters
        for cluster in range(self.n_clusters):
            cluster_returns = self.data[self.data['cluster'] == cluster]['return_1d']
            self.cluster_performance[cluster] = {
                'mean_return': cluster_returns.mean(),
                'sharpe': cluster_returns.mean() / cluster_returns.std(),
                'size': len(cluster_returns)
            }
    
            
    def predict(self) -> pd.Series:
        """
        Generate predictions based on cluster membership.
        
        Returns:
            Series with predicted returns
        """
        if self.clusters is None:
            raise ValueError("Model needs to be trained first")
            
        # Identify best performing cluster based on Sharpe ratio
        best_cluster = max(self.cluster_performance.items(),
                          key=lambda x: x[1]['sharpe'])[0]
                          
        # Generate predictions (1 for stocks in best cluster, 0 otherwise)
        predictions = pd.Series(0, index=self.data.index)
        predictions[self.data['cluster'] == best_cluster] = 1
        
        return predictions
        
    def evaluate(self) -> Dict:
        """
        Evaluate the clustering strategy performance.
        
        Returns:
            Dictionary with performance metrics and return series
        """
        if self.clusters is None:
            raise ValueError("Model needs to be trained first")
            
        metrics = {
            'cluster_performance': self.cluster_performance,
            'cluster_sizes': {
                i: (self.clusters == i).sum() 
                for i in range(self.n_clusters)
            }
        }
        
        # Calculate strategy returns
        predictions = self.predict()
        strategy_returns = (predictions * self.data['return_1d'])
        cumulative_returns = strategy_returns.cumsum()
        
        metrics.update({
            'strategy_metrics': {
                'mean_return': strategy_returns.mean(),
                'sharpe_ratio': strategy_returns.mean() / strategy_returns.std(),
                'win_rate': (strategy_returns > 0).mean(),
                'max_drawdown': (cumulative_returns - 
                            cumulative_returns.expanding().max()).min(),
                'return_series': strategy_returns,  # Add return series
                'cumulative_returns': cumulative_returns  # Optional: add cumulative too
            }
        })
        
        return metrics

class StockPredictor:
    """
    Main interface for prediction system.
    """
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.strategies = {}
        
    def add_strategy(self, name: str, strategy: BasePredictor) -> None:
        """Add a prediction strategy"""
        self.strategies[name] = strategy
        
    def predict(self, strategy_name: str) -> Dict:
        """Get predictions from specified strategy"""
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy {strategy_name} not found")
            
        strategy = self.strategies[strategy_name]
        return {
            'predictions': strategy.predict(),
            'metrics': strategy.evaluate()
        }