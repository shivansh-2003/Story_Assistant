import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Crown, Heart, Sword, Star, Edit, Trash2, Download, Save, X } from 'lucide-react';
import { characterAPI, PersonalityType } from '@/lib/api';
import { useToast } from "@/hooks/use-toast";

interface Character {
  id: string;
  name: string;
  age?: number;
  role?: string;
  personality?: string;
  background?: string;
  appearance?: string;
  motivation?: string;
  archetype?: string;
  relationships?: string[];
  primary_trait?: string;
}

interface CharacterCardProps {
  character: Character;
  onDelete: () => void;
  onExportProfile?: () => void;
  onUpdate: (updatedCharacter: Character) => void;
}

const CharacterCard: React.FC<CharacterCardProps> = ({ character, onDelete, onExportProfile, onUpdate }) => {
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [editedCharacter, setEditedCharacter] = useState<Character>(character);
  const [saving, setSaving] = useState(false);

  const archetypes = [
    'The Hero', 'The Mentor', 'The Ally', 'The Guardian', 'The Trickster',
    'The Shapeshifter', 'The Shadow', 'The Tyrant', 'The Innocent', 'The Explorer'
  ];

  const roles = ['Protagonist', 'Antagonist', 'Supporting Character', 'Minor Character', 'Love Interest'];
  
  const personalityTraits = [
    { value: PersonalityType.BRAVE, label: 'Brave' },
    { value: PersonalityType.CLEVER, label: 'Clever' },
    { value: PersonalityType.SHY, label: 'Shy' },
    { value: PersonalityType.AGGRESSIVE, label: 'Aggressive' },
    { value: PersonalityType.WISE, label: 'Wise' },
    { value: PersonalityType.COMPASSIONATE, label: 'Compassionate' },
    { value: PersonalityType.CUNNING, label: 'Cunning' }
  ];

  const handleInputChange = (field: keyof Character, value: any) => {
    setEditedCharacter(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    if (!editedCharacter.name?.trim()) {
      toast({
        title: "Name Required",
        description: "Please enter a character name.",
        variant: "destructive"
      });
      return;
    }

    try {
      setSaving(true);
      const response = await characterAPI.update(character.id, editedCharacter);
      onUpdate(response.character);
      setIsEditing(false);
      toast({
        title: "Character Updated",
        description: "Character has been updated successfully.",
      });
    } catch (error) {
      console.error('Failed to update character:', error);
      toast({
        title: "Update Failed",
        description: "Failed to update character. Please try again.",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditedCharacter(character);
    setIsEditing(false);
  };

  const getArchetypeIcon = (archetype: string) => {
    switch (archetype) {
      case 'The Hero': return <Crown className="w-4 h-4" />;
      case 'The Tyrant': return <Sword className="w-4 h-4" />;
      case 'The Innocent': return <Heart className="w-4 h-4" />;
      default: return <Star className="w-4 h-4" />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'Protagonist': return 'bg-primary/20 text-primary border-primary/30';
      case 'Antagonist': return 'bg-destructive/20 text-destructive border-destructive/30';
      case 'Supporting Character': return 'bg-secondary/20 text-secondary border-secondary/30';
      case 'Love Interest': return 'bg-accent/20 text-accent border-accent/30';
      default: return 'bg-muted/50 text-muted-foreground border-border';
    }
  };

  return (
    <>
      <Card className="bg-card/50 backdrop-blur-sm hover:shadow-mystical transition-all duration-300 hover:scale-105 group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-2">
              {getArchetypeIcon(character.archetype)}
              <Badge variant="outline" className={getRoleColor(character.role)}>
                {character.role}
              </Badge>
            </div>
            <div className="flex items-center space-x-1">
              {onExportProfile && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onExportProfile}
                  className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Export Profile"
                >
                  <Download className="w-3 h-3" />
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditing(true)}
                className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Edit Character"
              >
                <Edit className="w-3 h-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onDelete}
                className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:text-destructive"
                title="Delete Character"
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          </div>
          <CardTitle className="font-serif text-xl group-hover:text-primary transition-colors">
            {character.name}
          </CardTitle>
          <CardDescription className="text-sm">
            Age {character.age} • {character.archetype}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {character.personality && (
            <div>
              <h4 className="font-medium text-xs text-muted-foreground mb-1">Personality</h4>
              <p className="text-sm text-foreground/80 line-clamp-2">{character.personality}</p>
            </div>
          )}
          
          {character.background && (
            <div>
              <h4 className="font-medium text-xs text-muted-foreground mb-1">Background</h4>
              <p className="text-sm text-foreground/80 line-clamp-3">{character.background}</p>
            </div>
          )}

          {character.motivation && (
            <div>
              <h4 className="font-medium text-xs text-muted-foreground mb-1">Motivation</h4>
              <p className="text-sm text-foreground/80 line-clamp-2">{character.motivation}</p>
            </div>
          )}

          {character.relationships && character.relationships.length > 0 && (
            <div>
              <h4 className="font-medium text-xs text-muted-foreground mb-2">Relationships</h4>
              <div className="flex flex-wrap gap-1">
                {character.relationships.slice(0, 2).map((rel, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {rel}
                  </Badge>
                ))}
                {character.relationships.length > 2 && (
                  <Badge variant="outline" className="text-xs">
                    +{character.relationships.length - 2} more
                  </Badge>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditing} onOpenChange={setIsEditing}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="font-serif">Edit Character: {character.name}</DialogTitle>
            <DialogDescription>
              Update your character's details
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Character Name *</Label>
                <Input
                  id="edit-name"
                  placeholder="Enter character name..."
                  value={editedCharacter.name || ''}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-age">Age</Label>
                <Input
                  id="edit-age"
                  type="number"
                  placeholder="25"
                  value={editedCharacter.age || ''}
                  onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-role">Role</Label>
                <Select onValueChange={(value) => handleInputChange('role', value)} value={editedCharacter.role}>
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
                <Label htmlFor="edit-archetype">Archetype</Label>
                <Select onValueChange={(value) => handleInputChange('archetype', value)} value={editedCharacter.archetype}>
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
              <Label htmlFor="edit-primary-trait">Primary Personality Trait</Label>
              <Select onValueChange={(value) => handleInputChange('primary_trait', value)} value={editedCharacter.primary_trait}>
                <SelectTrigger>
                  <SelectValue placeholder="Select primary trait" />
                </SelectTrigger>
                <SelectContent>
                  {personalityTraits.map((trait) => (
                    <SelectItem key={trait.value} value={trait.value}>{trait.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-personality">Personality</Label>
              <Textarea
                id="edit-personality"
                placeholder="Describe their personality traits..."
                value={editedCharacter.personality || ''}
                onChange={(e) => handleInputChange('personality', e.target.value)}
                className="min-h-[80px]"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-background">Background</Label>
              <Textarea
                id="edit-background"
                placeholder="Their history and background story..."
                value={editedCharacter.background || ''}
                onChange={(e) => handleInputChange('background', e.target.value)}
                className="min-h-[80px]"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-appearance">Appearance</Label>
              <Textarea
                id="edit-appearance"
                placeholder="Physical description..."
                value={editedCharacter.appearance || ''}
                onChange={(e) => handleInputChange('appearance', e.target.value)}
                className="min-h-[60px]"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-motivation">Motivation</Label>
              <Textarea
                id="edit-motivation"
                placeholder="What drives them? What do they want?"
                value={editedCharacter.motivation || ''}
                onChange={(e) => handleInputChange('motivation', e.target.value)}
                className="min-h-[60px]"
              />
            </div>

            <div className="flex justify-end space-x-3">
              <Button variant="outline" onClick={handleCancel} disabled={saving}>
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={saving}>
                <Save className="w-4 h-4 mr-2" />
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default CharacterCard;