/**
 * Dashboard page with analytics overview.
 */
import React from 'react';
import { Shield, FileText, Video, Mic, Mail } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const features = [
    {
      icon: <Video className="w-8 h-8" />,
      title: 'Deepfake Detection',
      description: 'Analyze images and videos for AI-generated content',
      link: '/upload',
      color: 'bg-blue-500',
    },
    {
      icon: <Mic className="w-8 h-8" />,
      title: 'Voice Analysis',
      description: 'Detect voice spoofing and synthetic audio',
      link: '/live',
      color: 'bg-purple-500',
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: 'Document Verification',
      description: 'Check documents for tampering and forgery',
      link: '/upload',
      color: 'bg-green-500',
    },
    {
      icon: <Mail className="w-8 h-8" />,
      title: 'Email Fraud Detection',
      description: 'Identify C-suite impersonation attempts',
      link: '/upload',
      color: 'bg-red-500',
    },
  ];

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white">
        <div className="flex items-center gap-4 mb-4">
          <Shield className="w-12 h-12" />
          <div>
            <h1 className="text-3xl font-bold">FraudGuard AI</h1>
            <p className="text-blue-100">Advanced Fraud Detection Platform</p>
          </div>
        </div>
        <p className="text-lg">
          Protect your organization from deepfakes, voice spoofing, document tampering, and impersonation fraud.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature, index) => (
          <Link
            key={index}
            to={feature.link}
            className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200"
          >
            <div className={`inline-flex items-center justify-center w-16 h-16 rounded-lg ${feature.color} text-white mb-4`}>
              {feature.icon}
            </div>
            <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
            <p className="text-gray-600">{feature.description}</p>
          </Link>
        ))}
      </div>

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
