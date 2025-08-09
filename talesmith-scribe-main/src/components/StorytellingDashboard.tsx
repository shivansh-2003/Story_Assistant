import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sparkles, BookOpen, Users, FileText, Palette, Brain, Wand2, Star, Heart, Sword, Crown, Loader2, Trash2 } from 'lucide-react';
import HealthCheck from '@/components/HealthCheck';
import testApiConnection from '@/utils/apiTest';
import { storyAPI, characterAPI, Story } from '@/lib/api';
import { PDFExportDialog } from './PDFExportDialog';

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
  const [stories, setStories] = useState<Story[]>([]);
  const [loadingStories, setLoadingStories] = useState(true);
  const [showPDFDialog, setShowPDFDialog] = useState(false);
  const [allCharacters, setAllCharacters] = useState<any[]>([]);
  const [deletingStoryId, setDeletingStoryId] = useState<string | null>(null);

  // Load stories and characters on component mount
  useEffect(() => {
    loadStories();
    loadCharacters();
  }, []);

  const loadStories = async () => {
    try {
      setLoadingStories(true);
      const response = await storyAPI.getAll();
      // Since the API returns story IDs as strings, we need to fetch each story
      const storyPromises = response.stories.map(storyId => storyAPI.getById(storyId));
      const storyDetails = await Promise.all(storyPromises);
      setStories(storyDetails.map(detail => detail.story));
    } catch (error) {
      console.error('Failed to load stories:', error);
      // Keep empty array if loading fails
      setStories([]);
    } finally {
      setLoadingStories(false);
    }
  };

  const loadCharacters = async () => {
    try {
      const response = await characterAPI.getAll();
      setAllCharacters(response.characters || []);
    } catch (error) {
      console.error('Failed to load characters:', error);
      setAllCharacters([]);
    }
  };

  const deleteStory = async (storyId: string) => {
    try {
      setDeletingStoryId(storyId);
      await storyAPI.delete(storyId);
      setStories(prev => prev.filter(story => story.id !== storyId));
      // Note: We'd need a toast notification here if available
    } catch (error) {
      console.error('Failed to delete story:', error);
      // Note: We'd need error toast here if available
    } finally {
      setDeletingStoryId(null);
    }
  };

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
          
          <Card 
            className="bg-card/50 backdrop-blur-sm border-accent/20 hover:shadow-mystical transition-all duration-300 hover:scale-105 cursor-pointer"
            onClick={() => setShowPDFDialog(true)}
          >
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

          {loadingStories ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-2 text-muted-foreground">Loading your stories...</span>
            </div>
          ) : stories.length === 0 ? (
            <div className="text-center py-16">
              <BookOpen className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-serif font-bold mb-2">No Stories Yet</h3>
              <p className="text-muted-foreground mb-6">Start creating your first story to see it here</p>
              <Button variant="hero" onClick={() => navigate('/create-story')}>
                <Wand2 className="w-4 h-4 mr-2" />
                Create Your First Story
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 animate-fade-in">
              {stories.map((story, index) => (
                <Card 
                  key={story.id} 
                  className="bg-card/50 backdrop-blur-sm hover:shadow-elegant transition-all duration-300 hover:scale-105 group cursor-pointer animate-scale-in"
                  style={{ animationDelay: `${index * 100}ms` }}
                  onClick={() => navigate(`/story/${story.id}`)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-2">
                        {getGenreIcon(story.theme)}
                        <Badge variant="outline" className={getStatusColor(story.is_draft ? 'draft' : story.is_completed ? 'completed' : 'in-progress')}>
                          {story.is_draft ? 'draft' : story.is_completed ? 'completed' : 'in-progress'}
                        </Badge>
                      </div>
                      <Star className="w-4 h-4 text-muted-foreground group-hover:text-secondary transition-colors" />
                    </div>
                    <CardTitle className="font-serif text-xl group-hover:text-primary transition-colors">
                      {story.title || 'Untitled Story'}
                    </CardTitle>
                    <CardDescription className="text-sm">
                      {story.base_idea || 'No description available'}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                      <span className="flex items-center space-x-1">
                        <Users className="w-3 h-3" />
                        <span>{story.characters.length} characters</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <FileText className="w-3 h-3" />
                        <span>{story.chapters.length} chapters</span>
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">
                        Updated {new Date(story.updated_at).toLocaleDateString()}
                      </span>
                      <div className="flex space-x-2">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/story/${story.id}`);
                          }}
                        >
                          Edit
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            // TODO: Add export functionality
                            console.log('Export story:', story.id);
                          }}
                        >
                          Export
                        </Button>
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (window.confirm('Are you sure you want to delete this story? This action cannot be undone.')) {
                              deleteStory(story.id!);
                            }
                          }}
                          disabled={deletingStoryId === story.id}
                        >
                          {deletingStoryId === story.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
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
              <Button 
                variant="adventure" 
                size="sm"
                onClick={() => setShowPDFDialog(true)}
              >
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
              <Button 
                variant="default" 
                size="sm"
                onClick={() => {
                  if (stories.length > 0) {
                    navigate(`/story/${stories[0].id}`);
                  } else {
                    navigate('/create-story');
                  }
                }}
              >
                Try AI Assistant
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* PDF Export Dialog */}
      <PDFExportDialog
        open={showPDFDialog}
        onOpenChange={setShowPDFDialog}
        characters={allCharacters}
        relationships={[]}
        story={stories.length > 0 ? {
          title: 'All Stories Collection',
          genre: 'mixed',
          description: 'A collection of your stories',
          chapters: []
        } : null}
        exportType="all"
      />
    </div>
  );
};

export default StorytellingDashboard;