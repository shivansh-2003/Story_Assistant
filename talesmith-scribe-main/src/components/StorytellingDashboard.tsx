import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sparkles, BookOpen, Users, FileText, Palette, Brain, Wand2, Star, Heart, Sword, Crown } from 'lucide-react';
import HealthCheck from '@/components/HealthCheck';

interface StoryProject {
  id: string;
  title: string;
  genre: string;
  description: string;
  characters: number;
  chapters: number;
  lastUpdated: string;
  status: 'draft' | 'in-progress' | 'completed';
  color: string;
}

const StorytellingDashboard = () => {
  const navigate = useNavigate();
  const recentProjects: StoryProject[] = [
    {
      id: '1',
      title: 'The Crystal Chronicles',
      genre: 'Fantasy',
      description: 'A magical journey through enchanted realms',
      characters: 8,
      chapters: 12,
      lastUpdated: '2 hours ago',
      status: 'in-progress',
      color: 'fantasy'
    },
    {
      id: '2',
      title: 'Midnight Secrets',
      genre: 'Mystery',
      description: 'A detective unravels dark mysteries in the city',
      characters: 5,
      chapters: 8,
      lastUpdated: '1 day ago',
      status: 'draft',
      color: 'mystery'
    },
    {
      id: '3',
      title: 'Hearts Across Time',
      genre: 'Romance',
      description: 'Love transcends time and space',
      characters: 4,
      chapters: 15,
      lastUpdated: '3 days ago',
      status: 'completed',
      color: 'romance'
    }
  ];

  const getGenreIcon = (genre: string) => {
    switch (genre.toLowerCase()) {
      case 'fantasy':
        return <Crown className="w-4 h-4" />;
      case 'mystery':
        return <FileText className="w-4 h-4" />;
      case 'romance':
        return <Heart className="w-4 h-4" />;
      case 'adventure':
        return <Sword className="w-4 h-4" />;
      default:
        return <BookOpen className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-secondary/20 text-secondary border-secondary/30';
      case 'in-progress':
        return 'bg-primary/20 text-primary border-primary/30';
      default:
        return 'bg-muted/50 text-muted-foreground border-border';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-atmospheric">
      {/* Navigation Bar */}
      <nav className="bg-card/30 backdrop-blur-sm border-b border-border/50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-6 h-6 text-primary-glow" />
                <span className="font-serif font-bold text-xl text-foreground">Storyteller</span>
              </div>
              <div className="hidden md:flex items-center space-x-6">
                <Button 
                  variant="ghost" 
                  className="text-foreground hover:text-primary"
                  onClick={() => navigate('/')}
                >
                  Dashboard
                </Button>
                <Button 
                  variant="ghost" 
                  className="text-foreground hover:text-primary"
                  onClick={() => navigate('/create-story')}
                >
                  New Story
                </Button>
                <Button 
                  variant="ghost" 
                  className="text-foreground hover:text-primary"
                  onClick={() => navigate('/characters')}
                >
                  Characters
                </Button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Brain className="w-4 h-4 mr-2" />
                AI Assistant
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-mystical">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative container mx-auto px-4 py-20">
          <div className="text-center space-y-6">
            <div className="animate-fade-in">
              <h1 className="text-6xl font-serif font-bold text-foreground mb-4">
                Interactive Storytelling
              </h1>
              <p className="text-xl text-foreground/80 max-w-2xl mx-auto font-sans">
                Craft immersive stories with AI-powered assistance, dynamic character development, 
                and beautiful custom PDF exports.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in">
              <Button 
                variant="hero" 
                size="hero" 
                className="shadow-elegant hover-scale"
                onClick={() => navigate('/create-story')}
              >
                <Wand2 className="w-5 h-5 mr-2" />
                Create New Story
              </Button>
              <Button variant="outline" size="lg" className="backdrop-blur-sm">
                <Brain className="w-5 h-5 mr-2" />
                AI Writing Assistant
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Dashboard Content */}
      <div className="container mx-auto px-4 py-12">
        {/* API Health Check */}
        <HealthCheck />
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <Card 
            className="bg-card/50 backdrop-blur-sm border-primary/20 hover:shadow-elegant transition-all duration-300 hover:scale-105 cursor-pointer"
            onClick={() => navigate('/create-story')}
          >
            <CardContent className="p-6 text-center">
              <BookOpen className="w-12 h-12 text-primary mx-auto mb-4" />
              <h3 className="font-semibold font-sans">New Story</h3>
              <p className="text-sm text-muted-foreground">Start your next masterpiece</p>
            </CardContent>
          </Card>
          
          <Card 
            className="bg-card/50 backdrop-blur-sm border-secondary/20 hover:shadow-golden transition-all duration-300 hover:scale-105 cursor-pointer"
            onClick={() => navigate('/characters')}
          >
            <CardContent className="p-6 text-center">
              <Users className="w-12 h-12 text-secondary mx-auto mb-4" />
              <h3 className="font-semibold font-sans">Characters</h3>
              <p className="text-sm text-muted-foreground">Develop compelling personas</p>
            </CardContent>
          </Card>
          
          <Card className="bg-card/50 backdrop-blur-sm border-accent/20 hover:shadow-mystical transition-all duration-300 hover:scale-105">
            <CardContent className="p-6 text-center">
              <Palette className="w-12 h-12 text-accent mx-auto mb-4" />
              <h3 className="font-semibold font-sans">PDF Designer</h3>
              <p className="text-sm text-muted-foreground">Beautiful custom exports</p>
            </CardContent>
          </Card>
          
          <Card className="bg-card/50 backdrop-blur-sm border-primary/20 hover:shadow-elegant transition-all duration-300 hover:scale-105">
            <CardContent className="p-6 text-center">
              <Brain className="w-12 h-12 text-primary mx-auto mb-4" />
              <h3 className="font-semibold font-sans">AI Assistant</h3>
              <p className="text-sm text-muted-foreground">Intelligent writing help</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Projects */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-serif font-bold text-foreground">Your Stories</h2>
            <Button variant="secondary" size="lg">
              <BookOpen className="w-4 h-4 mr-2" />
              View All
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 animate-fade-in">
            {recentProjects.map((project, index) => (
              <Card 
                key={project.id} 
                className="bg-card/50 backdrop-blur-sm hover:shadow-elegant transition-all duration-300 hover:scale-105 group cursor-pointer animate-scale-in"
                style={{ animationDelay: `${index * 100}ms` }}
                onClick={() => navigate(`/story/${project.id}`)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      {getGenreIcon(project.genre)}
                      <Badge variant="outline" className={getStatusColor(project.status)}>
                        {project.status}
                      </Badge>
                    </div>
                    <Star className="w-4 h-4 text-muted-foreground group-hover:text-secondary transition-colors" />
                  </div>
                  <CardTitle className="font-serif text-xl group-hover:text-primary transition-colors">
                    {project.title}
                  </CardTitle>
                  <CardDescription className="text-sm">
                    {project.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                    <span className="flex items-center space-x-1">
                      <Users className="w-3 h-3" />
                      <span>{project.characters} characters</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <FileText className="w-3 h-3" />
                      <span>{project.chapters} chapters</span>
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                      Updated {project.lastUpdated}
                    </span>
                    <div className="flex space-x-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => navigate(`/story/${project.id}`)}
                      >
                        Edit
                      </Button>
                      <Button variant="outline" size="sm">
                        Export
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Features Showcase */}
        <div className="mt-16 grid grid-cols-1 lg:grid-cols-3 gap-8">
          <Card className="bg-gradient-fantasy/10 backdrop-blur-sm border-accent/30">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 font-serif">
                <Crown className="w-6 h-6 text-accent" />
                <span>Character Development</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Create rich, multi-dimensional characters with relationship mapping and dynamic growth arcs.
              </p>
              <Button 
                variant="fantasy" 
                size="sm"
                onClick={() => navigate('/characters')}
              >
                Explore Characters
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gradient-adventure/10 backdrop-blur-sm border-secondary/30">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 font-serif">
                <Palette className="w-6 h-6 text-secondary" />
                <span>Custom PDF Design</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Transform your stories into beautifully designed PDFs with professional layouts and typography.
              </p>
              <Button variant="adventure" size="sm">
                Design PDFs
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-gradient-primary/10 backdrop-blur-sm border-primary/30">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 font-serif">
                <Brain className="w-6 h-6 text-primary" />
                <span>AI-Powered Writing</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Get intelligent suggestions, plot development ideas, and character voice consistency checks.
              </p>
              <Button variant="default" size="sm">
                Try AI Assistant
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default StorytellingDashboard;