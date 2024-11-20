import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const ClusterChart = ({ data }) => {
  if (!data?.data) return null;

  const transformedData = data.data.map(cluster => ({
    cluster: cluster.cluster,
    meanReturn: cluster.mean_return * 100,
    sharpe: cluster.metrics.sharpe,
    size: cluster.total_points * 2,
    winRate: cluster.metrics.win_rate * 100
  }));

  return (
    <div className="w-full h-[400px] flex justify-center">
      <ScatterChart 
        width={800} 
        height={400} 
        margin={{ top: 20, right: 20, bottom: 60, left: 60 }} 
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          type="number" 
          dataKey="meanReturn" 
          name="Mean Return" 
          unit="%" 
          label={{ 
            value: 'Mean Return', 
            position: 'bottom', 
            offset: 40  
          }}
        />
        <YAxis 
          type="number" 
          dataKey="sharpe" 
          name="Sharpe Ratio"
          label={{ 
            value: 'Sharpe Ratio', 
            angle: -90, 
            position: 'left',
            offset: 40  
          }}
        />
        <Tooltip 
          formatter={(value, name) => {
            if (name === 'meanReturn') return [`${value.toFixed(2)}%`, 'Mean Return'];
            if (name === 'sharpe') return [value.toFixed(2), 'Sharpe Ratio'];
            if (name === 'size') return [`${value/2} points`, 'Cluster Size'];
            if (name === 'winRate') return [`${value.toFixed(2)}%`, 'Win Rate'];
            return [value, name];
          }}
        />
        <Legend verticalAlign="top" height={36}/>
        <Scatter 
          name="Market Clusters" 
          data={transformedData} 
          fill="#8884d8"
          shape="circle"
        />
      </ScatterChart>
    </div>
  );
};

export default ClusterChart;