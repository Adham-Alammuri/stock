import React, { useState } from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  Scatter,
  ReferenceArea
} from 'recharts';
import Checkbox from '../components/Checkbox';

const StockChart = ({ data }) => {
  const [showIndicators, setShowIndicators] = useState({
    price: true,
    candlesticks: true,
    sma20: true,
    sma50: true,
    bollinger: true,
    volume: true,
    rsi: true
  });

  const [zoomState, setZoomState] = useState(null);
  const [dragState, setDragState] = useState({
    startIndex: null,
    endIndex: null
  });

  const formatChartData = (rawData) => {
    if (!rawData?.dates) return [];
    
    return rawData.dates.map((date, index) => {
      const [open, high, low, close] = rawData.ohlc[index];
      
      return {
        index,
        date: new Date(date),
        dateStr: date,
        open,
        high,
        low,
        close,
        price: close,
        volume: rawData.volume[index],
        sma20: rawData.indicators?.sma?.sma20?.[index],
        sma50: rawData.indicators?.sma?.sma50?.[index],
        bb_upper: rawData.indicators?.bollinger?.upper?.[index],
        bb_lower: rawData.indicators?.bollinger?.lower?.[index],
        rsi: rawData.indicators?.rsi?.values?.[index] || null,
        candlestick: [open, close, low, high]
      };
    }).sort((a, b) => a.date - b.date);
  };

  const chartData = formatChartData(data);

  // Calculate price range
  const allPrices = chartData.flatMap(d => [
    d.price,
    d.sma20,
    d.sma50,
    d.bb_upper,
    d.bb_lower,
    d.high,
    d.low
  ].filter(Boolean));

  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const priceRange = maxPrice - minPrice;
  
  const yAxisMin = minPrice - (priceRange * 0.1);
  const yAxisMax = maxPrice + (priceRange * 0.1);

  const CandlestickPoint = (props) => {
    const { x, y, payload, yScale = y => y } = props;
    if (!payload.candlestick) return null;
    
    const [open, close, low, high] = payload.candlestick;
    const isUp = close > open;
    const color = isUp ? '#2ECC71' : '#E74C3C';
    const width = 6;
    
    const openY = props.yAxis.scale(open);
    const closeY = props.yAxis.scale(close);
    const lowY = props.yAxis.scale(low);
    const highY = props.yAxis.scale(high);
    
    return (
      <g>
        <line 
          x1={x} 
          x2={x} 
          y1={lowY} 
          y2={highY} 
          stroke={color} 
        />
        <rect
          x={x - width/2}
          y={Math.min(openY, closeY)}
          width={width}
          height={Math.abs(openY - closeY)}
          fill={color}
          stroke={color}
        />
      </g>
    );
  };

  const handleMouseDown = (e) => {
    if (!e || !e.activeLabel) return;
    const startIndex = chartData.findIndex(d => d.dateStr === e.activeLabel);
    if (startIndex === -1) return;

    setDragState({
      startIndex,
      endIndex: startIndex
    });
  };

  const handleMouseMove = (e) => {
    if (!dragState.startIndex || !e || !e.activeLabel) return;
    const endIndex = chartData.findIndex(d => d.dateStr === e.activeLabel);
    if (endIndex === -1) return;

    setDragState(prev => ({
      ...prev,
      endIndex
    }));
  };

  const handleMouseUp = () => {
    if (dragState.startIndex === null || dragState.endIndex === null) {
      setDragState({ startIndex: null, endIndex: null });
      return;
    }

    const startIndex = Math.min(dragState.startIndex, dragState.endIndex);
    const endIndex = Math.max(dragState.startIndex, dragState.endIndex);

    if (startIndex !== endIndex) {
      setZoomState({ startIndex, endIndex });
    }

    setDragState({ startIndex: null, endIndex: null });
  };

  const handleResetZoom = () => {
    setZoomState(null);
    setDragState({ startIndex: null, endIndex: null });
  };

  // Get visible data based on zoom state
  const getVisibleData = () => {
    if (!zoomState) return chartData;
    return chartData.slice(zoomState.startIndex, zoomState.endIndex + 1);
  };

  const visibleData = getVisibleData();

  const indicators = [
    { key: 'price', label: 'Price Line' },
    { key: 'sma20', label: 'SMA 20' },
    { key: 'sma50', label: 'SMA 50' },
    { key: 'bollinger', label: 'Bollinger Bands' },
    { key: 'rsi', label: 'RSI' }
  ];

  return (
    <div className="space-y-4" style={{ userSelect: 'none' }}>
      <div className="flex flex-wrap gap-4 mb-4">
        {indicators.map(({ key, label }) => (
          <Checkbox
            key={key}
            label={label}
            checked={showIndicators[key]}
            onChange={(checked) => 
              setShowIndicators(prev => ({...prev, [key]: checked}))
            }
          />
        ))}
      </div>

      {zoomState && (
        <div className="flex justify-end mb-2">
          <button
            onClick={handleResetZoom}
            className="px-4 py-2 text-sm bg-gray-200 rounded hover:bg-gray-300"
          >
            Reset Zoom
          </button>
        </div>
      )}

      {/* Price and Indicators Chart */}
      <div className="h-[400px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart 
            data={visibleData}
            margin={{ top: 20, right: 30, left: 70, bottom: 5 }}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
            <XAxis 
              dataKey="dateStr" 
              tickFormatter={(date) => new Date(date).toLocaleDateString()}
              interval="preserveStartEnd"
              minTickGap={50}
            />
            <YAxis 
              domain={[yAxisMin, yAxisMax]}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
              orientation="left"
            />
            <Tooltip
              contentStyle={{ backgroundColor: 'white', borderRadius: '8px' }}
              formatter={(value, name) => {
                if (name === 'volume') return [`${(value/1e6).toFixed(2)}M`, 'Volume'];
                if (typeof value === 'number') return [`$${value.toFixed(2)}`, name];
                return [value, name];
              }}
              labelFormatter={(label) => new Date(label).toLocaleDateString()}
            />
            <Legend />

            {/* Selection area while dragging */}
            {dragState.startIndex !== null && dragState.endIndex !== null && (
              <ReferenceArea
                x1={chartData[dragState.startIndex].dateStr}
                x2={chartData[dragState.endIndex].dateStr}
                strokeOpacity={0.3}
                fill="#8884d8"
                fillOpacity={0.3}
              />
            )}

            {/* Bollinger Bands */}
            {showIndicators.bollinger && (
              <>
                <Line
                  type="monotone"
                  dataKey="bb_upper"
                  stroke="#BB8FCE"
                  dot={false}
                  strokeWidth={1}
                  name="Upper Band"
                />
                <Line
                  type="monotone"
                  dataKey="bb_lower"
                  stroke="#BB8FCE"
                  dot={false}
                  strokeWidth={1}
                  name="Lower Band"
                />
              </>
            )}

            {/* Candlesticks */}
            <Scatter
              data={visibleData}
              shape={(props) => <CandlestickPoint {...props} yAxis={props.yAxis} />}
              legendType="none"
            />

            {/* Price Line */}
            {showIndicators.price && (
              <Line
                type="monotone"
                dataKey="price"
                stroke="#2E86C1"
                dot={false}
                strokeWidth={2}
                name="Price"
              />
            )}

            {/* Moving Averages */}
            {showIndicators.sma20 && (
              <Line
                type="monotone"
                dataKey="sma20"
                stroke="#28B463"
                dot={false}
                strokeDasharray="5 5"
                name="SMA 20"
              />
            )}
            {showIndicators.sma50 && (
              <Line
                type="monotone"
                dataKey="sma50"
                stroke="#E74C3C"
                dot={false}
                strokeDasharray="5 5"
                name="SMA 50"
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Volume Chart */}
      <div className="h-[100px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart 
            data={visibleData}
            margin={{ top: 5, right: 30, left: 70, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
            <XAxis 
              dataKey="dateStr" 
              tickFormatter={(date) => new Date(date).toLocaleDateString()}
              interval="preserveStartEnd"
              minTickGap={50}
            />
            <YAxis 
              orientation="left"
              tickFormatter={(value) => `${(value/1e6).toFixed(0)}M`}
            />
            <Tooltip
              contentStyle={{ backgroundColor: 'white', borderRadius: '8px' }}
              formatter={(value) => [`${(value/1e6).toFixed(2)}M`, 'Volume']}
              labelFormatter={(label) => new Date(label).toLocaleDateString()}
            />
            <Bar
              dataKey="volume"
              fill="#566573"
              opacity={0.5}
              name="Volume"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* RSI Chart */}
      {showIndicators.rsi && (
        <div className="h-[100px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart 
              data={visibleData}
              margin={{ top: 5, right: 30, left: 70, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
              <XAxis 
                dataKey="dateStr" 
                tickFormatter={(date) => new Date(date).toLocaleDateString()}
                interval="preserveStartEnd"
                minTickGap={50}
              />
              <YAxis 
                domain={[0, 100]}
                ticks={[0, 30, 70, 100]}
                orientation="left"
              />
              <Tooltip
                contentStyle={{ backgroundColor: 'white', borderRadius: '8px' }}
                formatter={(value) => [value?.toFixed(2), 'RSI']}
                labelFormatter={(label) => new Date(label).toLocaleDateString()}
              />
              <Line
                type="monotone"
                dataKey="rsi"
                stroke="#8884d8"
                dot={false}
                name="RSI"
              />
              <Line
                type="monotone"
                dataKey={() => 70}
                stroke="#E74C3C"
                strokeDasharray="3 3"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey={() => 30}
                stroke="#28B463"
                strokeDasharray="3 3"
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default StockChart;