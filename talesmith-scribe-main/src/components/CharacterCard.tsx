import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Crown, Heart, Sword, Star, Edit, Trash2 } from 'lucide-react';

interface Character {
  id: string;
  name: string;
  age: number;
  role: string;
  personality: string;
  background: string;
  appearance: string;
  motivation: string;
  archetype: string;
  relationships: string[];
}

interface CharacterCardProps {
  character: Character;
  onDelete: () => void;
}

const CharacterCard: React.FC<CharacterCardProps> = ({ character, onDelete }) => {
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
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <Edit className="w-3 h-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onDelete}
              className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:text-destructive"
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
  );
};

export default CharacterCard;