/**
 * MedMatch - Callback Probability Predictor Component
 * Uses TensorFlow.js neural network for real-time predictions
 */
import React, { useState, useEffect, useCallback } from 'react';
import { callbackPredictor } from '../../services/callbackPredictorModel';

const CallbackProbabilityPredictor = ({ 
  resume, 
  job, 
  onPredictionComplete,
  className = '' 
}) => {
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  // Initialize model and run prediction when resume/job changes
  const runPrediction = useCallback(async () => {
    if (!resume || !job) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Initialize model if needed
      await callbackPredictor.initialize();
      
      // Run analysis
      const result = await callbackPredictor.analyzeMatch(resume, job);
      setPrediction(result);
      
      // Get model info
      setModelInfo(callbackPredictor.getModelInfo());
      
      // Callback to parent
      if (onPredictionComplete) {
        onPredictionComplete(result);
      }
    } catch (err) {
      console.error('Prediction error:', err);
      setError(err.message || 'Failed to predict callback probability');
    } finally {
      setIsLoading(false);
    }
  }, [resume, job, onPredictionComplete]);

  useEffect(() => {
    runPrediction();
  }, [runPrediction]);

  // Get color based on probability
  const getColor = (prob) => {
    if (prob >= 70) return 'text-green-600 bg-green-100';
    if (prob >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getGradient = (prob) => {
    if (prob >= 70) return 'from-green-500 to-emerald-500';
    if (prob >= 40) return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-rose-500';
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg ${className}`}>
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-turquoise"></div>
          <span className="text-gray-600 dark:text-gray-300">
            Analyzing your match with AI...
          </span>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className={`bg-red-50 dark:bg-red-900/20 rounded-xl p-6 ${className}`}>
        <div className="flex items-center space-x-3 text-red-600 dark:text-red-400">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
        <button 
          onClick={runPrediction}
          className="mt-4 text-sm text-turquoise hover:underline"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Render prediction results
  if (!prediction) return null;

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden ${className}`}>
      {/* Header with main score */}
      <div className={`bg-gradient-to-r ${getGradient(prediction.probability)} p-6`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white/80 text-sm font-medium mb-1">
              AI Callback Probability
            </h3>
            <div className="flex items-baseline space-x-2">
              <span className="text-5xl font-bold text-white">
                {prediction.probability}%
              </span>
              <span className="text-white/70 text-lg capitalize">
                {prediction.category} chance
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="bg-white/20 rounded-full px-3 py-1 text-white text-sm mb-2">
              <span className="mr-1">🧠</span>
              TensorFlow.js
            </div>
            <div className="text-white/70 text-xs">
              {prediction.confidence}% confidence
            </div>
          </div>
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700">
        <div className="bg-white dark:bg-gray-800 p-4 text-center">
          <div className="text-2xl font-bold text-turquoise">
            {Math.round((prediction.features?.skills_match_ratio || 0) * 100)}%
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Skills Match</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 text-center">
          <div className="text-2xl font-bold text-pink-500">
            {Math.round((prediction.features?.job_title_similarity || 0) * 100)}%
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Title Match</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 text-center">
          <div className="text-2xl font-bold text-purple-500">
            {Math.round((prediction.features?.resume_completeness || 0) * 100)}%
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Profile Score</div>
        </div>
      </div>

      {/* Recommendations */}
      {prediction.recommendations && prediction.recommendations.length > 0 && (
        <div className="p-4 border-t dark:border-gray-700">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            💡 Recommendations to Improve
          </h4>
          <ul className="space-y-2">
            {prediction.recommendations.slice(0, 3).map((rec, idx) => (
              <li key={idx} className="flex items-start space-x-2 text-sm">
                <span className={`
                  px-2 py-0.5 rounded text-xs font-medium
                  ${rec.priority === 'high' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : ''}
                  ${rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' : ''}
                  ${rec.priority === 'low' ? 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400' : ''}
                `}>
                  {rec.priority}
                </span>
                <span className="text-gray-600 dark:text-gray-300">{rec.message}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Toggle details */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="w-full p-3 text-sm text-turquoise hover:bg-turquoise/5 transition-colors flex items-center justify-center space-x-1"
      >
        <span>{showDetails ? 'Hide' : 'Show'} Technical Details</span>
        <svg 
          className={`w-4 h-4 transition-transform ${showDetails ? 'rotate-180' : ''}`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Detailed breakdown */}
      {showDetails && (
        <div className="p-4 border-t dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Feature Analysis
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(prediction.features || {}).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between text-sm">
                <span className="text-gray-500 dark:text-gray-400">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-turquoise h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.round(value * 100)}%` }}
                    />
                  </div>
                  <span className="text-gray-700 dark:text-gray-300 w-10 text-right">
                    {Math.round(value * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          {modelInfo && (
            <div className="mt-4 pt-4 border-t dark:border-gray-700">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                <div className="flex justify-between">
                  <span>Model Version:</span>
                  <span className="font-mono">{modelInfo.version}</span>
                </div>
                <div className="flex justify-between mt-1">
                  <span>Features Used:</span>
                  <span>{modelInfo.numFeatures}</span>
                </div>
                <div className="flex justify-between mt-1">
                  <span>Neural Network:</span>
                  <span>4 layers, in-browser</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CallbackProbabilityPredictor;
