import React, { useState, useEffect } from 'react';
import { Brain, MessageSquare, Database, Settings, ExternalLink, RefreshCw } from 'lucide-react';

interface OpenWebUIStatus {
  status: 'loading' | 'connected' | 'error';
  url?: string;
  error?: string;
}

const AIInterface: React.FC = () => {
  const [openWebUIStatus, setOpenWebUIStatus] = useState<OpenWebUIStatus>({ status: 'loading' });
  const [showEmbedded, setShowEmbedded] = useState(false);

  const checkOpenWebUIStatus = async () => {
    try {
      const response = await fetch('http://localhost:3000/health', {
        method: 'GET',
        mode: 'cors'
      });
      
      if (response.ok) {
        setOpenWebUIStatus({ 
          status: 'connected', 
          url: 'http://localhost:3000' 
        });
      } else {
        setOpenWebUIStatus({ 
          status: 'error', 
          error: 'Open WebUI is not responding' 
        });
      }
    } catch (error) {
      setOpenWebUIStatus({ 
        status: 'error', 
        error: 'Could not connect to Open WebUI. Make sure it\'s running on localhost:3000' 
      });
    }
  };

  useEffect(() => {
    checkOpenWebUIStatus();
    // Check status every 30 seconds
    const interval = setInterval(checkOpenWebUIStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleOpenInNewTab = () => {
    window.open('http://localhost:3000', '_blank');
  };

  const handleToggleEmbedded = () => {
    setShowEmbedded(!showEmbedded);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Brain className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Medical Interface</h1>
                <p className="text-gray-600">Enhanced medical AI powered by Open WebUI</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  openWebUIStatus.status === 'connected' ? 'bg-green-500' : 
                  openWebUIStatus.status === 'error' ? 'bg-red-500' : 'bg-yellow-500'
                }`} />
                <span className="text-sm text-gray-600">
                  {openWebUIStatus.status === 'connected' ? 'Open WebUI Connected' :
                   openWebUIStatus.status === 'error' ? 'Open WebUI Disconnected' : 'Checking...'}
                </span>
              </div>
              
              <button
                onClick={checkOpenWebUIStatus}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                title="Refresh status"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Status and Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Medical Assistant Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <MessageSquare className="h-6 w-6 text-green-600" />
              <h3 className="text-lg font-semibold">Medical Assistant</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Your existing PubMed-powered medical research assistant
            </p>
            <a
              href="/chat"
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <MessageSquare className="h-4 w-4 mr-2" />
              Open Chat
            </a>
          </div>

          {/* Open WebUI Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Brain className="h-6 w-6 text-blue-600" />
              <h3 className="text-lg font-semibold">Open WebUI</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Advanced AI interface with multiple model support
            </p>
            <div className="space-y-2">
              <button
                onClick={handleOpenInNewTab}
                disabled={openWebUIStatus.status !== 'connected'}
                className="w-full inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Open in New Tab
              </button>
              <button
                onClick={handleToggleEmbedded}
                disabled={openWebUIStatus.status !== 'connected'}
                className="w-full inline-flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <Settings className="h-4 w-4 mr-2" />
                {showEmbedded ? 'Hide' : 'Show'} Embedded
              </button>
            </div>
          </div>

          {/* Integration Status Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Database className="h-6 w-6 text-purple-600" />
              <h3 className="text-lg font-semibold">Integration</h3>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>PubMed API:</span>
                <span className="text-green-600">Connected</span>
              </div>
              <div className="flex justify-between">
                <span>Medical Models:</span>
                <span className="text-green-600">Available</span>
              </div>
              <div className="flex justify-between">
                <span>Open WebUI:</span>
                <span className={openWebUIStatus.status === 'connected' ? 'text-green-600' : 'text-red-600'}>
                  {openWebUIStatus.status === 'connected' ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {openWebUIStatus.status === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <h4 className="text-red-800 font-medium">Connection Error</h4>
            </div>
            <p className="text-red-700 mt-2">{openWebUIStatus.error}</p>
            <div className="mt-3 text-sm text-red-600">
              <p>To fix this:</p>
              <ol className="list-decimal list-inside mt-1 space-y-1">
                <li>Make sure Docker is running</li>
                <li>Run: <code className="bg-red-100 px-1 rounded">./start-medical-ai.sh</code></li>
                <li>Wait for Open WebUI to start</li>
                <li>Click the refresh button above</li>
              </ol>
            </div>
          </div>
        )}

        {/* Embedded Open WebUI */}
        {showEmbedded && openWebUIStatus.status === 'connected' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Open WebUI (Embedded)</h3>
                <button
                  onClick={handleToggleEmbedded}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="h-[800px]">
              <iframe
                src="http://localhost:3000"
                className="w-full h-full border-0"
                title="Open WebUI"
                sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
              />
            </div>
          </div>
        )}

        {/* Quick Start Guide */}
        {openWebUIStatus.status === 'connected' && !showEmbedded && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Start Guide</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Medical Research</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Use "Medical Assistant" model for PubMed research</li>
                  <li>• Ask evidence-based medical questions</li>
                  <li>• Get citations and literature references</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Advanced AI</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Switch between different AI models</li>
                  <li>• Use streaming responses for real-time interaction</li>
                  <li>• Access medical analysis and case studies</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIInterface;