import numpy as np
import pandas as pd
from typing import Optional, Tuple, Dict, List

class StockAnalyzer:
    def __init__(self, data: pd.DataFrame, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Initialize StockAnalyzer with market data and optional date range.

        Args:
            data: DataFrame with OHLCV market data
            start_date: Starting date for analysis period
            end_date: Ending date for analysis period

        Raises:
            TypeError: If data is not a pandas DataFrame
            ValueError: If data is empty or missing required columns
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be Pandas DataFrame")
        
        if data.empty:
            raise ValueError("Data is empty")
        
        self.required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in self.required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        self.data = data.copy()
        self.start_date = start_date
        self.end_date = end_date

    @property    
    def daily_returns(self) -> pd.Series:
        """
        Calculate daily percentage returns from closing prices.
        
        Returns:
            Series of daily price returns, using Adjusted Close if available
        """
        if 'Adj Close' in self.data.columns:
            return self.data['Adj Close'].pct_change()
        return self.data['Close'].pct_change()

    def calculate_sma(self, window: int) -> pd.Series:
        """
        Calculate Simple Moving Average for specified window.
        
        Args:
            window: Number of periods for moving average

        Returns:
            Series containing SMA values for each period
        """
        sma = self.data["Close"].rolling(window=window).mean()

        if self.start_date and self.end_date:
            return sma[self.start_date:self.end_date]
        return sma
        
    def calculate_ema(self, window: int = 26) -> pd.Series:
        """
        Calculate Exponential Moving Average.
        
        EMA places greater weight on recent prices compared to SMA.
        Common windows: 12, 26 (MACD), 50, 200 (trend following)
        
        Args:
            window: Number of periods for EMA calculation

        Returns:
            Series containing EMA values for each period
        """
        ema = self.data['Close'].ewm(span=window, adjust=False).mean()
        
        if self.start_date and self.end_date:
            return ema[self.start_date:self.end_date]
        return ema
        
    def calculate_bollinger_bands(self, window: int = 20, num_std: float = 2) -> pd.DataFrame:
        """
        Calculate Bollinger Bands and related indicators.
        
        Includes middle band (SMA), upper/lower bands (±2 std dev),
        %B (price position) and bandwidth (volatility indicator).

        Args:
            window: Period for moving average and standard deviation
            num_std: Number of standard deviations for bands

        Returns:
            DataFrame with columns:
            - BB_Upper: Upper band
            - BB_Middle: Middle band (SMA)
            - BB_Lower: Lower band
            - BB_%B: Price position relative to bands
            - BB_Bandwidth: Band width (volatility indicator)
        """
        middle_band = self.data['Close'].rolling(window=window).mean()
        rolling_std = self.data['Close'].rolling(window=window).std()
        
        upper_band = middle_band + (rolling_std * num_std)
        lower_band = middle_band - (rolling_std * num_std)

        bollinger_bands = pd.DataFrame({
            'BB_Upper': upper_band,
            'BB_Middle': middle_band,
            'BB_Lower': lower_band,
            'BB_%B': (self.data['Close'] - lower_band) / (upper_band - lower_band),
            'BB_Bandwidth': (upper_band - lower_band) / middle_band
        }, index=self.data.index)

        if self.start_date and self.end_date:
            return bollinger_bands[self.start_date:self.end_date]
        return bollinger_bands

    def calculate_rsi(self, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        RSI measures momentum by comparing the magnitude of recent gains
        to recent losses. Range: 0-100, with >70 overbought, <30 oversold.

        Args:
            window: Lookback period for RSI calculation (default: 14)

        Returns:
            Series containing RSI values (0-100) for each period
        """
        delta = self.data['Close'].diff()
        
        gains = delta.copy()
        losses = delta.copy()
        
        gains[gains < 0] = 0
        losses[losses > 0] = 0
        losses = abs(losses)

        avg_gains = gains.rolling(window=window).mean()
        avg_losses = losses.rolling(window=window).mean()

        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    def calculate_volatility(self, window: int = 252) -> Tuple[float, pd.Series]:
        """
        Calculate historical volatility using daily returns.
        
        Annualized volatility is a key risk metric used in financial analysis
        and option pricing. Uses daily returns for improved statistical properties.

        Args:
            window: Rolling window in trading days (default: 252, one year)

        Returns:
            Tuple containing:
            - Current annualized volatility
            - Historical volatility series
        """
        daily_returns = self.data['Close'].pct_change()
        rolling_std = daily_returns.rolling(window=window).std()
        annualized_vol = rolling_std * np.sqrt(252)

        return annualized_vol.iloc[-1], annualized_vol
    
    def calculate_garman_klass_volatility(self) -> pd.Series:
        """
        Calculate Garman-Klass volatility, which provides a more accurate volatility
        estimate using OHLC prices. 
        
        Returns:
            Series containing Garman-Klass volatility values
        """
        return (
            (np.log(self.data['High']) - np.log(self.data['Low'])).pow(2) / 2 -
            (2 * np.log(2) - 1) * 
            (np.log(self.data['Close']) - np.log(self.data['Open'])).pow(2)
        )

    def calculate_dollar_volume(self) -> pd.Series:
        """
        Calculate dollar volume, a measure of trading activity.
        
        Returns:
            Series containing dollar volume values in millions
        """
        return (self.data['Close'] * self.data['Volume']) / 1e6

    def calculate_relative_volume(self, window: int = 20) -> pd.Series:
        """
        Calculate volume relative to its moving average.
        Handles edge cases of zero volume or zero moving average.
        
        Args:
            window: Moving average window length
            
        Returns:
            Series containing relative volume values, minimum value of 0.0001
        """
        volume_ma = self.data['Volume'].rolling(window=window).mean()
        
        # Avoid division by zero
        volume_ma = volume_ma.replace(0, np.nan)
        relative_vol = self.data['Volume'] / volume_ma
        
        # Replace inf, -inf, and nan with 0.0001 (very low relative volume)
        relative_vol = relative_vol.replace([np.inf, -np.inf, np.nan], 0.0001)
        
        return relative_vol
    
    def calculate_momentum(self, periods: List[int] = [5, 10, 20, 50]) -> Dict[str, pd.Series]:
        """
        Calculate price momentum over multiple timeframes.
        
        Args:
            periods: List of periods to calculate momentum for
            
        Returns:
            Dictionary with momentum values for each period
        """
        momentum = {}
        for period in periods:
            momentum[f'momentum_{period}d'] = self.data['Close'].pct_change(periods=period)
        return momentum
    
    def prepare_features_for_clustering(self) -> pd.DataFrame:
        """
        Prepare complete feature set for clustering analysis with proper error handling
        """
        features = pd.DataFrame(index=self.data.index)
        
        # Basic price features
        features['return_1d'] = self.daily_returns.fillna(0)
        
        # Get volatility (handle potential errors)
        try:
            _, vol_series = self.calculate_volatility()
            features['vol'] = vol_series.fillna(method='ffill')
        except Exception as e:
            features['vol'] = 0
            print(f"Error calculating volatility: {e}")
        
        # Momentum features (with error handling)
        momentum_dict = self.calculate_momentum()
        if '20d' in momentum_dict:
            features['momentum_20d'] = momentum_dict['momentum_20d'].fillna(0)
        else:
            features['momentum_20d'] = 0
        
        # Technical indicators
        features['rsi'] = self.calculate_rsi().fillna(50)  # Neutral RSI for missing values
        
        # Bollinger Band position
        try:
            bb = self.calculate_bollinger_bands()
            features['bb_position'] = ((self.data['Close'] - bb['BB_Lower']) / 
                                    (bb['BB_Upper'] - bb['BB_Lower'])).fillna(0.5)
        except Exception:
            features['bb_position'] = 0.5  # Neutral position
        
        # Volume features
        features['dollar_volume'] = self.calculate_dollar_volume().fillna(method='ffill')
        features['relative_volume'] = self.calculate_relative_volume().fillna(1)
        
        # Volatility
        features['garman_klass_vol'] = self.calculate_garman_klass_volatility().fillna(method='ffill')
        
        # Forward fill any remaining NaNs and drop any that still exist
        features = features.fillna(method='ffill').fillna(method='bfill')
        
        # Ensure we have enough valid data
        if len(features.dropna()) < 20:  # Minimum required for meaningful clustering
            raise ValueError("Not enough valid data points for clustering")
            
        return features.dropna()