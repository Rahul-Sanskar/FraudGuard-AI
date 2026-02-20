/**
 * Homepage with Static Data and Live Data mode selection.
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Upload, Radio, FileText, Video, Mic, Mail, Camera } from 'lucide-react';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white">
        <div className="flex items-center gap-4 mb-4">
          <Shield className="w-12 h-12" />
          <div>
            <h1 className="text-3xl font-bold">FraudGuard AI</h1>
            <p className="text-blue-100">Advanced Multimodal Fraud Detection Platform</p>
          </div>
        </div>
        <p className="text-lg">
          Protect your organization from deepfakes, voice spoofing, document tampering, and impersonation fraud.
        </p>
      </div>

      {/* Main Mode Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Static Data Mode */}
        <div
          onClick={() => navigate('/static')}
          className="bg-white rounded-lg shadow-lg p-8 border-2 border-gray-200 hover:border-blue-500 hover:shadow-xl transition-all cursor-pointer group"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="bg-blue-500 text-white p-4 rounded-lg group-hover:scale-110 transition-transform">
              <Upload className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Static Data</h2>
              <p className="text-gray-600">Upload files for analysis</p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-3 text-gray-700">
              <Video className="w-5 h-5 text-blue-500" />
              <span>Deepfake Detection (Image & Video)</span>
            </div>
            <div className="flex items-center gap-3 text-gray-700">
              <FileText className="w-5 h-5 text-green-500" />
              <span>Document Verification</span>
            </div>
            <div className="flex items-center gap-3 text-gray-700">
              <Mic className="w-5 h-5 text-purple-500" />
              <span>Voice Analysis (Audio Files)</span>
            </div>
            <div className="flex items-center gap-3 text-gray-700">
              <Mail className="w-5 h-5 text-red-500" />
              <span>Email Fraud Detection</span>
            </div>
          </div>

          <div className="mt-6 text-center">
            <button className="bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors">
              Upload Files
            </button>
          </div>
        </div>

        {/* Live Data Mode */}
        <div
          onClick={() => navigate('/live')}
          className="bg-white rounded-lg shadow-lg p-8 border-2 border-gray-200 hover:border-purple-500 hover:shadow-xl transition-all cursor-pointer group"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="bg-purple-500 text-white p-4 rounded-lg group-hover:scale-110 transition-transform">
              <Radio className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Live Data</h2>
              <p className="text-gray-600">Real-time capture & analysis</p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-3 text-gray-700">
              <Camera className="w-5 h-5 text-blue-500" />
              <span>Live Webcam Detection</span>
            </div>
            <div className="flex items-center gap-3 text-gray-700">
              <Mic className="w-5 h-5 text-purple-500" />
              <span>Live Voice Recording</span>
            </div>
            <div className="flex items-center gap-3 text-gray-700">
              <Radio className="w-5 h-5 text-green-500" />
              <span>Real-time Analysis</span>
            </div>
          </div>

          <div className="mt-6 text-center">
            <button className="bg-purple-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-600 transition-colors">
              Start Live Mode
            </button>
          </div>
        </div>
      </div>

      {/* Platform Statistics */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-2xl font-bold mb-4">Platform Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-4xl font-bold text-blue-600">99.2%</p>
            <p className="text-gray-600 mt-2">Detection Accuracy</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-green-600">&lt;2s</p>
            <p className="text-gray-600 mt-2">Average Analysis Time</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-purple-600">24/7</p>
            <p className="text-gray-600 mt-2">Real-time Monitoring</p>
          </div>
        </div>
      </div>
    </div>
  );
};
