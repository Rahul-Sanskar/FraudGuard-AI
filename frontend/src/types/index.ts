/**
 * Type definitions for the FraudGuard platform.
 */

export interface AnalysisResponse {
  risk_score: number;
  prediction: 'Low' | 'Medium' | 'High';
  confidence: number;
  explanation: string;
}

export interface AnalysisLog {
  id: number;
  input_type: string;
  risk_score: number;
  prediction: string;
  confidence: number;
  created_at: string;
}

export type AnalysisType = 'image' | 'video' | 'audio' | 'document' | 'email';
