import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Heart, Users, Plus, Trash2, Edit, Loader2, Network } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";
import { relationshipAPI, Relationship, RelationshipRequest, Character } from '@/lib/api';

interface RelationshipManagementDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  characters: Character[];
  storyId?: string;
  onRelationshipChange?: () => void;
}

export const RelationshipManagementDialog = ({
  open,
  onOpenChange,
  characters,
  storyId,
  onRelationshipChange
}: RelationshipManagementDialogProps) => {
  const { toast } = useToast();
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);

  const [newRelationship, setNewRelationship] = useState<RelationshipRequest>({
    character1_id: '',
    character2_id: '',
    type: '',
    description: '',
    strength: 5
  });

  const relationshipTypes = [
    'Friend', 'Enemy', 'Family', 'Romantic', 'Mentor', 'Student', 'Rival', 
    'Ally', 'Business Partner', 'Neighbor', 'Colleague', 'Subordinate', 
    'Superior', 'Sibling', 'Parent', 'Child', 'Spouse', 'Ex-lover', 'Stranger'
  ];

  useEffect(() => {
    if (open) {
      loadRelationships();
    }
  }, [open]);

  const loadRelationships = async () => {
    try {
      setLoading(true);
      const response = await relationshipAPI.getAll();
      setRelationships(response.relationships || []);
    } catch (error) {
      console.error('Failed to load relationships:', error);
      toast({
        title: "Error Loading Relationships",
        description: "Failed to load relationships. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const createRelationship = async () => {
    if (!newRelationship.character1_id || !newRelationship.character2_id || !newRelationship.type) {
      toast({
        title: "Missing Information",
        description: "Please select both characters and a relationship type.",
        variant: "destructive"
      });
      return;
    }

    if (newRelationship.character1_id === newRelationship.character2_id) {
      toast({
        title: "Invalid Relationship",
        description: "A character cannot have a relationship with themselves.",
        variant: "destructive"
      });
      return;
    }

    try {
      setCreating(true);
      const response = await relationshipAPI.create(newRelationship);
      setRelationships(prev => [...prev, response.relationship]);
      
      // Reset form
      setNewRelationship({
        character1_id: '',
        character2_id: '',
        type: '',
        description: '',
        strength: 5
      });

      toast({
        title: "Relationship Created!",
        description: "The relationship has been added successfully.",
      });

      if (onRelationshipChange) {
        onRelationshipChange();
      }
    } catch (error) {
      console.error('Failed to create relationship:', error);
      toast({
        title: "Creation Failed",
        description: "Failed to create relationship. Please try again.",
        variant: "destructive"
      });
    } finally {
      setCreating(false);
    }
  };

  const deleteRelationship = async (relationshipId: string) => {
    try {
      await relationshipAPI.delete(relationshipId);
      setRelationships(prev => prev.filter(rel => rel.id !== relationshipId));
      
      toast({
        title: "Relationship Deleted",
        description: "The relationship has been removed.",
      });

      if (onRelationshipChange) {
        onRelationshipChange();
      }
    } catch (error) {
      console.error('Failed to delete relationship:', error);
      toast({
        title: "Deletion Failed",
        description: "Failed to delete relationship. Please try again.",
        variant: "destructive"
      });
    }
  };

  const getCharacterName = (characterId: string) => {
    const character = characters.find(c => c.id === characterId);
    return character?.name || 'Unknown Character';
  };

  const getStrengthColor = (strength: number) => {
    if (strength >= 8) return 'bg-green-500';
    if (strength >= 6) return 'bg-yellow-500';
    if (strength >= 4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getStrengthText = (strength: number) => {
    if (strength >= 8) return 'Very Strong';
    if (strength >= 6) return 'Strong';
    if (strength >= 4) return 'Moderate';
    return 'Weak';
  };

  // Filter relationships for story characters if storyId is provided
  const filteredRelationships = storyId 
    ? relationships.filter(rel => 
        characters.some(c => c.id === rel.character1_id) && 
        characters.some(c => c.id === rel.character2_id)
      )
    : relationships;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Network className="w-5 h-5" />
            <span>Relationship Management</span>
          </DialogTitle>
          <DialogDescription>
            Create and manage character relationships to build rich story dynamics.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="view" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="view">View Relationships</TabsTrigger>
            <TabsTrigger value="create">Create Relationship</TabsTrigger>
          </TabsList>

          <TabsContent value="view" className="space-y-4">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                <span className="ml-2 text-muted-foreground">Loading relationships...</span>
              </div>
            ) : filteredRelationships.length === 0 ? (
              <div className="text-center py-12">
                <Heart className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-serif font-bold mb-2">No Relationships Yet</h3>
                <p className="text-muted-foreground mb-6">
                  {storyId ? 'Create relationships between your story characters to add depth.' : 'Start creating relationships between your characters.'}
                </p>
                <Button variant="outline" onClick={() => {}}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Relationship
                </Button>
              </div>
            ) : (
              <div className="grid gap-4">
                {filteredRelationships.map((relationship) => (
                  <Card key={relationship.id} className="relative">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline">
                              {getCharacterName(relationship.character1_id)}
                            </Badge>
                            <Heart className="w-4 h-4 text-primary" />
                            <Badge variant="outline">
                              {getCharacterName(relationship.character2_id)}
                            </Badge>
                          </div>
                          <Badge variant="secondary">{relationship.type}</Badge>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="flex items-center space-x-1">
                            <div 
                              className={`w-3 h-3 rounded-full ${getStrengthColor(relationship.strength)}`}
                            />
                            <span className="text-sm text-muted-foreground">
                              {getStrengthText(relationship.strength)} ({relationship.strength}/10)
                            </span>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteRelationship(relationship.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    {relationship.description && (
                      <CardContent className="pt-0">
                        <p className="text-sm text-muted-foreground">
                          {relationship.description}
                        </p>
                      </CardContent>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="create" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Create New Relationship</CardTitle>
                <CardDescription>
                  Define a relationship between two characters.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">First Character</label>
                    <Select
                      value={newRelationship.character1_id}
                      onValueChange={(value) => setNewRelationship(prev => ({ ...prev, character1_id: value }))}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select character" />
                      </SelectTrigger>
                      <SelectContent>
                        {characters.map((character) => (
                          <SelectItem key={character.id} value={character.id!}>
                            {character.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Second Character</label>
                    <Select
                      value={newRelationship.character2_id}
                      onValueChange={(value) => setNewRelationship(prev => ({ ...prev, character2_id: value }))}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select character" />
                      </SelectTrigger>
                      <SelectContent>
                        {characters
                          .filter(c => c.id !== newRelationship.character1_id)
                          .map((character) => (
                            <SelectItem key={character.id} value={character.id!}>
                              {character.name}
                            </SelectItem>
                          ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Relationship Type</label>
                    <Select
                      value={newRelationship.type}
                      onValueChange={(value) => setNewRelationship(prev => ({ ...prev, type: value }))}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        {relationshipTypes.map((type) => (
                          <SelectItem key={type} value={type}>
                            {type}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Strength (1-10)</label>
                    <Select
                      value={newRelationship.strength.toString()}
                      onValueChange={(value) => setNewRelationship(prev => ({ ...prev, strength: parseInt(value) }))}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: 10 }, (_, i) => i + 1).map((num) => (
                          <SelectItem key={num} value={num.toString()}>
                            {num} - {num >= 8 ? 'Very Strong' : num >= 6 ? 'Strong' : num >= 4 ? 'Moderate' : 'Weak'}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium">Description (Optional)</label>
                  <Textarea
                    value={newRelationship.description}
                    onChange={(e) => setNewRelationship(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe the relationship dynamics..."
                    className="mt-1"
                    rows={3}
                  />
                </div>

                <Button 
                  onClick={createRelationship} 
                  disabled={creating}
                  className="w-full"
                >
                  {creating ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Plus className="w-4 h-4 mr-2" />
                  )}
                  {creating ? 'Creating...' : 'Create Relationship'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
