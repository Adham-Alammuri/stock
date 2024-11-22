// src/lib/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const StockAPI = {
  getPrediction: async ({ ticker }) => {
    try {
      const response = await axios.get(`${API_URL}/api/prediction/${ticker}/predict`);
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },


  getChartData: async ({ ticker, start_date, end_date }) => {
    try {
      const params = new URLSearchParams({
        output_format: 'mpld3',
        ...(start_date && { start_date }),
        ...(end_date && { end_date })
      });
      
      const response = await axios.get(`${API_URL}/api/visualization/${ticker}/chart?${params}`);
      return response.data;
    } catch (error) {
      console.error('Chart API Error:', error);
      throw error;
    }
  },

  getSentimentAnalysis: async ({ ticker }) => {
    try {
      const response = await axios.get(`${API_URL}/api/sentiment/${ticker}/analyze`);
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
}