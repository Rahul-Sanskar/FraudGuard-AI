/**
 * Component to display analysis results.
 */
import React from 'react';
import { AnalysisResponse } from '@/types';
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';

interface AnalysisResultProps {
  result: AnalysisResponse;
}

export const AnalysisResult: React.FC<AnalysisResultProps> = ({ result }) => {
  const getRiskColor = (prediction: string) => {
    switch (prediction) {
      case 'Low':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'Medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'High':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (prediction: string) => {
    switch (prediction) {
      case 'Low':
        return <CheckCircle className="w-6 h-6" />;
      case 'Medium':
        return <AlertTriangle className="w-6 h-6" />;
      case 'High':
        return <AlertCircle className="w-6 h-6" />;
      default:
        return null;
    }
  };

  return (
    <div className={`border-2 rounded-lg p-6 ${getRiskColor(result.prediction)}`}>
      <div className="flex items-center gap-3 mb-4">
        {getRiskIcon(result.prediction)}
        <h3 className="text-xl font-bold">{result.prediction} Risk</h3>
      </div>
      
      <div className="space-y-3">
        <div>
          <p className="text-sm font-medium mb-1">Risk Score</p>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full ${
                result.prediction === 'Low' ? 'bg-green-500' :
                result.prediction === 'Medium' ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${result.risk_score * 100}%` }}
            />
          </div>
          <p className="text-sm mt-1">{(result.risk_score * 100).toFixed(1)}%</p>
        </div>
        
        <div>
          <p className="text-sm font-medium mb-1">Confidence</p>
          <p className="text-lg font-semibold">{(result.confidence * 100).toFixed(1)}%</p>
        </div>
        
        <div>
          <p className="text-sm font-medium mb-1">Explanation</p>
          <p className="text-sm">{result.explanation}</p>
        </div>
      </div>
    </div>
  );
};
