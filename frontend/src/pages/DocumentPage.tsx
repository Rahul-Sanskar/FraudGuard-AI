import React, { useState, useCallback } from 'react';
import { FileText } from 'lucide-react';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { UploadZone } from '@/components/ui/UploadZone';
import { ResultPanel } from '@/components/ui/ResultPanel';
import { Loader } from '@/components/ui/Loader';
import { ToastContainer } from '@/components/ui/Toast';
import { useToast } from '@/hooks/useToast';
import { analyzeDocument } from '@/services/api';
import { AnalysisResponse } from '@/types';

export const DocumentPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const { toasts, showToast, removeToast } = useToast();

  const handleFileSelect = useCallback((selectedFile: File) => {
    setFile(selectedFile);
    setResult(null);
    
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(selectedFile);
  }, []);

  const handleClearPreview = useCallback(() => {
    setFile(null);
    setPreview(null);
    setResult(null);
  }, []);

  const handleAnalyze = async () => {
    if (!file) {
      showToast('Please select a document first', 'warning');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await analyzeDocument(file);
      setResult(response);
      showToast('Document analysis completed successfully', 'success');
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
        <div className="p-3 bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-xl">
          <FileText className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">
            Document Verification
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Verify document authenticity and detect tampering
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-neutral-900 dark:text-white">
                Upload Document
              </h2>
            </CardHeader>
            <CardBody>
              <UploadZone
                onFileSelect={handleFileSelect}
                accept="image/*,.pdf"
                preview={preview}
                onClearPreview={handleClearPreview}
                disabled={loading}
              />
            </CardBody>
          </Card>

          {file && !loading && !result && (
            <Button
              variant="primary"
              size="lg"
              onClick={handleAnalyze}
              className="w-full"
            >
              Verify Document
            </Button>
          )}
        </div>

        <div>
          {loading && (
            <Card>
              <CardBody className="py-12">
                <Loader size="lg" text="Analyzing document..." />
              </CardBody>
            </Card>
          )}

          {result && !loading && <ResultPanel result={result} />}

          {!loading && !result && (
            <Card className="border-dashed">
              <CardBody className="py-12 text-center">
                <FileText className="w-16 h-16 mx-auto mb-4 text-neutral-300 dark:text-neutral-600" />
                <p className="text-neutral-600 dark:text-neutral-400">
                  Upload a document and click verify to see results
                </p>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
