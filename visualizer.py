import matplotlib.pyplot as plt
import mplfinance as mpf
from typing import List, Dict, Optional, Union
import pandas as pd
import numpy as np

class StockVisualizer:
    """
    Visualization class for stock market technical analysis.
    
    Provides multiple visualization methods:
    - Candlestick charts with technical indicators
    - Technical analysis dashboard with price, volume, and RSI
    - Data preparation for web-based visualization
    
    Features:
    - Multiple technical indicators (SMA, BB, RSI)
    - Volume analysis
    - Customizable styling
    - Web-ready data formatting
    """
        
    def __init__(self, analyzer):
        """
        Initialize visualizer with a StockAnalyzer instance.
        
        Args:
            analyzer: StockAnalyzer instance containing data and indicator methods
        """
        self.analyzer = analyzer

        self.style = {
            'prices': '#2E86C1',      # Blue for price line
            'sma20': '#28B463',       # Green for SMA 20
            'sma50': '#E74C3C',       # Red for SMA 50
            'ema': '#D35400',         # Orange for EMA
            'bb_upper': '#BB8FCE',    # Purple for Bollinger Bands
            'bb_lower': '#BB8FCE',
            'volume': '#566573',      # Grey for volume
            'up_candle': '#2ECC71',   # Green for price increase
            'down_candle': '#E74C3C'  # Red for price decrease
        }

    def _format_volume(self, x, p):
        """
        Helper method to format volume values.
        
        Args:
            x: Volume number
            p: Position (unused, required by formatter)
            
        Returns:
            Formatted string (e.g., '1.5M', '500K', '2.1B')
        """
        if x == 0:
            return '0'
        elif x >= 1e9:  # Billions
            return f'{x/1e9:.1f}B'
        elif x >= 1e6:  # Millions
            return f'{int(x/1e6)}M'
        else:
            return f'{int(x/1e3)}K'
            
    def plot_candlestick(self, indicators: List[str] = ['sma', 'bb'], output_format: str = 'matplotlib') -> Union[None, Dict]:
        """
        Create candlestick chart with optional technical indicators.
        
        Args:
            indicators: List of indicators to plot ['sma', 'ema', 'bb', 'rsi']
            output_format: Either 'matplotlib' for display or 'json' for web
            
        Returns:
            None for matplotlib display, Dict for web data format
        """

        if output_format == 'matplotlib':
            # Prepare the plot style
            mc = mpf.make_marketcolors(
                up=self.style['up_candle'],
                down=self.style['down_candle'],
                edge='inherit',
                volume=self.style['volume']
            )
            style = mpf.make_mpf_style(
                marketcolors=mc,
                y_on_right=False,
                )

            added_plots = []

            if 'sma' in indicators:
                sma20 = self.analyzer.calculate_sma(20)
                sma50 = self.analyzer.calculate_sma(50)
                added_plots.extend([
                    mpf.make_addplot(sma20, color=self.style['sma20'], label='SMA 20'),
                    mpf.make_addplot(sma50, color=self.style['sma50'], label='SMA 50')
                ])
            
            if 'bb' in indicators:
                bb = self.analyzer.calculate_bollinger_bands()
                added_plots.extend([
                    mpf.make_addplot(bb['BB_Upper'], color=self.style['bb_upper']),
                    mpf.make_addplot(bb['BB_Lower'], color=self.style['bb_lower'])
                ])
            
            fig, axes = mpf.plot(
                self.analyzer.data,
                type='candle',
                style=style,
                volume=True,
                addplot=added_plots,
                returnfig=True,
                volume_panel=1,
                ylabel='Price ($)'
            )

            plt.title('Stock Price with technical Indicators')
            plt.show()
        
        else:
            return self.prepare_candlestick_data(indicators)
        
    def plot_technical_analysis(self, indicators: List[str] = ['sma', 'ema', 'bb', 'rsi'], output_format: str = 'matplotlib') -> Union[None, Dict]:
        """
        Create comprehensive technical analysis chart with multiple panels.
        
        Args:
            indicators: List of indicators to include
            output_format: 'matplotlib' for display or 'json' for web
        """

        if output_format == 'matplotlib':

            fig = plt.figure(figsize=(12, 8))
            
            gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.3)
            
            # Main price plot with indicators
            ax1 = fig.add_subplot(gs[0])
            ax1.plot(self.analyzer.data.index, self.analyzer.data['Close'],
                    label='Price', color=self.style['prices'])
            
            # Add technical indicators to main plot
            if 'sma' in indicators:
                sma20 = self.analyzer.calculate_sma(20)
                sma50 = self.analyzer.calculate_sma(50)
                ax1.plot(sma20.index, sma20, label='SMA 20', 
                        color=self.style['sma20'])
                ax1.plot(sma50.index, sma50, label='SMA 50', 
                        color=self.style['sma50'])
            
            if 'bb' in indicators:
                bb = self.analyzer.calculate_bollinger_bands()
                ax1.fill_between(bb.index, bb['BB_Upper'], bb['BB_Lower'],
                               alpha=0.1, color=self.style['bb_upper'])
            
            ax1.set_title('Price and Indicators')
            ax1.legend()
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.2f}'))

            
            # Volume subplot
            ax2 = fig.add_subplot(gs[1])
            ax2.bar(self.analyzer.data.index, self.analyzer.data['Volume'],
                   color=self.style['volume'])
            ax2.set_title('Volume')
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(self._format_volume))

            
            # RSI subplot with overbought/oversold lines
            if 'rsi' in indicators:
                ax3 = fig.add_subplot(gs[2])
                rsi = self.analyzer.calculate_rsi()
                ax3.plot(rsi.index, rsi, color='purple')
                ax3.axhline(y=70, color='r', linestyle='--')  # Overbought line
                ax3.axhline(y=30, color='g', linestyle='--')  # Oversold line
                ax3.set_title('RSI')
                ax3.set_ylim(0, 100)  # RSI scale
                ax3.fill_between(rsi.index, rsi, 70, where=(rsi>=70), color='r', alpha=0.3)
                ax3.fill_between(rsi.index, rsi, 30, where=(rsi<=30), color='g', alpha=0.3)

            plt.tight_layout()
            plt.show()
        else:
            return self._prepare_technical_data(indicators)
    
    def prepare_candlestick_data(self, indicators: List[str]) -> Dict:

        """
        Prepare candlestick data for web visualization.
        
        Args:
            indicators: List of indicators to include in the data
            
        Returns:
            Dictionary containing formatted data for web charts
        """       
        data = {
            'dates': self.analyzer.data.index.strftime('%Y-%m-%d').tolist(),
            'ohlc': self.analyzer.data[['Open', 'High', 'Low', 'Close']].values.tolist(),
            'volume': self.analyzer.data['Volume'].tolist(),
            'indicators': {}
        }

        if 'sma' in indicators:
            data['indicators']['sma'] = {
                'sma20': self.analyzer.calculate_sma(20).tolist(),
                'sma50': self.analyzer.calculate_sma(50).tolist(),
            }
        if 'bb' in indicators:
            bb = self.analyzer.calculate_bollinger_bands()
            data['indicators']['bollinger'] = {
                'upper':  bb['BB_Upper'].tolist(),
                'middle': bb['BB_Middle'].tolist(),
                'lower:': bb['BB_Lower'].tolist()
            }

        return data