/**
 * Main App component with routing.
 */
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { Dashboard } from '@/pages/Dashboard';
import { DeepfakePage } from '@/pages/DeepfakePage';
import { VoicePage } from '@/pages/VoicePage';
import { DocumentPage } from '@/pages/DocumentPage';
import { EmailPage } from '@/pages/EmailPage';
import { NotFound } from '@/pages/NotFound';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <BrowserRouter>
          <div className="min-h-screen flex flex-col bg-neutral-50 dark:bg-neutral-950 transition-colors">
            <Navbar />
            <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/deepfake" element={<DeepfakePage />} />
                <Route path="/voice" element={<VoicePage />} />
                <Route path="/document" element={<DocumentPage />} />
                <Route path="/email" element={<EmailPage />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </BrowserRouter>
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default App;
