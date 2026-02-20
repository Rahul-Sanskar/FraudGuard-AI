/**
 * Upload page for file-based analysis.
 */
import React, { useState } from 'react';
import { FileUpload } from '@/components/FileUpload';
import { AnalysisResult } from '@/components/AnalysisResult';
import { analyzeImage, analyzeVideo, analyzeAudio, analyzeDocument, analyzeEmail } from '@/services/api';
import { AnalysisResponse } from '@/types';
import { Loader2 } from 'lucide-react';

type AnalysisMode = 'image' | 'video' | 'audio' | 'document' | 'email';

export const UploadPage: React.FC = () => {
  const [mode, setMode] = useState<AnalysisMode>('image');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [emailText, setEmailText] = useState('');

  const handleFileAnalysis = async (file: File) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let response: AnalysisResponse;

      switch (mode) {
        case 'image':
          response = await analyzeImage(file);
          break;
        case 'video':
          response = await analyzeVideo(file);
          break;
        case 'audio':
          response = await analyzeAudio(file);
          break;
        case 'document':
          response = await analyzeDocument(file);
          break;
        default:
          throw new Error('Invalid analysis mode');
      }

      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleEmailAnalysis = async () => {
    if (!emailText.trim()) {
      setError('Please enter email text');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeEmail(emailText);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const getAcceptType = () => {
    switch (mode) {
      case 'image':
        return 'image/*';
      case 'video':
        return 'video/*';
      case 'audio':
        return 'audio/*';
      case 'document':
        return 'application/pdf,image/*';
      default:
        return '*';
    }
  };

  const getLabel = () => {
    switch (mode) {
      case 'image':
        return 'Upload Image for Deepfake Detection';
      case 'video':
        return 'Upload Video for Deepfake Detection';
      case 'audio':
        return 'Upload Audio for Voice Spoofing Detection';
      case 'document':
        return 'Upload Document for Tampering Detection';
      default:
        return 'Upload File';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Analysis Upload</h1>
        <p className="text-gray-600">Upload files or text for fraud detection analysis</p>
      </div>

      <div className="flex gap-2 flex-wrap">
        {(['image', 'video', 'audio', 'document', 'email'] as AnalysisMode[]).map((m) => (
          <button
            key={m}
            onClick={() => {
              setMode(m);
              setResult(null);
              setError(null);
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              mode === m
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        {mode === 'email' ? (
          <div className="space-y-4">
            <textarea
              value={emailText}
              onChange={(e) => setEmailText(e.target.value)}
              placeholder="Paste email content here..."
              className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              onClick={handleEmailAnalysis}
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading && <Loader2 className="w-5 h-5 animate-spin" />}
              {loading ? 'Analyzing...' : 'Analyze Email'}
            </button>
          </div>
        ) : (
          <FileUpload
            onFileSelect={handleFileAnalysis}
            accept={getAcceptType()}
            label={getLabel()}
            disabled={loading}
          />
        )}

        {loading && (
          <div className="mt-6 flex items-center justify-center gap-3 text-blue-600">
            <Loader2 className="w-6 h-6 animate-spin" />
            <p className="font-medium">Analyzing...</p>
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-6">
            <AnalysisResult result={result} />
          </div>
        )}
      </div>
    </div>
  );
};
