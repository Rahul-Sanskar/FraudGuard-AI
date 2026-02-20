import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="w-20 h-20 bg-neutral-100 dark:bg-neutral-800 rounded-full flex items-center justify-center mx-auto mb-6">
          <AlertCircle className="w-10 h-10 text-neutral-400 dark:text-neutral-500" />
        </div>
        <h1 className="text-6xl font-bold text-neutral-900 dark:text-white mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-neutral-700 dark:text-neutral-300 mb-2">
          Page Not Found
        </h2>
        <p className="text-neutral-600 dark:text-neutral-400 mb-8 max-w-md mx-auto">
          The page you are looking for does not exist or has been moved.
        </p>
        <Button onClick={() => navigate('/')} variant="primary" size="lg">
          Return to Dashboard
        </Button>
      </div>
    </div>
  );
};
