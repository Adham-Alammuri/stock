import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { StockAPI } from './lib/api'
import DatePicker from 'react-datepicker'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import "react-datepicker/dist/react-datepicker.css"
import ClusterChart from './components/ClusterChart';
import StockChart from './components/TechnicalChart';

const SignalIcon = ({ signal }) => {
  if (signal?.includes('BUY')) {
    return <TrendingUp className="w-8 h-8 text-green-500" />;
  } else if (signal?.includes('SELL')) {
    return <TrendingDown className="w-8 h-8 text-red-500" />;
  }
  return <Minus className="w-8 h-8 text-yellow-500" />;
};

function App() {
  const [formState, setFormState] = useState({
    ticker: '',
    analysisMode: 'default',
    startDate: null,
    endDate: null,
  })
  
  // Separate state for submitted values
  const [submittedValues, setSubmittedValues] = useState({
    ticker: '',
    startDate: null,
    endDate: null,
  })
  
  const [activeView, setActiveView] = useState('prediction')

  const handleInputChange = (field, value) => {
    setFormState(prev => ({
      ...prev,
      [field]: field === 'ticker' ? value.toUpperCase() : value
    }))
  }
  
  const predictionQuery = useQuery({
    queryKey: ['prediction', submittedValues.ticker, submittedValues.startDate, submittedValues.endDate],
    queryFn: () => StockAPI.getPrediction({ 
      ticker: submittedValues.ticker,
      start_date: submittedValues.startDate?.toISOString().split('T')[0],
      end_date: submittedValues.endDate?.toISOString().split('T')[0],
    }),
    enabled: !!submittedValues.ticker,
  })

  const chartQuery = useQuery({
    queryKey: ['chart', submittedValues.ticker, submittedValues.startDate, submittedValues.endDate],
    queryFn: () => StockAPI.getChartData({ 
      ticker: submittedValues.ticker,
      start_date: submittedValues.startDate?.toISOString().split('T')[0],
      end_date: submittedValues.endDate?.toISOString().split('T')[0],
    }),
    enabled: !!submittedValues.ticker && activeView === 'visualizer',
  })

  const sentimentQuery = useQuery({
    queryKey: ['sentiment', submittedValues.ticker],
    queryFn: () => StockAPI.getSentimentAnalysis({ ticker: submittedValues.ticker }),
    enabled: !!submittedValues.ticker,
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (formState.ticker) {
      setSubmittedValues({
        ticker: formState.ticker,
        startDate: formState.startDate,
        endDate: formState.endDate,
      })
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="w-3/4 mx-auto py-8">
        {/* Header and Toggle Section */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">Stock Analysis Dashboard</h1>
          
          <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1">
            <button
              onClick={() => setActiveView('prediction')}
              className={`px-6 py-2 rounded-lg transition-colors ${
                activeView === 'prediction' 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Prediction
            </button>
            <button
              onClick={() => setActiveView('visualizer')}
              className={`px-6 py-2 rounded-lg transition-colors ${
                activeView === 'visualizer' 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Chart Analysis
            </button>
          </div>
        </div>
        
        {/* Form Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex gap-4">
              <input
                type="text"
                value={formState.ticker}
                onChange={(e) => handleInputChange('ticker', e.target.value)}
                placeholder="Enter stock ticker (e.g., AAPL)"
                className="flex-grow p-2 border rounded"
              />
              
              <select 
                value={formState.analysisMode}
                onChange={(e) => handleInputChange('analysisMode', e.target.value)}
                className="p-2 border rounded w-40"
              >
                <option value="default">Default (1 Year)</option>
                <option value="custom">Custom Date Range</option>
              </select>
            </div>
            
            {formState.analysisMode === 'custom' && (
              <div className="flex gap-4 justify-center">
                <div>
                  <label className="block text-sm mb-1">Start Date</label>
                  <DatePicker
                    selected={formState.startDate}
                    onChange={(date) => handleInputChange('startDate', date)}
                    className="p-2 border rounded"
                    maxDate={formState.endDate || new Date()}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">End Date</label>
                  <DatePicker
                    selected={formState.endDate}
                    onChange={(date) => handleInputChange('endDate', date)}
                    className="p-2 border rounded"
                    minDate={formState.startDate}
                    maxDate={new Date()}
                  />
                </div>
              </div>
            )}
            
            <button 
              type="submit"
              className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
              disabled={formState.analysisMode === 'custom' && (!formState.startDate || !formState.endDate)}
            >
              Analyze
            </button>
          </form>
        </div>

        {/* Results Section */}
        {activeView === 'prediction' ? (
          <div className="space-y-6">
            {predictionQuery.isLoading && (
              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                  <p className="mt-2">Loading prediction data...</p>
                </div>
              </div>
            )}
            
            {predictionQuery.error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                Error: {predictionQuery.error.message}
              </div>
            )}

            {predictionQuery.data?.data && (
              <div className="space-y-6">
                {/* Current Prediction Card */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-bold mb-4">Current Prediction</h2>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <SignalIcon signal={predictionQuery.data.data.overview.current_prediction.signal} />
                      <div>
                        <p className="text-2xl font-bold">{predictionQuery.data.data.overview.current_prediction.signal}</p>
                        <p className="text-gray-600">
                        Analysis as of market close {predictionQuery.data.data.overview.current_prediction.date}
                        </p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      predictionQuery.data.data.overview.current_prediction.confidence === 'High'
                        ? 'bg-green-100 text-green-800'
                        : predictionQuery.data.data.overview.current_prediction.confidence === 'Medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                    }`}>
                      {predictionQuery.data.data.overview.current_prediction.confidence} Confidence
                    </span>
                  </div>
                </div>

                {/* Strategy Performance Card */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-bold mb-4">Strategy Performance</h2>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(predictionQuery.data.data.strategy_performance.metrics).map(([key, value]) => (
                      <div key={key} className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}</p>
                        <p className="text-lg font-semibold">
                          {typeof value === 'number'
                            ? key.includes('rate') || key.includes('return')
                              ? `${(value * 100).toFixed(2)}%`
                              : value.toFixed(2)
                            : value}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {predictionQuery.data.data.strategy_performance.explanations[key]}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                  {/* Clustering Analysis Card */}
                  <div className="bg-white p-6 rounded-lg shadow-md">
                    <h2 className="text-xl font-bold mb-4">Market Clustering Analysis</h2>
                    {predictionQuery.data?.data?.clustering_visualization ? (
                      <ClusterChart data={predictionQuery.data.data.clustering_visualization} />
                    ) : (
                      <div className="text-center text-gray-500">
                        No clustering data available
                      </div>
                    )}
                  </div>

                  {/* Sentiment Analysis Card */}
                  <div className="bg-white p-6 rounded-lg shadow-md">
                    <h2 className="text-xl font-bold mb-4">Sentiment Analysis</h2>
                    {sentimentQuery.isLoading ? (
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                        <p className="mt-2">Loading sentiment data...</p>
                      </div>
                    ) : sentimentQuery.error?.response?.status === 429 ? (
                      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
                        Alpha Vantage API rate limit reached. Please try again tomorrow or upgrade to a premium plan.
                      </div>
                    ) : sentimentQuery.error ? (
                      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                        Error loading sentiment data: {sentimentQuery.error.message}
                      </div>
                    ) : sentimentQuery.data?.data && (
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-600">Overall Sentiment</p>
                          <p className="text-lg font-semibold">
                            {sentimentQuery.data.data.overall_sentiment?.toFixed(2) ?? 'N/A'}
                          </p>
                          <p className="text-sm text-gray-500">
                            {sentimentQuery.data.data.sentiment_category}
                          </p>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-600">News Volume</p>
                          <p className="text-lg font-semibold">
                            {sentimentQuery.data.data.news_count ?? 'N/A'}
                          </p>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-600">Sentiment Trend</p>
                          <p className="text-lg font-semibold">
                            {sentimentQuery.data.data.sentiment_trend ?? 'N/A'}
                          </p>
                        </div>
                        {/* Add sentiment definition */}
                        <div className="col-span-3 mt-4 p-4 bg-gray-50 rounded-lg">
                          <p className="text-sm font-medium mb-2">Sentiment Score Ranges:</p>
                          {Object.entries(sentimentQuery.data.data.sentiment_score_definition || {}).map(([category, range]) => (
                            <div key={category} className="text-sm text-gray-600">
                              <span className="font-medium">{category}:</span> {range}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>  

                {/* Technical Indicators Card */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-bold mb-4">Technical Indicators</h2>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(predictionQuery.data.data.technical_indicators.current_values).map(([key, value]) => (
                      <div key={key} className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}</p>
                        <p className="text-lg font-semibold">{value.toFixed(2)}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {predictionQuery.data.data.technical_indicators.interpretations[key]}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Baseline Comparison Card */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-bold mb-4">Performance Comparison</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-lg font-semibold mb-3">Buy & Hold Performance</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Accuracy</span>
                          <span className="font-medium">{(predictionQuery.data.data.baseline_comparison.buy_hold_metrics.accuracy * 100).toFixed(2)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Sharpe Ratio</span>
                          <span className="font-medium">{predictionQuery.data.data.baseline_comparison.buy_hold_metrics.sharpe_ratio.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Annual Return</span>
                          <span className="font-medium">{(predictionQuery.data.data.baseline_comparison.buy_hold_metrics.annual_return * 100).toFixed(2)}%</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3">Recommendation</h3>
                      <p className="text-gray-700">{predictionQuery.data.data.baseline_comparison.recommendation}</p>
                      <p className="mt-2 text-sm text-gray-500">
                        Strategy performance is {predictionQuery.data.data.baseline_comparison.strategy_vs_baseline.toLowerCase()} compared to baseline
                      </p>
                    </div>
                  </div>
                </div>

                {/* Recent Performance Card */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-bold mb-4">Recent Performance</h2>
                  <p className="text-sm text-gray-600 mb-4">{predictionQuery.data.data.recent_performance.period}</p>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(predictionQuery.data.data.recent_performance.metrics).map(([key, value]) => (
                      <div key={key} className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}</p>
                        <p className="text-lg font-semibold">
                          {typeof value === 'number'
                            ? key.includes('rate') || key.includes('return')
                              ? `${(value * 100).toFixed(2)}%`
                              : value.toFixed(2)
                            : value}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white p-6 rounded-lg shadow-md">
            {chartQuery.isLoading && (
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-2">Loading chart data...</p>
              </div>
            )}
            {chartQuery.error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                Error: {chartQuery.error.message}
              </div>
            )}
          {chartQuery.data && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold">Technical Analysis</h2>
              {}
              <StockChart data={chartQuery.data.data} />
            </div>
          )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App