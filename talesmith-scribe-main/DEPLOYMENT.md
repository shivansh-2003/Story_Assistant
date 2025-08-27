# Vercel Deployment Guide

## API Connectivity Issue Fix

This guide will help you resolve the API connectivity issues when deploying to Vercel.

### Problem
The application works locally but fails to connect to the API when deployed to Vercel due to environment variable configuration issues.

### Solution Steps

#### 1. Set Environment Variables in Vercel

1. Go to your Vercel dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add the following environment variable:

```
Name: VITE_API_URL
Value: https://story-assistant.onrender.com
Environment: Production, Preview, Development
```

#### 2. Verify API Server CORS Configuration

Ensure your backend API server (at `https://story-assistant.onrender.com`) has CORS configured to accept requests from your Vercel domain:

```python
# In your FastAPI backend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:8080",  # Local development
        "https://your-vercel-domain.vercel.app",  # Your Vercel domain
        "https://*.vercel.app",  # All Vercel domains (optional)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3. Redeploy Your Application

After setting the environment variables:

1. Go to your Vercel project dashboard
2. Click **Deployments**
3. Click **Redeploy** on your latest deployment

#### 4. Test the Connection

1. Open your deployed application
2. Navigate to the Health Check component (if available)
3. Click "Check API Health" to verify the connection

### Debugging

If you're still having issues:

1. **Check Browser Console**: Open developer tools and look for error messages
2. **Verify Environment Variables**: The Health Check component will show the current API URL
3. **Test API Directly**: Try accessing `https://story-assistant.onrender.com/health/` directly in your browser
4. **Check Network Tab**: Look for failed requests in the Network tab of developer tools

### Common Issues

1. **CORS Errors**: The API server doesn't allow requests from your Vercel domain
2. **Environment Variables Not Set**: VITE_API_URL is not configured in Vercel
3. **API Server Down**: The backend server is not running or accessible
4. **Wrong API URL**: The fallback URL is incorrect

### Files Modified

- `src/lib/api.ts`: Added better error handling and debugging
- `vite.config.ts`: Updated environment variable handling
- `vercel.json`: Added Vercel configuration
- `src/components/HealthCheck.tsx`: Enhanced debugging component

### Alternative Solutions

If the above doesn't work, consider:

1. **Using a Different API URL**: Update the fallback URL in `src/lib/api.ts`
2. **Adding API Routes**: Create API routes in Vercel to proxy requests
3. **Using a Different Backend**: Deploy your backend to a different service

### Support

If you continue to have issues, check:
- Vercel deployment logs
- Browser console errors
- Network request failures
- API server logs
noteId: "0db15c70831311f0807d8b43481c9e63"
tags: []

---

