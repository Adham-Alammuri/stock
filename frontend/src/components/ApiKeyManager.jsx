import React, { useState, useEffect } from 'react';

const ApiKeyManager = ({ onApiKeyChange }) => {
  const [apiKey, setApiKey] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    const storedKey = localStorage.getItem('alphavantage_api_key');
    if (storedKey) {
      setApiKey(storedKey);
      onApiKeyChange(storedKey);
    } else {
      setIsEditing(true);
    }
  }, [onApiKeyChange]);

  const handleSave = () => {
    if (apiKey.trim()) {
      localStorage.setItem('alphavantage_api_key', apiKey);
      setIsEditing(false);
      setShowSuccess(true);
      onApiKeyChange(apiKey);
      setTimeout(() => setShowSuccess(false), 3000);
    }
  };

  const handleRemove = () => {
    localStorage.removeItem('alphavantage_api_key');
    setApiKey('');
    setIsEditing(true);
    onApiKeyChange(null);
  };

  if (!isEditing && apiKey) {
    return (
      <div className="mb-6 bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-green-500">✓</span>
            <span className="text-sm text-gray-600">API Key configured</span>
          </div>
          <div className="space-x-2">
            <button 
              className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
              onClick={() => setIsEditing(true)}
            >
              Change
            </button>
            <button 
              className="px-3 py-1 text-sm border rounded hover:bg-gray-50 text-red-500"
              onClick={handleRemove}
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-6 bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Alpha Vantage API Key (Optional)</h2>
      <div className="space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded p-4 text-sm text-blue-700">
          To use sentiment analysis features, please provide your Alpha Vantage API key. 
          You can get a free API key from{' '}
          <a 
            href="https://www.alphavantage.co/support/#api-key" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline"
          >
            Alpha Vantage
          </a>
          . The free tier includes 25 API calls per day.
        </div>

        <div className="flex space-x-2">
          <input
            type="password"
            placeholder="Enter your API key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="flex-grow p-2 border rounded"
          />
          <button 
            onClick={handleSave} 
            disabled={!apiKey.trim()}
            className={`px-4 py-2 rounded ${
              apiKey.trim() 
                ? 'bg-blue-500 text-white hover:bg-blue-600' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Save
          </button>
        </div>

        {showSuccess && (
          <div className="bg-green-50 border border-green-200 rounded p-4 text-sm text-green-700">
            API key saved successfully!
          </div>
        )}
      </div>
    </div>
  );
};

export default ApiKeyManager;