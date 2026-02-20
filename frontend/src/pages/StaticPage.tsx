/**
 * Static Data page with 4 detection modules.
 */
import React, { useState } from 'react';
import { Video, FileText, Mic, Mail, Upload, AlertCircle } from 'lucide-react';
import { AnalysisResult } from '@/components/AnalysisResult';
import { analyzeImage, analyzeVideo, analyzeAudio, analyzeDocument, analyzeEmail } from '@/services/api';
import { AnalysisResponse } from '@/types';

type DetectionModule = 'deepfake' | 'document' | 'voice' | 'email';

export const StaticPage: React.FC = () => {
  const [activeModule, setActiveModule] = useState<DetectionModule>('deepfake');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [emailText, setEmailText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setResult(null);
    setError(null);

    // Generate preview
    if (selectedFile.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result as string);
      reader.readAsDataURL(selectedFile);
    } else if (selectedFile.type.startsWith('video/')) {
      const url = URL.createObjectURL(selectedFile);
      setPreview(url);
    } else if (selectedFile.type.startsWith('audio/')) {
      const url = URL.createObjectURL(selectedFile);
      setPreview(url);
    } else {
      setPreview(null);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let response: AnalysisResponse;

      if (activeModule === 'email') {
        if (!emailText.trim()) {
          throw new Error('Please enter email text');
        }
        response = await analyzeEmail(emailText);
      } else {
        if (!file) {
          throw new Error('Please select a file');
        }

        switch (activeModule) {
          case 'deepfake':
            if (file.type.startsWith('image/')) {
              response = await analyzeImage(file, false);  // is_live=false for static uploads
            } else if (file.type.startsWith('video/')) {
              response = await analyzeVideo(file);
            } else {
              throw new Error('Please select an image or video file');
            }
            break;
          case 'document':
            response = await analyzeDocument(file);
            break;
          case 'voice':
            response = await analyzeAudio(file);
            break;
          default:
            throw new Error('Invalid module');
        }
      }

      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const modules = [
    {
      id: 'deepfake' as DetectionModule,
      icon: <Video className="w-6 h-6" />,
      title: 'Deepfake Detection',
      description: 'Upload image or video',
      accept: 'image/*,video/*',
      color: 'blue',
    },
    {
      id: 'document' as DetectionModule,
      icon: <FileText className="w-6 h-6" />,
      title: 'Document Verification',
      description: 'Upload image or PDF',
      accept: 'image/*,application/pdf',
      color: 'green',
    },
    {
      id: 'voice' as DetectionModule,
      icon: <Mic className="w-6 h-6" />,
      title: 'Voice Analysis',
      description: 'Upload audio file',
      accept: 'audio/*',
      color: 'purple',
    },
    {
      id: 'email' as DetectionModule,
      icon: <Mail className="w-6 h-6" />,
      title: 'Email Fraud Detection',
      description: 'Paste email text',
      accept: '',
      color: 'red',
    },
  ];

  const activeModuleData = modules.find((m) => m.id === activeModule)!;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-2">Static Data Analysis</h1>
        <p className="text-gray-600">Upload files for fraud detection analysis</p>
      </div>

      {/* Module Selection */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {modules.map((module) => (
          <button
            key={module.id}
            onClick={() => {
              setActiveModule(module.id);
              setFile(null);
              setPreview(null);
              setResult(null);
              setError(null);
              setEmailText('');
            }}
            className={`p-4 rounded-lg border-2 transition-all ${
              activeModule === module.id
                ? `border-${module.color}-500 bg-${module.color}-50`
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className={`flex items-center justify-center w-12 h-12 rounded-lg bg-${module.color}-500 text-white mx-auto mb-2`}>
              {module.icon}
            </div>
            <h3 className="font-semibold text-sm text-center">{module.title}</h3>
            <p className="text-xs text-gray-600 text-center mt-1">{module.description}</p>
          </button>
        ))}
      </div>

      {/* Upload/Input Area */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">{activeModuleData.title}</h2>

        {activeModule === 'email' ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Text
            </label>
            <textarea
              value={emailText}
              onChange={(e) => setEmailText(e.target.value)}
              className="w-full h-48 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Paste email content here..."
            />
          </div>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload File
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
              <input
                type="file"
                accept={activeModuleData.accept}
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">
                  {file ? file.name : 'Click to upload or drag and drop'}
                </p>
                <p className="text-sm text-gray-500">{activeModuleData.description}</p>
              </label>
            </div>

            {/* Preview */}
            {preview && (
              <div className="mt-4">
                <h3 className="font-semibold mb-2">Preview:</h3>
                {file?.type.startsWith('image/') && (
                  <img src={preview} alt="Preview" className="max-w-md max-h-64 rounded-lg mx-auto" />
                )}
                {file?.type.startsWith('video/') && (
                  <video src={preview} controls className="max-w-md max-h-64 rounded-lg mx-auto" />
                )}
                {file?.type.startsWith('audio/') && (
                  <audio src={preview} controls className="w-full max-w-md mx-auto" />
                )}
              </div>
            )}
          </div>
        )}

        {/* Analyze Button */}
        <button
          onClick={handleAnalyze}
          disabled={loading || (activeModule !== 'email' && !file) || (activeModule === 'email' && !emailText.trim())}
          className="mt-6 w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>

        {/* Error */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <AnalysisResult result={result} />
        </div>
      )}
    </div>
  );
};
