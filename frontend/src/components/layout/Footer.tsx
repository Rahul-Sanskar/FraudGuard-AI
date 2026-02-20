import React from 'react';
import { Shield } from 'lucide-react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white dark:bg-neutral-900 border-t border-neutral-200 dark:border-neutral-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Shield className="w-6 h-6 text-primary-600" />
              <span className="font-semibold text-neutral-900 dark:text-white">FraudGuard AI</span>
            </div>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              Enterprise-grade fraud detection powered by advanced AI technology.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-neutral-900 dark:text-white mb-3">Detection Services</h3>
            <ul className="space-y-2 text-sm text-neutral-600 dark:text-neutral-400">
              <li>Deepfake Detection</li>
              <li>Voice Spoof Detection</li>
              <li>Document Verification</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-neutral-900 dark:text-white mb-3">Resources</h3>
            <ul className="space-y-2 text-sm text-neutral-600 dark:text-neutral-400">
              <li>Documentation</li>
              <li>API Reference</li>
              <li>Support</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-neutral-200 dark:border-neutral-800 text-center text-sm text-neutral-600 dark:text-neutral-400">
          {currentYear} FraudGuard AI. All rights reserved.
        </div>
      </div>
    </footer>
  );
};
