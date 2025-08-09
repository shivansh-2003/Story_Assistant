import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Save, Eye, FileText, Users, Settings, Brain, Download, Network } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import { PDFExportDialog } from '@/components/PDFExportDialog';

const StoryEditor = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { toast } = useToast();
  
  const [storyContent, setStoryContent] = useState({
    title: 'The Crystal Chronicles',
    genre: 'Fantasy',
    description: 'A magical journey through enchanted realms',
    chapters: [
      {
        id: '1',
        title: 'Chapter 1: The Awakening',
        content: 'In the depths of the Whispering Woods, where ancient magic still thrummed through every leaf and stone, Elena Shadowheart felt the familiar pull of destiny...',
        wordCount: 1250,
        status: 'completed'
      },
      {
        id: '2',
        title: 'Chapter 2: The Prophecy Unveiled',
        content: 'The old sage\'s words echoed in Elena\'s mind as she gazed upon the crystal altar...',
        wordCount: 980,
        status: 'in-progress'
      }
    ]
  });

  const [currentChapter, setCurrentChapter] = useState(storyContent.chapters[0]);
  const [isEditing, setIsEditing] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);

  // Mock data for characters and relationships
  const [linkedCharacters] = useState([
    {
      id: '1',
      name: 'Elena Shadowheart',
      age: 28,
      role: 'Protagonist',
      personality: 'Brave, determined, and compassionate. Elena has a strong sense of justice.',
      background: 'Former royal guard who discovered corruption in the kingdom.',
      appearance: 'Tall with raven-black hair and piercing green eyes.',
      motivation: 'To restore justice and protect the innocent.',
      archetype: 'The Hero',
      relationships: []
    },
    {
      id: '2',
      name: 'Lord Varian',
      age: 45,
      role: 'Antagonist',
      personality: 'Cunning, manipulative, and ruthless.',
      background: 'Noble who seized power through political machinations.',
      appearance: 'Distinguished with silver hair and cold blue eyes.',
      motivation: 'To maintain absolute control over the kingdom.',
      archetype: 'The Tyrant',
      relationships: []
    }
  ]);

  const [relationships] = useState([
    {
      id: '1',
      character1Id: '1',
      character2Id: '2',
      type: 'Enemy',
      description: 'Elena seeks to overthrow Varian\'s corrupt rule',
      strength: 8
    }
  ]);

  const saveStory = () => {
    // Here you would save to database
    toast({
      title: "Story Saved",
      description: "Your changes have been saved successfully.",
    });
  };

  const exportStory = () => {
    setShowExportDialog(true);
  };

  const addNewChapter = () => {
    const newChapter = {
      id: Date.now().toString(),
      title: `Chapter ${storyContent.chapters.length + 1}: New Chapter`,
      content: '',
      wordCount: 0,
      status: 'draft' as const
    };
    
    setStoryContent(prev => ({
      ...prev,
      chapters: [...prev.chapters, newChapter]
    }));
    setCurrentChapter(newChapter);
    setIsEditing(true);
  };

  const updateChapterContent = (content: string) => {
    const wordCount = content.trim().split(/\s+/).length;
    const updatedChapter = { 
      ...currentChapter, 
      content, 
      wordCount: content.trim() ? wordCount : 0 
    };
    
    setCurrentChapter(updatedChapter);
    setStoryContent(prev => ({
      ...prev,
      chapters: prev.chapters.map(ch => 
        ch.id === currentChapter.id ? updatedChapter : ch
      )
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-atmospheric">
      {/* Header */}
      <div className="bg-gradient-mystical/50 backdrop-blur-sm border-b border-border/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate('/')}
                className="text-foreground hover:bg-white/10"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-xl font-serif font-bold text-foreground">{storyContent.title}</h1>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline">{storyContent.genre}</Badge>
                  <span className="text-sm text-muted-foreground">
                    {storyContent.chapters.length} chapters
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={exportStory}>
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
              <Button variant="outline" size="sm">
                <Eye className="w-4 h-4 mr-2" />
                Preview
              </Button>
              <Button variant="secondary" size="sm" onClick={saveStory}>
                <Save className="w-4 h-4 mr-2" />
                Save
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Chapters */}
          <div className="lg:col-span-1">
            <Card className="bg-card/50 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg font-serif">Chapters</CardTitle>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={addNewChapter}
                  className="w-full"
                >
                  Add Chapter
                </Button>
              </CardHeader>
              <CardContent className="space-y-2">
                {storyContent.chapters.map((chapter) => (
                  <div
                    key={chapter.id}
                    className={`p-3 rounded-lg cursor-pointer transition-all ${
                      currentChapter.id === chapter.id 
                        ? 'bg-primary/20 border border-primary/30' 
                        : 'bg-muted/30 hover:bg-muted/50'
                    }`}
                    onClick={() => setCurrentChapter(chapter)}
                  >
                    <h4 className="font-medium text-sm">{chapter.title}</h4>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-xs text-muted-foreground">
                        {chapter.wordCount} words
                      </span>
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${
                          chapter.status === 'completed' ? 'border-secondary/30 text-secondary' :
                          chapter.status === 'in-progress' ? 'border-primary/30 text-primary' :
                          'border-muted-foreground/30'
                        }`}
                      >
                        {chapter.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Main Editor */}
          <div className="lg:col-span-3">
            <Tabs defaultValue="write" className="space-y-4">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="write" className="flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>Write</span>
                </TabsTrigger>
                <TabsTrigger value="characters" className="flex items-center space-x-2">
                  <Users className="w-4 h-4" />
                  <span>Characters</span>
                </TabsTrigger>
                <TabsTrigger value="ai-assist" className="flex items-center space-x-2">
                  <Brain className="w-4 h-4" />
                  <span>AI Assist</span>
                </TabsTrigger>
                <TabsTrigger value="settings" className="flex items-center space-x-2">
                  <Settings className="w-4 h-4" />
                  <span>Settings</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="write" className="space-y-4">
                <Card className="bg-card/50 backdrop-blur-sm">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <Input
                          value={currentChapter.title}
                          onChange={(e) => setCurrentChapter(prev => ({ ...prev, title: e.target.value }))}
                          className="font-serif text-lg font-bold border-none bg-transparent p-0 h-auto"
                          placeholder="Chapter Title"
                        />
                        <p className="text-sm text-muted-foreground mt-1">
                          {currentChapter.wordCount} words
                        </p>
                      </div>
                      <Button
                        variant={isEditing ? "secondary" : "outline"}
                        size="sm"
                        onClick={() => setIsEditing(!isEditing)}
                      >
                        {isEditing ? "Preview" : "Edit"}
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {isEditing ? (
                      <Textarea
                        value={currentChapter.content}
                        onChange={(e) => updateChapterContent(e.target.value)}
                        placeholder="Start writing your chapter..."
                        className="min-h-[500px] resize-none border-none bg-transparent p-4 text-base leading-relaxed"
                      />
                    ) : (
                      <div className="min-h-[500px] p-4 bg-background/50 rounded-lg">
                        <div className="prose prose-stone dark:prose-invert max-w-none">
                          {currentChapter.content ? (
                            <p className="text-base leading-relaxed whitespace-pre-wrap">
                              {currentChapter.content}
                            </p>
                          ) : (
                            <p className="text-muted-foreground italic">
                              No content yet. Click Edit to start writing.
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="characters">
                <Card className="bg-card/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle>Story Characters</CardTitle>
                    <CardDescription>
                      Characters linked to this story
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Show linked characters */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 border border-border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">Elena Shadowheart</h4>
                            <Badge variant="outline">Protagonist</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">The Hero</p>
                          <p className="text-xs text-muted-foreground">
                            Former royal guard turned rebel seeking justice
                          </p>
                        </div>
                        <div className="p-4 border border-border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">Lord Varian</h4>
                            <Badge variant="outline">Antagonist</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">The Tyrant</p>
                          <p className="text-xs text-muted-foreground">
                            Noble who seized power through manipulation
                          </p>
                        </div>
                      </div>
                      
                      <div className="text-center pt-4 border-t border-border space-y-2">
                        <div className="flex justify-center space-x-2">
                          <Button 
                            variant="outline"
                            size="sm"
                            onClick={() => navigate('/characters')}
                          >
                            <Users className="w-4 h-4 mr-2" />
                            Manage Characters
                          </Button>
                          <Button 
                            variant="outline"
                            size="sm"
                            onClick={() => setShowExportDialog(true)}
                          >
                            <Network className="w-4 h-4 mr-2" />
                            View Relationships
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="ai-assist">
                <Card className="bg-card/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Brain className="w-5 h-5" />
                      <span>AI Writing Assistant</span>
                    </CardTitle>
                    <CardDescription>
                      Get help with plot development, character dialogue, and more
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <Button variant="outline" className="h-auto p-4 text-left">
                          <div>
                            <h4 className="font-medium">Continue Story</h4>
                            <p className="text-sm text-muted-foreground">Get suggestions for what happens next</p>
                          </div>
                        </Button>
                        <Button variant="outline" className="h-auto p-4 text-left">
                          <div>
                            <h4 className="font-medium">Improve Dialogue</h4>
                            <p className="text-sm text-muted-foreground">Enhance character conversations</p>
                          </div>
                        </Button>
                        <Button variant="outline" className="h-auto p-4 text-left">
                          <div>
                            <h4 className="font-medium">Plot Ideas</h4>
                            <p className="text-sm text-muted-foreground">Generate plot twists and developments</p>
                          </div>
                        </Button>
                        <Button variant="outline" className="h-auto p-4 text-left">
                          <div>
                            <h4 className="font-medium">Character Voice</h4>
                            <p className="text-sm text-muted-foreground">Maintain consistent character voices</p>
                          </div>
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="settings">
                <Card className="bg-card/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle>Story Settings</CardTitle>
                    <CardDescription>
                      Configure your story preferences
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Story Title</label>
                      <Input 
                        value={storyContent.title}
                        onChange={(e) => setStoryContent(prev => ({ ...prev, title: e.target.value }))}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Description</label>
                      <Textarea 
                        value={storyContent.description}
                        onChange={(e) => setStoryContent(prev => ({ ...prev, description: e.target.value }))}
                        className="mt-1"
                        rows={3}
                      />
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>

      {/* PDF Export Dialog */}
      <PDFExportDialog
        open={showExportDialog}
        onOpenChange={setShowExportDialog}
        characters={linkedCharacters}
        relationships={relationships}
        story={storyContent}
        exportType="story"
      />
    </div>
  );
};

export default StoryEditor;