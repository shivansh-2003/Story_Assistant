// Utility functions to test API connection from browser console

export const testApiConnection = async () => {
  const baseUrl = 'https://story-assistant.onrender.com';
  
  try {
    console.log('🔍 Testing API connection...');
    
    // Test 1: Health check
    console.log('1. Testing health endpoint...');
    const healthResponse = await fetch(`${baseUrl}/health/`);
    const healthData = await healthResponse.json();
    console.log('✅ Health check:', healthData);
    
    // Test 2: Characters endpoint
    console.log('2. Testing characters endpoint...');
    const charactersResponse = await fetch(`${baseUrl}/characters/`);
    const charactersData = await charactersResponse.json();
    console.log('✅ Characters:', charactersData);
    
    // Test 3: Stories endpoint  
    console.log('3. Testing stories endpoint...');
    const storiesResponse = await fetch(`${baseUrl}/stories/`);
    const storiesData = await storiesResponse.json();
    console.log('✅ Stories:', storiesData);
    
    console.log('🎉 All API tests passed!');
    return {
      success: true,
      health: healthData,
      characters: charactersData,
      stories: storiesData
    };
    
  } catch (error) {
    console.error('❌ API test failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
};

// Make it available globally for browser console testing
if (typeof window !== 'undefined') {
  (window as any).testApiConnection = testApiConnection;
}

export default testApiConnection;
