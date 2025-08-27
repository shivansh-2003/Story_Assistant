import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, Loader2, RefreshCw } from 'lucide-react';
import { healthCheck } from '@/lib/api';

const HealthCheck = () => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkHealth = async () => {
    setStatus('loading');
    try {
      const response = await healthCheck();
      setStatus('success');
      setMessage(response.message);
      setLastChecked(new Date());
    } catch (error) {
      setStatus('error');
      setMessage(error instanceof Error ? error.message : 'Failed to connect to API');
      setLastChecked(new Date());
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const getStatusIcon = () => {
    switch (status) {
      case 'loading':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getAlertVariant = () => {
    switch (status) {
      case 'loading':
        return 'default';
      case 'success':
        return 'default';
      case 'error':
        return 'destructive';
    }
  };

  return (
    <Alert variant={getAlertVariant()} className="mb-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <AlertDescription>
            <strong>API Status:</strong> {message || 'Checking connection...'}
            {lastChecked && (
              <span className="text-xs text-muted-foreground ml-2">
                (Last checked: {lastChecked.toLocaleTimeString()})
              </span>
            )}
          </AlertDescription>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={checkHealth}
            disabled={status === 'loading'}
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            Check
          </Button>
        </div>
      </div>
    </Alert>
  );
};

export default HealthCheck;
