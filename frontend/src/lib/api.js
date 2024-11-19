// src/lib/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const StockAPI = {
  getPrediction: async ({ ticker }) => {
    try {
      const response = await axios.get(`${API_URL}/api/prediction/${ticker}/predict`)
      return response.data
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }
}