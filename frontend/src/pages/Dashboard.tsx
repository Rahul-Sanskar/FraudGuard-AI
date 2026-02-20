import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, Mic, FileText, Mail, Shield, Activity } from 'lucide-react';
import { Card, CardBody } from '@/components/ui/Card';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const modules = [
    {
      id: 'deepfake',
      title: 'Deepfake Detection',
      description: 'Detect manipulated images and videos using advanced neural networks',
      icon: <Video className="w-8 h-8" />,
      color: 'from-blue-500 to-blue-600',
      path: '/deepfake',
    },
    {
      id: 'voice',
      title: 'Voice Spoof Detection',
      description: 'Identify synthetic and cloned voice recordings with high precision',
      icon: <Mic className="w-8 h-8" />,
      color: 'from-purple-500 to-purple-600',
      path: '/voice',
    },
    {
      id: 'document',
      title: 'Document Verification',
      description: 'Verify document authenticity and detect tampering attempts',
      icon: <FileText className="w-8 h-8" />,
      color: 'from-teal-500 to-teal-600',
      path: '/document',
    },
    {
      id: 'email',
      title: 'Email Fraud Detection',
      description: 'Detect C-suite impersonation and Business Email Compromise using FinBERT',
      icon: <Mail className="w-8 h-8" />,
      color: 'from-red-500 to-red-600',
      path: '/email',
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 p-8 md:p-12 text-white">
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl">
              <Shield className="w-10 h-10" />
            </div>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold">FraudGuard AI</h1>
              <p className="text-primary-100">Enterprise Fraud Detection Platform</p>
            </div>
          </div>
          <p className="text-lg text-primary-50 max-w-2xl">
            Protect your organization with AI-powered detection across multiple fraud vectors. 
            Advanced machine learning models provide real-time analysis and risk assessment.
          </p>
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800">
          <CardBody>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-500 text-white rounded-lg">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">System Status</p>
                <p className="text-2xl font-bold text-neutral-900 dark:text-white">Operational</p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800">
          <CardBody>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-500 text-white rounded-lg">
                <Shield className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Active Modules</p>
                <p className="text-2xl font-bold text-neutral-900 dark:text-white">4</p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      <div>
        <h2 className="text-2xl font-semibold text-neutral-900 dark:text-white mb-6">
          Detection Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {modules.map((module) => (
            <Card
              key={module.id}
              hover
              onClick={() => navigate(module.path)}
              className="group cursor-pointer"
            >
              <CardBody className="space-y-4">
                <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${module.color} flex items-center justify-center text-white group-hover:scale-110 transition-transform duration-300`}>
                  {module.icon}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-neutral-900 dark:text-white mb-2">
                    {module.title}
                  </h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
                    {module.description}
                  </p>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
