import React, { useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { healthCheck } from '../lib/api';

const HealthCheck = () => {
  const [status, setStatus] = useState<'idle' | 'checking' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_URL || 'https://story-assistant.onrender.com');

  const checkHealth = async () => {
    setStatus('checking');
    setMessage('');
    setError('');
    
    try {
      console.log('Checking API health...');
      console.log('API URL:', apiUrl);
      console.log('Environment variables:', {
        VITE_API_URL: import.meta.env.VITE_API_URL,
        NODE_ENV: import.meta.env.NODE_ENV,
        MODE: import.meta.env.MODE
      });
      
      const result = await healthCheck();
      setStatus('success');
      setMessage(result.message);
    } catch (err: any) {
      setStatus('error');
      setError(err.message || 'Unknown error occurred');
      console.error('Health check failed:', err);
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'checking':
        return '⏳';
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '🔍';
    }
  };

  const getAlertVariant = () => {
    switch (status) {
      case 'success':
        return 'default';
      case 'error':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {getStatusIcon()} API Health Check
        </CardTitle>
        <CardDescription>
          Test connection to the Story Assistant backend
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="text-sm font-medium">API URL:</div>
          <Badge variant="outline" className="font-mono text-xs">
            {apiUrl}
          </Badge>
        </div>
        
        <div className="space-y-2">
          <div className="text-sm font-medium">Environment:</div>
          <div className="text-xs space-y-1">
            <div>NODE_ENV: {import.meta.env.NODE_ENV}</div>
            <div>MODE: {import.meta.env.MODE}</div>
            <div>VITE_API_URL: {import.meta.env.VITE_API_URL || 'Not set'}</div>
          </div>
        </div>

        <Button 
          onClick={checkHealth} 
          disabled={status === 'checking'}
          className="w-full"
        >
          {status === 'checking' ? 'Checking...' : 'Check API Health'}
        </Button>

        {status === 'success' && (
          <Alert variant={getAlertVariant()}>
            <AlertTitle>API is Healthy</AlertTitle>
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )}

        {status === 'error' && (
          <Alert variant={getAlertVariant()}>
            <AlertTitle>API Connection Failed</AlertTitle>
            <AlertDescription>
              {error}
              <div className="mt-2 text-xs">
                <strong>Troubleshooting tips:</strong>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  <li>Check if the API server is running</li>
                  <li>Verify the API URL is correct</li>
                  <li>Check CORS configuration on the server</li>
                  <li>Ensure environment variables are set in Vercel</li>
                </ul>
              </div>
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default HealthCheck;
