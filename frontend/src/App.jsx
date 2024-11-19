import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { StockAPI } from './lib/api'
import DatePicker from 'react-datepicker'
import "react-datepicker/dist/react-datepicker.css"

function App() {
  const [ticker, setTicker] = useState('')
  const [submittedTicker, setSubmittedTicker] = useState('') // New state for submitted ticker
  const [analysisMode, setAnalysisMode] = useState('default')
  const [startDate, setStartDate] = useState(null)
  const [endDate, setEndDate] = useState(null)
  const [activeView, setActiveView] = useState('prediction')
  
  const predictionQuery = useQuery({
    queryKey: ['prediction', submittedTicker, startDate, endDate], // Use submittedTicker
    queryFn: () => StockAPI.getPrediction({ 
      ticker: submittedTicker,
      start_date: startDate?.toISOString().split('T')[0],
      end_date: endDate?.toISOString().split('T')[0],
    }),
    enabled: !!submittedTicker, // Only run when submittedTicker has a value
  })

  const chartQuery = useQuery({
    queryKey: ['chart', submittedTicker, startDate, endDate], // Use submittedTicker
    queryFn: () => StockAPI.getChartData({ 
      ticker: submittedTicker,
      start_date: startDate?.toISOString().split('T')[0],
      end_date: endDate?.toISOString().split('T')[0]
    }),
    enabled: !!submittedTicker && activeView === 'visualizer',
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (ticker) {
      setSubmittedTicker(ticker) // Update submittedTicker only on form submission
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8 max-w-4xl"> {/* Container with max width and center alignment */}
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
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="Enter stock ticker (e.g., AAPL)"
                className="flex-grow p-2 border rounded"
              />
              
              <select 
                value={analysisMode}
                onChange={(e) => setAnalysisMode(e.target.value)}
                className="p-2 border rounded w-40"
              >
                <option value="default">Default (1 Year)</option>
                <option value="custom">Custom Date Range</option>
              </select>
            </div>
            
            {analysisMode === 'custom' && (
              <div className="flex gap-4 justify-center">
                <div>
                  <label className="block text-sm mb-1">Start Date</label>
                  <DatePicker
                    selected={startDate}
                    onChange={setStartDate}
                    className="p-2 border rounded"
                    maxDate={endDate || new Date()}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">End Date</label>
                  <DatePicker
                    selected={endDate}
                    onChange={setEndDate}
                    className="p-2 border rounded"
                    minDate={startDate}
                    maxDate={new Date()}
                  />
                </div>
              </div>
            )}
            
            <button 
              type="submit"
              className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
              disabled={analysisMode === 'custom' && (!startDate || !endDate)}
            >
              Analyze
            </button>
          </form>
        </div>

        {/* Results Section */}
        {activeView === 'prediction' ? (
          <div className="bg-white rounded-lg shadow-md p-6">
            {predictionQuery.isLoading && <div className="text-center">Loading prediction data...</div>}
            {predictionQuery.error && <div className="text-red-500">Error: {predictionQuery.error.message}</div>}
            {predictionQuery.data && (
              <div>
                <h2 className="text-xl font-bold mb-4">Prediction Results</h2>
                <pre className="overflow-auto">{JSON.stringify(predictionQuery.data, null, 2)}</pre>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-6">
            {chartQuery.isLoading && <div className="text-center">Loading chart data...</div>}
            {chartQuery.error && <div className="text-red-500">Error: {chartQuery.error.message}</div>}
            {chartQuery.data && (
              <div>
                <h2 className="text-xl font-bold mb-4">Technical Analysis</h2>
                <pre className="overflow-auto">{JSON.stringify(chartQuery.data, null, 2)}</pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App