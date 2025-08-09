import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { X, Plus, Heart, Sword, Users, Crown, Shield } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";
import { Character } from '@/lib/api';

interface Relationship {
  id: string;
  character1Id: string;
  character2Id: string;
  type: string;
  description: string;
  strength: number;
}

interface RelationshipMappingProps {
  characters: Character[];
  onClose?: () => void;
}

const RelationshipMapping = ({ characters, onClose }: RelationshipMappingProps) => {
  const { toast } = useToast();
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [isAddingRelationship, setIsAddingRelationship] = useState(false);
  const [newRelationship, setNewRelationship] = useState({
    character1Id: '',
    character2Id: '',
    type: '',
    description: '',
    strength: 5
  });

  const relationshipTypes = [
    'Ally', 'Enemy', 'Romantic', 'Family', 'Mentor', 'Rival', 'Friend', 'Neutral'
  ];

  const getRelationshipIcon = (type: string) => {
    switch (type) {
      case 'Romantic': return <Heart className="w-4 h-4 text-red-500" />;
      case 'Enemy': case 'Rival': return <Sword className="w-4 h-4 text-red-600" />;
      case 'Friend': case 'Ally': return <Users className="w-4 h-4 text-blue-500" />;
      case 'Family': return <Crown className="w-4 h-4 text-purple-500" />;
      case 'Mentor': return <Shield className="w-4 h-4 text-green-500" />;
      default: return <Users className="w-4 h-4 text-gray-500" />;
    }
  };

  const addRelationship = () => {
    if (!newRelationship.character1Id || !newRelationship.character2Id || !newRelationship.type) {
      toast({
        title: "Missing Information",
        description: "Please select both characters and relationship type.",
        variant: "destructive"
      });
      return;
    }

    if (newRelationship.character1Id === newRelationship.character2Id) {
      toast({
        title: "Invalid Relationship",
        description: "A character cannot have a relationship with themselves.",
        variant: "destructive"
      });
      return;
    }

    const relationship: Relationship = {
      id: Date.now().toString(),
      ...newRelationship
    };

    setRelationships(prev => [...prev, relationship]);
    setNewRelationship({
      character1Id: '',
      character2Id: '',
      type: '',
      description: '',
      strength: 5
    });
    setIsAddingRelationship(false);

    toast({
      title: "Relationship Added",
      description: "Character relationship has been mapped successfully.",
    });
  };

  const removeRelationship = (id: string) => {
    setRelationships(prev => prev.filter(rel => rel.id !== id));
    toast({
      title: "Relationship Removed",
      description: "Character relationship has been removed.",
    });
  };

  const getCharacterName = (id: string) => {
    return characters.find(char => char.id === id)?.name || 'Unknown';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-serif font-bold">Relationship Mapping</h2>
          <p className="text-muted-foreground">Visualize and manage character relationships</p>
        </div>
        <div className="flex items-center space-x-2">
          <Dialog open={isAddingRelationship} onOpenChange={setIsAddingRelationship}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Plus className="w-4 h-4 mr-2" />
                Add Relationship
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Character Relationship</DialogTitle>
                <DialogDescription>
                  Define how two characters relate to each other
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>First Character</Label>
                    <Select onValueChange={(value) => setNewRelationship(prev => ({ ...prev, character1Id: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select character" />
                      </SelectTrigger>
                      <SelectContent>
                        {characters.map((character) => (
                          <SelectItem key={character.id} value={character.id}>
                            {character.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Second Character</Label>
                    <Select onValueChange={(value) => setNewRelationship(prev => ({ ...prev, character2Id: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select character" />
                      </SelectTrigger>
                      <SelectContent>
                        {characters.map((character) => (
                          <SelectItem key={character.id} value={character.id}>
                            {character.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Relationship Type</Label>
                  <Select onValueChange={(value) => setNewRelationship(prev => ({ ...prev, type: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select relationship type" />
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

                <div className="space-y-2">
                  <Label>Description</Label>
                  <Input
                    placeholder="Describe their relationship..."
                    value={newRelationship.description}
                    onChange={(e) => setNewRelationship(prev => ({ ...prev, description: e.target.value }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Relationship Strength (1-10)</Label>
                  <Input
                    type="number"
                    min="1"
                    max="10"
                    value={newRelationship.strength}
                    onChange={(e) => setNewRelationship(prev => ({ ...prev, strength: parseInt(e.target.value) || 5 }))}
                  />
                </div>

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsAddingRelationship(false)}>
                    Cancel
                  </Button>
                  <Button onClick={addRelationship}>
                    Add Relationship
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {characters.length < 2 ? (
        <Card>
          <CardContent className="text-center py-8">
            <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="font-medium mb-2">Need More Characters</h3>
            <p className="text-muted-foreground">
              Create at least 2 characters to start mapping relationships.
            </p>
          </CardContent>
        </Card>
      ) : relationships.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <Heart className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="font-medium mb-2">No Relationships Yet</h3>
            <p className="text-muted-foreground mb-4">
              Start mapping how your characters relate to each other.
            </p>
            <Button variant="outline" onClick={() => setIsAddingRelationship(true)}>
              Create First Relationship
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {relationships.map((relationship) => (
            <Card key={relationship.id} className="bg-card/50 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getRelationshipIcon(relationship.type)}
                    <Badge variant="outline">{relationship.type}</Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeRelationship(relationship.id)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{getCharacterName(relationship.character1Id)}</span>
                    <span className="text-muted-foreground">⇄</span>
                    <span className="font-medium">{getCharacterName(relationship.character2Id)}</span>
                  </div>
                  
                  {relationship.description && (
                    <p className="text-sm text-muted-foreground">{relationship.description}</p>
                  )}
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">Strength:</span>
                    <div className="flex items-center space-x-1">
                      {Array.from({ length: 10 }, (_, i) => (
                        <div
                          key={i}
                          className={`w-2 h-2 rounded-full ${
                            i < relationship.strength ? 'bg-primary' : 'bg-muted'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-xs font-medium">{relationship.strength}/10</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default RelationshipMapping;