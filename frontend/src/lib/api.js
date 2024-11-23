// src/lib/api.js
import axios from 'axios';

const API_URL = 'https://stock-analysis-backend-9ly4.onrender.com';

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const StockAPI = {
  getPrediction: async ({ ticker }, retries = 3) => {
    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        const response = await axios.get(`${API_URL}/api/prediction/${ticker}/predict`);
        return response.data;
      } catch (error) {
        if (attempt === retries - 1) {
          if (error.response?.status === 404) {
            throw new Error(`Could not find any data for ticker '${ticker}'. Please verify the ticker symbol is correct.`);
          }
          console.error('API Error:', error);
          throw error;
        }
        // Wait for 2s, 4s then 6s)
        await wait(2000 * (attempt + 1));
      }
    }
  },

  getChartData: async ({ ticker }, retries = 3) => {
    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        const response = await axios.get(`${API_URL}/api/visualization/${ticker}/chart`);
        return response.data;
      } catch (error) {
        if (attempt === retries - 1) {
          console.error('API Error:', error);
          throw error;
        }
        await wait(2000 * (attempt + 1));
      }
    }
  },

  getSentimentAnalysis: async ({ ticker, apiKey }, retries = 3) => {
    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        const response = await axios.get(`${API_URL}/api/sentiment/${ticker}/analyze`, {
          headers: {
            'X-API-KEY': apiKey
          }
        });
        return response.data;
      } catch (error) {
        if (attempt === retries - 1) {
          if (error.response?.status === 429) {
            throw new Error(error.response.data.detail);
          }
          if (error.response?.status === 401) {
            throw new Error('Invalid API key. Please check your API key and try again.');
          }
          console.error('API Error:', error);
          throw error;
        }
        await wait(2000 * (attempt + 1));
      }
    }
  }
}