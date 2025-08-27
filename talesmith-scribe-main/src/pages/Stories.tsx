import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, BookOpen, Plus, Search, Filter, Crown, Heart, Sword, Star, Loader2, Trash2, Edit, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import { storyAPI, Story, StoryTheme } from '@/lib/api';

const Stories = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTheme, setFilterTheme] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // Load stories on component mount
  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      setLoading(true);
      const response = await storyAPI.getAll();
      // Since the API returns story IDs as strings, we need to fetch each story
      const storyPromises = response.stories.map(storyId => storyAPI.getById(storyId));
      const storyDetails = await Promise.all(storyPromises);
      setStories(storyDetails.map(detail => detail.story));
    } catch (error) {
      console.error('Failed to load stories:', error);
      toast({
        title: "Error Loading Stories",
        description: "Failed to load stories from the server.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const deleteStory = async (storyId: string) => {
    try {
      await storyAPI.delete(storyId);
      setStories(prev => prev.filter(story => story.id !== storyId));
      toast({
        title: "Story Deleted",
        description: "Story has been deleted successfully.",
      });
    } catch (error) {
      console.error('Failed to delete story:', error);
      toast({
        title: "Deletion Failed",
        description: "Failed to delete story. Please try again.",
        variant: "destructive"
      });
    }
  };

  const getGenreIcon = (theme: StoryTheme) => {
    switch (theme) {
      case StoryTheme.FANTASY:
        return <Crown className="w-4 h-4" />;
      case StoryTheme.ROMANCE:
        return <Heart className="w-4 h-4" />;
      case StoryTheme.ADVENTURE:
        return <Sword className="w-4 h-4" />;
      default:
        return <Star className="w-4 h-4" />;
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

  const getStatusText = (story: Story) => {
    if (story.is_draft) return 'draft';
    if (story.is_completed) return 'completed';
    return 'in-progress';
  };

  const filteredStories = stories.filter(story => {
    const matchesSearch = story.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         story.base_idea?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTheme = filterTheme === 'all' || story.theme === filterTheme;
    const matchesStatus = filterStatus === 'all' || getStatusText(story) === filterStatus;
    
    return matchesSearch && matchesTheme && matchesStatus;
  });

  const themeOptions = [
    { value: 'all', label: 'All Themes' },
    { value: StoryTheme.FANTASY, label: 'Fantasy' },
    { value: StoryTheme.MYSTERY, label: 'Mystery' },
    { value: StoryTheme.ADVENTURE, label: 'Adventure' },
    { value: StoryTheme.SCIFI, label: 'Sci-Fi' },
    { value: StoryTheme.HORROR, label: 'Horror' },
    { value: StoryTheme.ROMANCE, label: 'Romance' }
  ];

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'draft', label: 'Draft' },
    { value: 'in-progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' }
  ];

  return (
    <div className="min-h-screen bg-gradient-atmospheric">
      {/* Header */}
      <div className="bg-gradient-mystical/50 backdrop-blur-sm border-b border-border/50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate('/')}
                className="text-foreground hover:bg-white/10"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <div className="flex items-center space-x-2">
                <BookOpen className="w-6 h-6 text-primary-glow" />
                <h1 className="text-2xl font-serif font-bold text-foreground">All Stories</h1>
              </div>
            </div>
            <Button variant="hero" onClick={() => navigate('/create-story')}>
              <Plus className="w-4 h-4 mr-2" />
              Create New Story
            </Button>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search stories by title or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Select value={filterTheme} onValueChange={setFilterTheme}>
              <SelectTrigger className="w-40">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {themeOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {statusOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Stories Grid */}
        {loading ? (
          <div className="text-center py-16">
            <Loader2 className="w-16 h-16 text-primary mx-auto mb-4 animate-spin" />
            <h2 className="text-2xl font-serif font-bold mb-2">Loading Stories</h2>
            <p className="text-muted-foreground">Fetching your story collection...</p>
          </div>
        ) : filteredStories.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-2xl font-serif font-bold mb-2">
              {stories.length === 0 ? 'No Stories Yet' : 'No Stories Found'}
            </h2>
            <p className="text-muted-foreground mb-6">
              {stories.length === 0 
                ? 'Start creating your first story to see it here'
                : 'Try adjusting your search or filters'
              }
            </p>
            {stories.length === 0 && (
              <Button variant="hero" onClick={() => navigate('/create-story')}>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Story
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredStories.map((story, index) => (
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
                      <Badge variant="outline" className={getStatusColor(getStatusText(story))}>
                        {getStatusText(story)}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/story/${story.id}`);
                        }}
                        className="h-8 w-8 p-0"
                        title="Edit Story"
                      >
                        <Edit className="w-3 h-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteStory(story.id);
                        }}
                        className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                        title="Delete Story"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
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
                      <Star className="w-3 h-3" />
                      <span>{story.characters.length} characters</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <BookOpen className="w-3 h-3" />
                      <span>{story.chapters.length} chapters</span>
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                      Updated {new Date(story.updated_at).toLocaleDateString()}
                    </span>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/story/${story.id}`);
                      }}
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      View
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Summary */}
        {!loading && stories.length > 0 && (
          <div className="mt-8 text-center">
            <p className="text-sm text-muted-foreground">
              Showing {filteredStories.length} of {stories.length} stories
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Stories;
