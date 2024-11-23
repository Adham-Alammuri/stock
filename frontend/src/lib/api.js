// src/lib/api.js
import axios from 'axios';

const API_URL = 'http://0.0.0.0:10000/';

export const StockAPI = {
  getPrediction: async ({ ticker }) => {
    try {
      const response = await axios.get(`${API_URL}/api/prediction/${ticker}/predict`);
      return response.data;
    } catch (error) {
        if (error.response?.status === 404) {
            throw new Error(`Could not find any data for ticker '${ticker}'. Please verify the ticker symbol is correct.`);
        }
      console.error('API Error:', error);
      throw error;
    }
  },

  getChartData: async ({ ticker }) => {
    try {
      const response = await axios.get(`${API_URL}/api/visualization/${ticker}/chart`);
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  getSentimentAnalysis: async ({ ticker, apiKey }) => {
    try {
      const response = await axios.get(`${API_URL}/api/sentiment/${ticker}/analyze`, {
        headers: {
          'X-API-KEY': apiKey
        }
      });
      return response.data;
    } catch (error) {
      if (error.response?.status === 429) {
        throw new Error(error.response.data.detail);
      }
      if (error.response?.status === 401) {
        throw new Error('Invalid API key. Please check your API key and try again.');
      }
      console.error('API Error:', error);
      throw error;
    }
  }
}