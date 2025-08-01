import { useLocation } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-atmospheric">
      <div className="text-center space-y-6">
        <div className="text-9xl font-serif font-bold text-primary/20">404</div>
        <h1 className="text-4xl font-serif font-bold text-foreground">Story Not Found</h1>
        <p className="text-xl text-muted-foreground mb-4">
          This page seems to have wandered off into another dimension...
        </p>
        <div className="space-y-4">
          <a 
            href="/" 
            className="inline-flex items-center px-6 py-3 bg-gradient-primary text-primary-foreground rounded-lg hover:shadow-elegant transition-all duration-300 hover:scale-105 font-medium"
          >
            Return to Your Stories
          </a>
          <p className="text-sm text-muted-foreground">
            Or perhaps you'd like to create a new tale instead?
          </p>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
