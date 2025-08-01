import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Sparkles, BookOpen, Save, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";

const CreateStory = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [storyData, setStoryData] = useState({
    title: '',
    genre: '',
    description: '',
    premise: '',
    setting: '',
    targetAudience: ''
  });

  const genres = [
    'Fantasy', 'Science Fiction', 'Mystery', 'Romance', 'Thriller', 
    'Horror', 'Adventure', 'Historical Fiction', 'Contemporary', 'Young Adult'
  ];

  const audiences = [
    'Children (5-12)', 'Young Adult (13-17)', 'Adult (18-64)', 'All Ages'
  ];

  const handleInputChange = (field: string, value: string) => {
    setStoryData(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveDraft = () => {
    if (!storyData.title.trim()) {
      toast({
        title: "Title Required",
        description: "Please enter a title for your story.",
        variant: "destructive"
      });
      return;
    }

    // Here you would typically save to a database
    toast({
      title: "Draft Saved",
      description: "Your story has been saved as a draft.",
    });
  };

  const handleCreateStory = () => {
    if (!storyData.title.trim() || !storyData.genre || !storyData.description.trim()) {
      toast({
        title: "Missing Information",
        description: "Please fill in title, genre, and description.",
        variant: "destructive"
      });
      return;
    }

    // Here you would typically create the story in the database
    toast({
      title: "Story Created!",
      description: "Your new story has been created successfully.",
    });
    
    // Navigate to story editor (we'll create this later)
    navigate('/');
  };

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
                <Sparkles className="w-6 h-6 text-primary-glow" />
                <h1 className="text-2xl font-serif font-bold text-foreground">Create New Story</h1>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline" onClick={handleSaveDraft}>
                <Save className="w-4 h-4 mr-2" />
                Save Draft
              </Button>
              <Button variant="hero" onClick={handleCreateStory}>
                <BookOpen className="w-4 h-4 mr-2" />
                Create Story
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Story Details Form */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="font-serif">Story Information</CardTitle>
                <CardDescription>
                  Provide the basic details about your story
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="title">Story Title *</Label>
                  <Input
                    id="title"
                    placeholder="Enter your story title..."
                    value={storyData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className="text-lg font-medium"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="genre">Genre *</Label>
                    <Select onValueChange={(value) => handleInputChange('genre', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a genre" />
                      </SelectTrigger>
                      <SelectContent>
                        {genres.map((genre) => (
                          <SelectItem key={genre} value={genre}>
                            {genre}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="audience">Target Audience</Label>
                    <Select onValueChange={(value) => handleInputChange('targetAudience', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select target audience" />
                      </SelectTrigger>
                      <SelectContent>
                        {audiences.map((audience) => (
                          <SelectItem key={audience} value={audience}>
                            {audience}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description *</Label>
                  <Textarea
                    id="description"
                    placeholder="Provide a brief description of your story..."
                    value={storyData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    className="min-h-[100px]"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="premise">Story Premise</Label>
                  <Textarea
                    id="premise"
                    placeholder="What's the central conflict or main idea of your story?"
                    value={storyData.premise}
                    onChange={(e) => handleInputChange('premise', e.target.value)}
                    className="min-h-[120px]"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="setting">Setting & World</Label>
                  <Textarea
                    id="setting"
                    placeholder="Describe the world, time period, and location where your story takes place..."
                    value={storyData.setting}
                    onChange={(e) => handleInputChange('setting', e.target.value)}
                    className="min-h-[100px]"
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Preview Panel */}
          <div className="space-y-6">
            <Card className="bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 font-serif">
                  <Eye className="w-5 h-5" />
                  <span>Story Preview</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-serif text-lg font-bold text-foreground">
                    {storyData.title || 'Untitled Story'}
                  </h3>
                  {storyData.genre && (
                    <Badge variant="outline" className="mt-2">
                      {storyData.genre}
                    </Badge>
                  )}
                </div>
                
                {storyData.description && (
                  <div>
                    <h4 className="font-medium text-sm text-muted-foreground mb-2">Description</h4>
                    <p className="text-sm text-foreground/80">{storyData.description}</p>
                  </div>
                )}

                {storyData.targetAudience && (
                  <div>
                    <h4 className="font-medium text-sm text-muted-foreground mb-2">Target Audience</h4>
                    <Badge variant="secondary">{storyData.targetAudience}</Badge>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-gradient-primary/10 backdrop-blur-sm border-primary/30">
              <CardHeader>
                <CardTitle className="font-serif text-lg">Next Steps</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Create and develop characters</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Outline chapters and scenes</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Start writing your first chapter</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span>Use AI assistance for ideas</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateStory;