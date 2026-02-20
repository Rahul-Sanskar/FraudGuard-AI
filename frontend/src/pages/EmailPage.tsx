import React, { useState } from 'react';
import { Mail } from 'lucide-react';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ResultPanel } from '@/components/ui/ResultPanel';
import { Loader } from '@/components/ui/Loader';
import { ToastContainer } from '@/components/ui/Toast';
import { useToast } from '@/hooks/useToast';
import { analyzeEmail } from '@/services/api';
import { AnalysisResponse } from '@/types';

export const EmailPage: React.FC = () => {
  const [emailText, setEmailText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const { toasts, showToast, removeToast } = useToast();

  const handleAnalyze = async () => {
    if (!emailText.trim()) {
      showToast('Please enter email text', 'warning');
      return;
    }

    if (emailText.trim().length < 10) {
      showToast('Email text is too short. Please enter at least 10 characters.', 'warning');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await analyzeEmail(emailText);
      setResult(response);
      showToast('Email analysis completed successfully', 'success');
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Analysis failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setEmailText('');
    setResult(null);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <ToastContainer toasts={toasts} onClose={removeToast} />
      
      <div className="flex items-center gap-3">
        <div className="p-3 bg-gradient-to-br from-red-500 to-red-600 text-white rounded-xl">
          <Mail className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">
            Email Fraud Detection
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Detect C-suite impersonation and Business Email Compromise (BEC)
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-neutral-900 dark:text-white">
                Email Content
              </h2>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Paste email text below
                  </label>
                  <textarea
                    value={emailText}
                    onChange={(e) => setEmailText(e.target.value)}
                    placeholder="Paste the email content here for analysis..."
                    disabled={loading}
                    rows={12}
                    className="w-full px-4 py-3 border border-neutral-300 dark:border-neutral-700 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                  />
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-2">
                    Minimum 10 characters required
                  </p>
                </div>

                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2">
                    What we detect:
                  </h3>
                  <ul className="text-xs text-blue-800 dark:text-blue-300 space-y-1">
                    <li>• C-suite impersonation (CEO, CFO, executives)</li>
                    <li>• Urgent payment requests</li>
                    <li>• Wire transfer scams</li>
                    <li>• Business Email Compromise (BEC)</li>
                    <li>• Suspicious authority claims</li>
                    <li>• Pressure tactics and urgency</li>
                  </ul>
                </div>
              </div>
            </CardBody>
          </Card>

          <div className="flex gap-3">
            {!loading && !result && (
              <Button
                variant="primary"
                size="lg"
                onClick={handleAnalyze}
                disabled={!emailText.trim()}
                className="flex-1"
              >
                Analyze Email
              </Button>
            )}
            {emailText && (
              <Button
                variant="secondary"
                size="lg"
                onClick={handleClear}
                disabled={loading}
              >
                Clear
              </Button>
            )}
          </div>
        </div>

        <div>
          {loading && (
            <Card>
              <CardBody className="py-12">
                <Loader size="lg" text="Analyzing email with FinBERT..." />
              </CardBody>
            </Card>
          )}

          {result && !loading && <ResultPanel result={result} />}

          {!loading && !result && (
            <Card className="border-dashed">
              <CardBody className="py-12 text-center">
                <Mail className="w-16 h-16 mx-auto mb-4 text-neutral-300 dark:text-neutral-600" />
                <p className="text-neutral-600 dark:text-neutral-400 mb-4">
                  Paste email content and click analyze to detect fraud
                </p>
                <div className="text-left max-w-md mx-auto bg-neutral-50 dark:bg-neutral-800 rounded-lg p-4">
                  <p className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 mb-2">
                    Example indicators:
                  </p>
                  <ul className="text-xs text-neutral-600 dark:text-neutral-400 space-y-1">
                    <li>• Requests for urgent wire transfers</li>
                    <li>• Claims to be CEO/CFO/Executive</li>
                    <li>• Unusual payment instructions</li>
                    <li>• Pressure to act immediately</li>
                    <li>• Requests for confidentiality</li>
                  </ul>
                </div>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
