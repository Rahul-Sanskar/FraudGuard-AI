import React from 'react';
import { AnalysisResponse } from '@/types';
import { AlertCircle, CheckCircle, AlertTriangle, TrendingUp } from 'lucide-react';
import { Card, CardBody } from './Card';

interface ResultPanelProps {
  result: AnalysisResponse;
}

export const ResultPanel: React.FC<ResultPanelProps> = ({ result }) => {
  const getRiskConfig = (prediction: string) => {
    switch (prediction) {
      case 'Low':
        return {
          color: 'text-green-600 dark:text-green-400',
          bgColor: 'bg-green-50 dark:bg-green-900/20',
          borderColor: 'border-green-200 dark:border-green-800',
          progressColor: 'bg-green-500',
          icon: <CheckCircle className="w-6 h-6" />,
        };
      case 'Medium':
        return {
          color: 'text-yellow-600 dark:text-yellow-400',
          bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
          borderColor: 'border-yellow-200 dark:border-yellow-800',
          progressColor: 'bg-yellow-500',
          icon: <AlertTriangle className="w-6 h-6" />,
        };
      case 'High':
        return {
          color: 'text-red-600 dark:text-red-400',
          bgColor: 'bg-red-50 dark:bg-red-900/20',
          borderColor: 'border-red-200 dark:border-red-800',
          progressColor: 'bg-red-500',
          icon: <AlertCircle className="w-6 h-6" />,
        };
      default:
        return {
          color: 'text-neutral-600 dark:text-neutral-400',
          bgColor: 'bg-neutral-50 dark:bg-neutral-900/20',
          borderColor: 'border-neutral-200 dark:border-neutral-800',
          progressColor: 'bg-neutral-500',
          icon: <AlertCircle className="w-6 h-6" />,
        };
    }
  };

  const config = getRiskConfig(result.prediction);
  const riskPercentage = (result.risk_score * 100).toFixed(1);
  const confidencePercentage = (result.confidence * 100).toFixed(1);

  return (
    <Card className="animate-fade-in">
      <CardBody>
        <div className={`flex items-center gap-3 mb-6 pb-6 border-b ${config.borderColor}`}>
          <div className={`p-3 rounded-lg ${config.bgColor} ${config.color}`}>
            {config.icon}
          </div>
          <div>
            <h3 className={`text-2xl font-semibold ${config.color}`}>
              {result.prediction} Risk
            </h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              Analysis completed
            </p>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Risk Score
              </span>
              <span className={`text-lg font-semibold ${config.color}`}>
                {riskPercentage}%
              </span>
            </div>
            <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full ${config.progressColor} transition-all duration-1000 ease-out rounded-full`}
                style={{ width: `${riskPercentage}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Confidence Level
              </span>
              <span className="text-lg font-semibold text-neutral-900 dark:text-white">
                {confidencePercentage}%
              </span>
            </div>
            <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-primary-500 transition-all duration-1000 ease-out rounded-full"
                style={{ width: `${confidencePercentage}%` }}
              />
            </div>
          </div>

          <div className={`p-4 rounded-lg ${config.bgColor} border ${config.borderColor}`}>
            <h4 className="text-sm font-semibold text-neutral-900 dark:text-white mb-2">
              Analysis Details
            </h4>
            <p className="text-sm text-neutral-700 dark:text-neutral-300 leading-relaxed">
              {result.explanation}
            </p>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};
