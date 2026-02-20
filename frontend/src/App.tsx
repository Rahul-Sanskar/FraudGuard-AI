/**
 * Main App component with routing.
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { HomePage } from '@/pages/HomePage';
import { StaticPage } from '@/pages/StaticPage';
import { LivePage } from '@/pages/LivePage';
import { Shield, Home, Upload, Radio } from 'lucide-react';

const Navigation: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-white shadow-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-2 text-xl font-bold text-blue-600">
            <Shield className="w-8 h-8" />
            FraudGuard AI
          </Link>

          <div className="flex gap-1">
            <Link
              to="/"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive('/')
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Home className="w-5 h-5" />
              Home
            </Link>
            <Link
              to="/static"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive('/static')
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Upload className="w-5 h-5" />
              Static
            </Link>
            <Link
              to="/live"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive('/live')
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Radio className="w-5 h-5" />
              Live
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/static" element={<StaticPage />} />
            <Route path="/live" element={<LivePage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
