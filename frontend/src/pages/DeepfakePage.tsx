import React, { useState, useCallback } from 'react';
import { Video, Camera, Upload as UploadIcon } from 'lucide-react';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { UploadZone } from '@/components/ui/UploadZone';
import { WebcamCapture } from '@/components/capture/WebcamCapture';
import { ResultPanel } from '@/components/ui/ResultPanel';
import { Loader } from '@/components/ui/Loader';
import { ToastContainer } from '@/components/ui/Toast';
import { useToast } from '@/hooks/useToast';
import { analyzeImage, analyzeVideo } from '@/services/api';
import { AnalysisResponse } from '@/types';

type AnalysisMode = 'upload' | 'webcam';

export const DeepfakePage: React.FC = () => {
  const [mode, setMode] = useState<AnalysisMode>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [isFromWebcam, setIsFromWebcam] = useState(false);
  const { toasts, showToast, removeToast } = useToast();

  const handleFileSelect = useCallback((selectedFile: File) => {
    setFile(selectedFile);
    setResult(null);
    setIsFromWebcam(false); // Mark as uploaded file
    
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(selectedFile);
  }, []);

  const handleWebcamCapture = useCallback((blob: Blob) => {
    const capturedFile = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
    setFile(capturedFile);
    setResult(null);
    setIsFromWebcam(true); // Mark as webcam capture
    
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(capturedFile);
    
    setMode('upload');
  }, []);

  const handleClearPreview = useCallback(() => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setIsFromWebcam(false);
  }, []);

  const handleAnalyze = async () => {
    if (!file) {
      showToast('Please select a file first', 'warning');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const isVideo = file.type.startsWith('video/');
      const response = isVideo 
        ? await analyzeVideo(file)
        : await analyzeImage(file, isFromWebcam); // Pass isFromWebcam flag
      
      setResult(response);
      showToast('Analysis completed successfully', 'success');
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Analysis failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <ToastContainer toasts={toasts} onClose={removeToast} />
      
      <div className="flex items-center gap-3">
        <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl">
          <Video className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">
            Deepfake Detection
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Analyze images and videos for manipulation
          </p>
        </div>
      </div>

      <div className="flex gap-3">
        <Button
          variant={mode === 'upload' ? 'primary' : 'secondary'}
          onClick={() => setMode('upload')}
          icon={<UploadIcon className="w-4 h-4" />}
        >
          Upload File
        </Button>
        <Button
          variant={mode === 'webcam' ? 'primary' : 'secondary'}
          onClick={() => setMode('webcam')}
          icon={<Camera className="w-4 h-4" />}
        >
          Use Webcam
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-neutral-900 dark:text-white">
                {mode === 'upload' ? 'Upload Media' : 'Capture from Webcam'}
              </h2>
            </CardHeader>
            <CardBody>
              {mode === 'upload' ? (
                <UploadZone
                  onFileSelect={handleFileSelect}
                  accept="image/*,video/*"
                  preview={preview}
                  onClearPreview={handleClearPreview}
                  disabled={loading}
                />
              ) : (
                <WebcamCapture onCapture={handleWebcamCapture} />
              )}
            </CardBody>
          </Card>

          {file && !loading && !result && mode === 'upload' && (
            <>
              {isFromWebcam && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                    <p className="text-sm font-medium text-blue-900 dark:text-blue-200">
                      Anti-Spoofing Active
                    </p>
                  </div>
                  <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                    This image will be checked for screen replay attacks (phone displays, printed photos)
                  </p>
                </div>
              )}
              <Button
                variant="primary"
                size="lg"
                onClick={handleAnalyze}
                className="w-full"
              >
                Analyze for Deepfakes
              </Button>
            </>
          )}
        </div>

        <div>
          {loading && (
            <Card>
              <CardBody className="py-12">
                <Loader size="lg" text="Analyzing media..." />
              </CardBody>
            </Card>
          )}

          {result && !loading && <ResultPanel result={result} />}

          {!loading && !result && (
            <Card className="border-dashed">
              <CardBody className="py-12 text-center">
                <Video className="w-16 h-16 mx-auto mb-4 text-neutral-300 dark:text-neutral-600" />
                <p className="text-neutral-600 dark:text-neutral-400">
                  {mode === 'upload' 
                    ? 'Upload a file and click analyze to see results'
                    : 'Capture an image from your webcam to analyze'}
                </p>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
