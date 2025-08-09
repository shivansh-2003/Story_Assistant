import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ArrowLeft, Plus, Users, Sparkles, Brain, Eye, Edit, Trash2, Crown, Heart, Sword, Star, Download, FileUser, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import CharacterCard from '@/components/CharacterCard';
import RelationshipMapping from '@/components/RelationshipMapping';
import { exportCharacterProfile, exportAllCharacters } from '@/utils/pdfExport';
import { characterAPI, Character, PersonalityType } from '@/lib/api';

// Remove duplicate interface since it's imported from api.ts

const Characters = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [showRelationshipMapping, setShowRelationshipMapping] = useState(false);
  const [newCharacter, setNewCharacter] = useState<Partial<Character>>({
    name: '',
    age: 0,
    role: '',
    personality: '',
    background: '',
    appearance: '',
    motivation: '',
    archetype: '',
    relationships: []
  });

  // Load characters on component mount
  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    try {
      setLoading(true);
      const response = await characterAPI.getAll();
      setCharacters(response.characters);
    } catch (error) {
      console.error('Failed to load characters:', error);
      toast({
        title: "Error Loading Characters",
        description: "Failed to load characters from the server.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const archetypes = [
    'The Hero', 'The Mentor', 'The Ally', 'The Guardian', 'The Trickster',
    'The Shapeshifter', 'The Shadow', 'The Tyrant', 'The Innocent', 'The Explorer'
  ];

  const roles = ['Protagonist', 'Antagonist', 'Supporting Character', 'Minor Character', 'Love Interest'];

  const handleInputChange = (field: keyof Character, value: any) => {
    setNewCharacter(prev => ({ ...prev, [field]: value }));
  };

  const generateCharacter = async () => {
    try {
      // Generate a basic character structure first
      const names = ['Aria Moonwhisper', 'Thorne Blackstone', 'Lyra Stardust', 'Gareth Ironwill', 'Seraphina Brightblade'];
      const personalities = ['Mysterious and wise', 'Bold and impulsive', 'Gentle but fierce', 'Loyal and steadfast', 'Cunning and ambitious'];
      const backgrounds = ['Orphaned at birth, raised by wolves', 'Former assassin seeking redemption', 'Lost heir to a forgotten kingdom', 'Scholar of ancient magics', 'Wandering bard with secrets'];
      
      const randomName = names[Math.floor(Math.random() * names.length)];
      const randomPersonality = personalities[Math.floor(Math.random() * personalities.length)];
      const randomBackground = backgrounds[Math.floor(Math.random() * backgrounds.length)];
      
      const baseCharacter: Partial<Character> = {
        name: randomName,
        age: Math.floor(Math.random() * 50) + 18,
        personality: randomPersonality,
        background: randomBackground,
        role: roles[Math.floor(Math.random() * roles.length)],
        archetype: archetypes[Math.floor(Math.random() * archetypes.length)],
        appearance: 'Generate appearance based on name and background',
        motivation: 'AI-generated motivation based on personality',
        relationships: []
      };
      
      setNewCharacter(baseCharacter);

      toast({
        title: "Character Generated!",
        description: "AI has created a new character for you to customize.",
      });
    } catch (error) {
      console.error('Character generation failed:', error);
      toast({
        title: "Generation Failed",
        description: "Failed to generate character. Please try again.",
        variant: "destructive"
      });
    }
  };

  const saveCharacter = async () => {
    if (!newCharacter.name?.trim()) {
      toast({
        title: "Name Required",
        description: "Please enter a character name.",
        variant: "destructive"
      });
      return;
    }

    try {
      const characterData = {
        name: newCharacter.name || '',
        age: newCharacter.age || 25,
        role: newCharacter.role || 'Supporting Character',
        personality: newCharacter.personality || '',
        background: newCharacter.background || '',
        appearance: newCharacter.appearance || '',
        motivation: newCharacter.motivation || '',
        archetype: newCharacter.archetype || 'The Explorer',
        relationships: newCharacter.relationships || [],
        primary_trait: PersonalityType.KIND // Default trait
      };

      const response = await characterAPI.create(characterData);
      
      // Update local state with the new character
      setCharacters(prev => [...prev, response.character]);
      
      // Reset form
      setNewCharacter({
        name: '', age: 0, role: '', personality: '', background: '',
        appearance: '', motivation: '', archetype: '', relationships: []
      });
      setIsDialogOpen(false);

      toast({
        title: "Character Created!",
        description: "Your new character has been added to your collection.",
      });
    } catch (error) {
      console.error('Failed to create character:', error);
      toast({
        title: "Creation Failed",
        description: "Failed to create character. Please try again.",
        variant: "destructive"
      });
    }
  };

  const deleteCharacter = async (id: string) => {
    try {
      await characterAPI.delete(id);
      setCharacters(prev => prev.filter(char => char.id !== id));
      toast({
        title: "Character Deleted",
        description: "Character has been removed from your collection.",
      });
    } catch (error) {
      console.error('Failed to delete character:', error);
      toast({
        title: "Deletion Failed",
        description: "Failed to delete character. Please try again.",
        variant: "destructive"
      });
    }
  };

  const getArchetypeIcon = (archetype: string) => {
    switch (archetype) {
      case 'The Hero': return <Crown className="w-4 h-4" />;
      case 'The Tyrant': return <Sword className="w-4 h-4" />;
      case 'The Innocent': return <Heart className="w-4 h-4" />;
      default: return <Star className="w-4 h-4" />;
    }
  };

  const exportSingleCharacterProfile = async (character: Character) => {
    try {
      await exportCharacterProfile(character);
      toast({
        title: "Export Complete",
        description: `${character.name}'s profile has been exported as PDF.`,
      });
    } catch (error) {
      toast({
        title: "Export Failed",
        description: "Failed to export character profile.",
        variant: "destructive"
      });
    }
  };

  const exportAllCharacterProfiles = async () => {
    if (characters.length === 0) {
      toast({
        title: "No Characters",
        description: "Create some characters first before exporting.",
        variant: "destructive"
      });
      return;
    }

    try {
      await exportAllCharacters(characters);
      toast({
        title: "Export Complete",
        description: "All character profiles have been exported as PDF.",
      });
    } catch (error) {
      toast({
        title: "Export Failed",
        description: "Failed to export character profiles.",
        variant: "destructive"
      });
    }
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
                <Users className="w-6 h-6 text-secondary-glow" />
                <h1 className="text-2xl font-serif font-bold text-foreground">Character Development</h1>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline" onClick={generateCharacter}>
                <Brain className="w-4 h-4 mr-2" />
                AI Generate
              </Button>
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="hero">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Character
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle className="font-serif">Create New Character</DialogTitle>
                    <DialogDescription>
                      Develop a compelling character for your story
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="char-name">Character Name *</Label>
                        <Input
                          id="char-name"
                          placeholder="Enter character name..."
                          value={newCharacter.name || ''}
                          onChange={(e) => handleInputChange('name', e.target.value)}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="char-age">Age</Label>
                        <Input
                          id="char-age"
                          type="number"
                          placeholder="25"
                          value={newCharacter.age || ''}
                          onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="char-role">Role</Label>
                        <Select onValueChange={(value) => handleInputChange('role', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select role" />
                          </SelectTrigger>
                          <SelectContent>
                            {roles.map((role) => (
                              <SelectItem key={role} value={role}>{role}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="char-archetype">Archetype</Label>
                        <Select onValueChange={(value) => handleInputChange('archetype', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select archetype" />
                          </SelectTrigger>
                          <SelectContent>
                            {archetypes.map((archetype) => (
                              <SelectItem key={archetype} value={archetype}>{archetype}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="char-personality">Personality</Label>
                      <Textarea
                        id="char-personality"
                        placeholder="Describe their personality traits..."
                        value={newCharacter.personality || ''}
                        onChange={(e) => handleInputChange('personality', e.target.value)}
                        className="min-h-[80px]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="char-background">Background</Label>
                      <Textarea
                        id="char-background"
                        placeholder="Their history and background story..."
                        value={newCharacter.background || ''}
                        onChange={(e) => handleInputChange('background', e.target.value)}
                        className="min-h-[80px]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="char-appearance">Appearance</Label>
                      <Textarea
                        id="char-appearance"
                        placeholder="Physical description..."
                        value={newCharacter.appearance || ''}
                        onChange={(e) => handleInputChange('appearance', e.target.value)}
                        className="min-h-[60px]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="char-motivation">Motivation</Label>
                      <Textarea
                        id="char-motivation"
                        placeholder="What drives them? What do they want?"
                        value={newCharacter.motivation || ''}
                        onChange={(e) => handleInputChange('motivation', e.target.value)}
                        className="min-h-[60px]"
                      />
                    </div>

                    <div className="flex justify-end space-x-3">
                      <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={saveCharacter}>
                        Create Character
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {showRelationshipMapping ? (
          <RelationshipMapping 
            characters={characters}
            onClose={() => setShowRelationshipMapping(false)}
          />
        ) : loading ? (
          <div className="text-center py-16">
            <Loader2 className="w-16 h-16 text-primary mx-auto mb-4 animate-spin" />
            <h2 className="text-2xl font-serif font-bold mb-2">Loading Characters</h2>
            <p className="text-muted-foreground">Fetching your character collection...</p>
          </div>
        ) : characters.length === 0 ? (
          <div className="text-center py-16">
            <Users className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-2xl font-serif font-bold mb-2">No Characters Yet</h2>
            <p className="text-muted-foreground mb-6">Start building your cast of characters</p>
            <Button variant="hero" onClick={() => setIsDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Character
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {characters.map((character) => (
              <CharacterCard 
                key={character.id} 
                character={character}
                onDelete={() => deleteCharacter(character.id)}
                onExportProfile={() => exportSingleCharacterProfile(character)}
              />
            ))}
          </div>
        )}

        {/* Character Development Tools */}
        {characters.length > 0 && !showRelationshipMapping && (
          <div className="mt-12 grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-gradient-fantasy/10 backdrop-blur-sm border-accent/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 font-serif">
                  <Sparkles className="w-5 h-5 text-accent" />
                  <span>Relationship Mapping</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Visualize connections between your characters and develop complex relationships.
                </p>
                <Button 
                  variant="fantasy" 
                  size="sm"
                  onClick={() => setShowRelationshipMapping(true)}
                >
                  Build Relationships
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-gradient-primary/10 backdrop-blur-sm border-primary/30">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 font-serif">
                  <FileUser className="w-5 h-5 text-primary" />
                  <span>Character Profiles</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Export detailed character sheets and profiles for reference.
                </p>
                <div className="flex flex-col space-y-2">
                  <Button 
                    variant="default" 
                    size="sm"
                    onClick={exportAllCharacterProfiles}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export All Profiles
                  </Button>
                  <p className="text-xs text-muted-foreground">
                    Individual profiles can be exported from each character card
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Characters;