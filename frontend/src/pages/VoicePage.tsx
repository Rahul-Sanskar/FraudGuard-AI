import React, { useState, useCallback } from 'react';
import { Mic, Upload as UploadIcon } from 'lucide-react';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { UploadZone } from '@/components/ui/UploadZone';
import { AudioRecorder } from '@/components/capture/AudioRecorder';
import { ResultPanel } from '@/components/ui/ResultPanel';
import { Loader } from '@/components/ui/Loader';
import { ToastContainer } from '@/components/ui/Toast';
import { useToast } from '@/hooks/useToast';
import { analyzeAudio } from '@/services/api';
import { AnalysisResponse } from '@/types';

type AnalysisMode = 'upload' | 'record';

export const VoicePage: React.FC = () => {
  const [mode, setMode] = useState<AnalysisMode>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const { toasts, showToast, removeToast } = useToast();

  const handleFileSelect = useCallback((selectedFile: File) => {
    setFile(selectedFile);
    setResult(null);
    setPreview('audio-file');
  }, []);

  const handleAudioCapture = useCallback((blob: Blob) => {
    const recordedFile = new File([blob], 'recording.webm', { type: 'audio/webm' });
    setFile(recordedFile);
    setResult(null);
    setPreview('audio-file');
    setMode('upload');
  }, []);

  const handleClearPreview = useCallback(() => {
    setFile(null);
    setPreview(null);
    setResult(null);
  }, []);

  const handleAnalyze = async () => {
    if (!file) {
      showToast('Please select an audio file first', 'warning');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await analyzeAudio(file);
      setResult(response);
      showToast('Voice analysis completed successfully', 'success');
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
        <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl">
          <Mic className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">
            Voice Spoof Detection
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Detect synthetic and cloned voice recordings
          </p>
        </div>
      </div>

      <div className="flex gap-3">
        <Button
          variant={mode === 'upload' ? 'primary' : 'secondary'}
          onClick={() => setMode('upload')}
          icon={<UploadIcon className="w-4 h-4" />}
        >
          Upload Audio
        </Button>
        <Button
          variant={mode === 'record' ? 'primary' : 'secondary'}
          onClick={() => setMode('record')}
          icon={<Mic className="w-4 h-4" />}
        >
          Record Audio
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-neutral-900 dark:text-white">
                {mode === 'upload' ? 'Upload Audio File' : 'Record Audio'}
              </h2>
            </CardHeader>
            <CardBody>
              {mode === 'upload' ? (
                <UploadZone
                  onFileSelect={handleFileSelect}
                  accept="audio/*,.mp3,.wav,.m4a,.ogg,.webm"
                  preview={preview}
                  onClearPreview={handleClearPreview}
                  disabled={loading}
                />
              ) : (
                <AudioRecorder onCapture={handleAudioCapture} />
              )}
            </CardBody>
          </Card>

          {file && !loading && !result && mode === 'upload' && (
            <Button
              variant="primary"
              size="lg"
              onClick={handleAnalyze}
              className="w-full"
            >
              Analyze Voice
            </Button>
          )}
        </div>

        <div>
          {loading && (
            <Card>
              <CardBody className="py-12">
                <Loader size="lg" text="Analyzing voice patterns..." />
              </CardBody>
            </Card>
          )}

          {result && !loading && <ResultPanel result={result} />}

          {!loading && !result && (
            <Card className="border-dashed">
              <CardBody className="py-12 text-center">
                <Mic className="w-16 h-16 mx-auto mb-4 text-neutral-300 dark:text-neutral-600" />
                <p className="text-neutral-600 dark:text-neutral-400">
                  {mode === 'upload'
                    ? 'Upload an audio file and click analyze to see results'
                    : 'Record audio from your microphone to analyze'}
                </p>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
