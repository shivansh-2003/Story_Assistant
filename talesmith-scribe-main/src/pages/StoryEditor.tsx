import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Save, Eye, FileText, Users, Settings, Brain, Download, Network, Loader2, Plus } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import { PDFExportDialog } from '@/components/PDFExportDialog';
import { storyAPI, chapterAPI, Story, Chapter, ChapterStatus, StoryTheme } from '@/lib/api';

const StoryEditor = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { toast } = useToast();
  
  const [story, setStory] = useState<Story | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [currentChapter, setCurrentChapter] = useState<Chapter | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [aiProcessing, setAiProcessing] = useState(false);

  // Load story and chapters on mount
  useEffect(() => {
    if (id) {
      loadStoryData();
    }
  }, [id]);

  const loadStoryData = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      const [storyResponse, chaptersResponse] = await Promise.all([
        storyAPI.getById(id),
        chapterAPI.getAll(id)
      ]);
      
      setStory(storyResponse.story);
      setChapters(chaptersResponse.chapters);
      
      if (chaptersResponse.chapters.length > 0) {
        setCurrentChapter(chaptersResponse.chapters[0]);
      }
    } catch (error) {
      console.error('Failed to load story:', error);
      toast({
        title: "Error Loading Story",
        description: "Failed to load story data. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

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

  const saveStory = async () => {
    if (!story || !id) return;
    
    try {
      setSaving(true);
      await storyAPI.update(id, story);
      toast({
        title: "Story Saved",
        description: "Your changes have been saved successfully.",
      });
    } catch (error) {
      console.error('Failed to save story:', error);
      toast({
        title: "Save Failed",
        description: "Failed to save story. Please try again.",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  const saveChapter = async (chapter: Chapter) => {
    if (!id) return;
    
    try {
      await chapterAPI.update(id, chapter.id!, {
        title: chapter.title,
        content: chapter.content,
        status: chapter.status
      });
      
      // Update local state
      setChapters(prev => prev.map(ch => ch.id === chapter.id ? chapter : ch));
      
      toast({
        title: "Chapter Saved",
        description: "Chapter has been saved successfully.",
      });
    } catch (error) {
      console.error('Failed to save chapter:', error);
      toast({
        title: "Save Failed",
        description: "Failed to save chapter. Please try again.",
        variant: "destructive"
      });
    }
  };

  const exportStory = () => {
    setShowExportDialog(true);
  };

  const addNewChapter = async () => {
    if (!id) return;
    
    try {
      const newChapterData = {
        title: `Chapter ${chapters.length + 1}: New Chapter`,
        content: '',
        status: ChapterStatus.DRAFT
      };
      
      const response = await chapterAPI.create(id, newChapterData);
      const newChapter = response.chapter;
      
      setChapters(prev => [...prev, newChapter]);
      setCurrentChapter(newChapter);
      setIsEditing(true);
      
      toast({
        title: "Chapter Created",
        description: "New chapter has been added to your story.",
      });
    } catch (error) {
      console.error('Failed to create chapter:', error);
      toast({
        title: "Creation Failed",
        description: "Failed to create new chapter. Please try again.",
        variant: "destructive"
      });
    }
  };

  const updateChapterContent = (content: string) => {
    if (!currentChapter) return;
    
    const wordCount = content.trim().split(/\s+/).length;
    const updatedChapter = { 
      ...currentChapter, 
      content, 
      word_count: content.trim() ? wordCount : 0 
    };
    
    setCurrentChapter(updatedChapter);
  };

  // AI Assistant Functions
  const generateChapterContent = async () => {
    if (!currentChapter || !id) return;
    
    try {
      setAiProcessing(true);
      const response = await chapterAPI.generateContent(id, currentChapter.id!, 'medium');
      const updatedChapter = response.chapter;
      
      setCurrentChapter(updatedChapter);
      setChapters(prev => prev.map(ch => ch.id === updatedChapter.id ? updatedChapter : ch));
      
      toast({
        title: "Content Generated!",
        description: "AI has generated content for your chapter.",
      });
    } catch (error) {
      console.error('Failed to generate content:', error);
      toast({
        title: "Generation Failed",
        description: "Failed to generate AI content. Please try again.",
        variant: "destructive"
      });
    } finally {
      setAiProcessing(false);
    }
  };

  const continueStory = async () => {
    if (!story || !currentChapter || !id) return;
    
    try {
      setAiProcessing(true);
      const response = await storyAPI.generateSegment({
        story_id: id,
        theme: story.theme,
        characters: story.characters,
        previous_content: currentChapter.content,
        auto_continue: true
      });
      
      // Add the new segment to current chapter
      const newContent = currentChapter.content + '\n\n' + (response.new_segment?.content || '');
      const updatedChapter = { ...currentChapter, content: newContent };
      
      setCurrentChapter(updatedChapter);
      
      toast({
        title: "Story Continued!",
        description: "AI has added new content to continue your story.",
      });
    } catch (error) {
      console.error('Failed to continue story:', error);
      toast({
        title: "Generation Failed",
        description: "Failed to continue story. Please try again.",
        variant: "destructive"
      });
    } finally {
      setAiProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-atmospheric flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <h2 className="text-xl font-serif font-bold mb-2">Loading Story</h2>
          <p className="text-muted-foreground">Please wait while we load your story...</p>
        </div>
      </div>
    );
  }

  if (!story) {
    return (
      <div className="min-h-screen bg-gradient-atmospheric flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-serif font-bold mb-2">Story Not Found</h2>
          <p className="text-muted-foreground mb-4">The requested story could not be loaded.</p>
          <Button onClick={() => navigate('/')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

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
                <h1 className="text-xl font-serif font-bold text-foreground">{story.title || 'Untitled Story'}</h1>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline">{story.theme}</Badge>
                  <span className="text-sm text-muted-foreground">
                    {chapters.length} chapters
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
              <Button variant="secondary" size="sm" onClick={saveStory} disabled={saving}>
                {saving ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Save className="w-4 h-4 mr-2" />
                )}
                {saving ? 'Saving...' : 'Save'}
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
                {chapters.length === 0 ? (
                  <div className="text-center py-8">
                    <FileText className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">No chapters yet</p>
                  </div>
                ) : (
                  chapters.map((chapter) => (
                    <div
                      key={chapter.id}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        currentChapter?.id === chapter.id 
                          ? 'bg-primary/20 border border-primary/30' 
                          : 'bg-muted/30 hover:bg-muted/50'
                      }`}
                      onClick={() => setCurrentChapter(chapter)}
                    >
                      <h4 className="font-medium text-sm">{chapter.title}</h4>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-muted-foreground">
                          {chapter.word_count || 0} words
                        </span>
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${
                            chapter.status === ChapterStatus.COMPLETED ? 'border-secondary/30 text-secondary' :
                            chapter.status === ChapterStatus.IN_PROGRESS ? 'border-primary/30 text-primary' :
                            'border-muted-foreground/30'
                          }`}
                        >
                          {chapter.status}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
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
                {!currentChapter ? (
                  <Card className="bg-card/50 backdrop-blur-sm">
                    <CardContent className="p-8 text-center">
                      <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-serif font-bold mb-2">No Chapter Selected</h3>
                      <p className="text-muted-foreground mb-6">Create or select a chapter to start writing your story.</p>
                      <Button variant="hero" onClick={addNewChapter}>
                        <Plus className="w-4 h-4 mr-2" />
                        Create First Chapter
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  <Card className="bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex-1 mr-4">
                          <Input
                            value={currentChapter.title}
                            onChange={(e) => {
                              const updatedChapter = { ...currentChapter, title: e.target.value };
                              setCurrentChapter(updatedChapter);
                            }}
                            className="font-serif text-lg font-bold border-none bg-transparent p-0 h-auto"
                            placeholder="Chapter Title"
                          />
                          <p className="text-sm text-muted-foreground mt-1">
                            {currentChapter.word_count || 0} words
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => saveChapter(currentChapter)}
                            disabled={saving}
                          >
                            {saving ? (
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                              <Save className="w-4 h-4 mr-2" />
                            )}
                            Save Chapter
                          </Button>
                          <Button
                            variant={isEditing ? "secondary" : "outline"}
                            size="sm"
                            onClick={() => setIsEditing(!isEditing)}
                          >
                            {isEditing ? "Preview" : "Edit"}
                          </Button>
                        </div>
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
                )}
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
                      {story?.characters && story.characters.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {story.characters.map((character) => (
                            <div key={character.id} className="p-4 border border-border rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium">{character.name}</h4>
                                <Badge variant="outline">{character.role || 'Character'}</Badge>
                              </div>
                              <p className="text-sm text-muted-foreground mb-2">{character.archetype || 'Unknown Archetype'}</p>
                              <p className="text-xs text-muted-foreground">
                                {character.background || character.personality || 'No description available'}
                              </p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                          <h3 className="text-lg font-serif font-bold mb-2">No Characters</h3>
                          <p className="text-muted-foreground mb-4">This story doesn't have any characters yet.</p>
                          <Button 
                            variant="outline"
                            onClick={() => navigate('/characters')}
                          >
                            <Users className="w-4 h-4 mr-2" />
                            Manage Characters
                          </Button>
                        </div>
                      )}
                      
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
                      {!currentChapter ? (
                        <div className="text-center py-8">
                          <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                          <p className="text-muted-foreground">Select or create a chapter to use AI assistance</p>
                          <Button variant="outline" onClick={addNewChapter} className="mt-4">
                            <Plus className="w-4 h-4 mr-2" />
                            Create Chapter
                          </Button>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 gap-4">
                            <Button 
                              variant="outline" 
                              className="h-auto p-4 text-left"
                              onClick={continueStory}
                              disabled={aiProcessing}
                            >
                              <div>
                                <h4 className="font-medium flex items-center">
                                  {aiProcessing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                                  Continue Story
                                </h4>
                                <p className="text-sm text-muted-foreground">Get suggestions for what happens next</p>
                              </div>
                            </Button>
                            <Button 
                              variant="outline" 
                              className="h-auto p-4 text-left"
                              onClick={generateChapterContent}
                              disabled={aiProcessing}
                            >
                              <div>
                                <h4 className="font-medium flex items-center">
                                  {aiProcessing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                                  Generate Content
                                </h4>
                                <p className="text-sm text-muted-foreground">Create AI-generated chapter content</p>
                              </div>
                            </Button>
                            <Button variant="outline" className="h-auto p-4 text-left" disabled>
                              <div>
                                <h4 className="font-medium">Improve Dialogue</h4>
                                <p className="text-sm text-muted-foreground">Enhance character conversations (Coming Soon)</p>
                              </div>
                            </Button>
                            <Button variant="outline" className="h-auto p-4 text-left" disabled>
                              <div>
                                <h4 className="font-medium">Character Voice</h4>
                                <p className="text-sm text-muted-foreground">Maintain consistent character voices (Coming Soon)</p>
                              </div>
                            </Button>
                          </div>
                          
                          {aiProcessing && (
                            <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
                              <div className="flex items-center space-x-3">
                                <Loader2 className="w-5 h-5 animate-spin text-primary" />
                                <div>
                                  <h4 className="font-medium text-primary">AI is working...</h4>
                                  <p className="text-sm text-muted-foreground">Generating content for your story. This may take a moment.</p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
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
                        value={story?.title || ''}
                        onChange={(e) => story && setStory({ ...story, title: e.target.value })}
                        className="mt-1"
                        placeholder="Enter story title..."
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Base Idea</label>
                      <Textarea 
                        value={story?.base_idea || ''}
                        onChange={(e) => story && setStory({ ...story, base_idea: e.target.value })}
                        className="mt-1"
                        rows={3}
                        placeholder="Describe your story idea..."
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Theme</label>
                      <Badge variant="outline" className="mt-1 block w-fit">
                        {story?.theme || 'No theme set'}
                      </Badge>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Status</label>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge variant={story?.is_draft ? "outline" : "secondary"}>
                          {story?.is_draft ? 'Draft' : story?.is_completed ? 'Completed' : 'In Progress'}
                        </Badge>
                      </div>
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
        characters={story?.characters || []}
        relationships={[]}
        story={story ? {
          title: story.title || 'Untitled Story',
          genre: story.theme,
          description: story.base_idea,
          chapters: chapters.map(ch => ({
            id: ch.id!,
            title: ch.title,
            content: ch.content,
            wordCount: ch.word_count || 0,
            status: ch.status
          }))
        } : null}
        exportType="story"
      />
    </div>
  );
};

export default StoryEditor;