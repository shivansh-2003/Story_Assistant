import React, { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { Download, FileText, Users, Network, Palette, Settings } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";
import { pdf } from '@react-pdf/renderer';
import { CharacterProfilePDF, StoryPDF, RelationshipNetworkPDF } from './PDFTemplates';

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

interface Relationship {
  id: string;
  character1Id: string;
  character2Id: string;
  type: string;
  description: string;
  strength: number;
}

interface Story {
  title: string;
  genre: string;
  description: string;
  chapters: {
    id: string;
    title: string;
    content: string;
    wordCount: number;
  }[];
}

interface PDFExportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  characters: Character[];
  relationships: Relationship[];
  story?: Story;
  exportType: 'character' | 'story' | 'relationships' | 'all';
  selectedCharacter?: Character;
}

export const PDFExportDialog = ({
  open,
  onOpenChange,
  characters,
  relationships,
  story,
  exportType,
  selectedCharacter
}: PDFExportDialogProps) => {
  const { toast } = useToast();
  const [exportOptions, setExportOptions] = useState({
    template: 'professional',
    includeRelationships: true,
    includeCharacters: true,
    colorScheme: 'default',
    selectedCharacterIds: [] as string[]
  });

  const templates = [
    {
      id: 'professional',
      name: 'Professional',
      description: 'Clean, business-style layout with structured sections',
      icon: <FileText className="w-5 h-5" />
    },
    {
      id: 'creative',
      name: 'Creative',
      description: 'Artistic design with decorative elements',
      icon: <Palette className="w-5 h-5" />
    },
    {
      id: 'minimal',
      name: 'Minimal',
      description: 'Simple, clean design focusing on content',
      icon: <Settings className="w-5 h-5" />
    }
  ];

  const colorSchemes = [
    { id: 'default', name: 'Indigo Blue', primary: '#4f46e5' },
    { id: 'emerald', name: 'Emerald Green', primary: '#059669' },
    { id: 'rose', name: 'Rose Pink', primary: '#e11d48' },
    { id: 'amber', name: 'Amber Gold', primary: '#d97706' }
  ];

  const handleExport = async () => {
    try {
      toast({
        title: "Generating PDF...",
        description: "Your professional PDF is being created.",
      });

      let pdfDocument;
      let filename = "export.pdf";

      switch (exportType) {
        case 'character':
          if (selectedCharacter) {
            const charRelationships = relationships.filter(rel => 
              rel.character1Id === selectedCharacter.id || rel.character2Id === selectedCharacter.id
            );
            pdfDocument = pdf(<CharacterProfilePDF 
              character={selectedCharacter} 
              relationships={charRelationships}
              allCharacters={characters}
            />);
            filename = `${selectedCharacter.name.replace(/\s+/g, '_')}_Profile.pdf`;
          }
          break;

        case 'story':
          if (story) {
            const storyCharacters = characters.filter(char => 
              exportOptions.selectedCharacterIds.length === 0 || 
              exportOptions.selectedCharacterIds.includes(char.id)
            );
            pdfDocument = pdf(<StoryPDF story={story} characters={storyCharacters} />);
            filename = `${story.title.replace(/\s+/g, '_')}.pdf`;
          }
          break;

        case 'relationships':
          pdfDocument = pdf(<RelationshipNetworkPDF 
            characters={characters} 
            relationships={relationships} 
          />);
          filename = "Character_Relationships.pdf";
          break;

        case 'all':
          // For now, export as relationship network
          pdfDocument = pdf(<RelationshipNetworkPDF 
            characters={characters} 
            relationships={relationships} 
          />);
          filename = "Complete_Character_Guide.pdf";
          break;
      }

      if (pdfDocument) {
        const blob = await pdfDocument.toBlob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        toast({
          title: "PDF Downloaded!",
          description: "Your professional PDF has been generated and downloaded.",
        });

        onOpenChange(false);
      }
    } catch (error) {
      console.error('PDF export error:', error);
      toast({
        title: "Export Failed",
        description: "There was an error generating your PDF. Please try again.",
        variant: "destructive"
      });
    }
  };

  const getExportTitle = () => {
    switch (exportType) {
      case 'character': return selectedCharacter ? `Export ${selectedCharacter.name}` : 'Export Character';
      case 'story': return story ? `Export "${story.title}"` : 'Export Story';
      case 'relationships': return 'Export Relationship Network';
      case 'all': return 'Export Complete Guide';
      default: return 'Export PDF';
    }
  };

  const getExportDescription = () => {
    switch (exportType) {
      case 'character': return 'Generate a professional character profile with relationships and detailed information.';
      case 'story': return 'Create a beautifully formatted story document with chapters and character information.';
      case 'relationships': return 'Export a comprehensive relationship network showing all character connections.';
      case 'all': return 'Generate a complete guide including all characters, relationships, and story content.';
      default: return 'Choose your export options and generate a professional PDF.';
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Download className="w-5 h-5" />
            <span>{getExportTitle()}</span>
          </DialogTitle>
          <DialogDescription>{getExportDescription()}</DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Template Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Template Style</CardTitle>
              <CardDescription>Choose the design template for your PDF</CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup 
                value={exportOptions.template} 
                onValueChange={(value) => setExportOptions(prev => ({ ...prev, template: value }))}
              >
                {templates.map((template) => (
                  <div key={template.id} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-muted/50">
                    <RadioGroupItem value={template.id} id={template.id} />
                    <Label htmlFor={template.id} className="flex-1 cursor-pointer">
                      <div className="flex items-start space-x-3">
                        {template.icon}
                        <div>
                          <div className="font-medium">{template.name}</div>
                          <div className="text-sm text-muted-foreground">{template.description}</div>
                        </div>
                      </div>
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </CardContent>
          </Card>

          {/* Color Scheme */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Color Scheme</CardTitle>
              <CardDescription>Select the primary color for your PDF</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                {colorSchemes.map((scheme) => (
                  <div
                    key={scheme.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-all ${
                      exportOptions.colorScheme === scheme.id 
                        ? 'border-primary bg-primary/5' 
                        : 'hover:bg-muted/50'
                    }`}
                    onClick={() => setExportOptions(prev => ({ ...prev, colorScheme: scheme.id }))}
                  >
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full" 
                        style={{ backgroundColor: scheme.primary }}
                      />
                      <span className="font-medium">{scheme.name}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Content Options */}
          {(exportType === 'story' || exportType === 'all') && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Content Options</CardTitle>
                <CardDescription>Choose what to include in your export</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="includeCharacters"
                    checked={exportOptions.includeCharacters}
                    onCheckedChange={(checked) => 
                      setExportOptions(prev => ({ ...prev, includeCharacters: checked as boolean }))
                    }
                  />
                  <Label htmlFor="includeCharacters">Include character profiles</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="includeRelationships"
                    checked={exportOptions.includeRelationships}
                    onCheckedChange={(checked) => 
                      setExportOptions(prev => ({ ...prev, includeRelationships: checked as boolean }))
                    }
                  />
                  <Label htmlFor="includeRelationships">Include relationship network</Label>
                </div>

                {characters.length > 0 && (
                  <div className="space-y-2">
                    <Label>Select Characters to Include:</Label>
                    <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                      {characters.map((character) => (
                        <div key={character.id} className="flex items-center space-x-2">
                          <Checkbox
                            id={character.id}
                            checked={
                              exportOptions.selectedCharacterIds.length === 0 || 
                              exportOptions.selectedCharacterIds.includes(character.id)
                            }
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setExportOptions(prev => ({
                                  ...prev,
                                  selectedCharacterIds: [...prev.selectedCharacterIds, character.id]
                                }));
                              } else {
                                setExportOptions(prev => ({
                                  ...prev,
                                  selectedCharacterIds: prev.selectedCharacterIds.filter(id => id !== character.id)
                                }));
                              }
                            }}
                          />
                          <Label htmlFor={character.id} className="text-sm">
                            {character.name}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Export Summary */}
          <Card className="bg-primary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="text-lg flex items-center space-x-2">
                <FileText className="w-5 h-5" />
                <span>Export Summary</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span>Template:</span>
                  <Badge variant="outline">
                    {templates.find(t => t.id === exportOptions.template)?.name}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Color Scheme:</span>
                  <Badge variant="outline">
                    {colorSchemes.find(c => c.id === exportOptions.colorScheme)?.name}
                  </Badge>
                </div>
                {exportType === 'character' && selectedCharacter && (
                  <div className="flex items-center justify-between">
                    <span>Character:</span>
                    <Badge>{selectedCharacter.name}</Badge>
                  </div>
                )}
                {exportType === 'story' && story && (
                  <div className="flex items-center justify-between">
                    <span>Story:</span>
                    <Badge>{story.title}</Badge>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span>Pages:</span>
                  <Badge variant="secondary">
                    {exportType === 'character' ? '2-3' : 
                     exportType === 'story' ? `${story?.chapters.length ? story.chapters.length + 2 : 3}+` :
                     exportType === 'relationships' ? '2-3' : '5+'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Separator />

        <div className="flex justify-end space-x-3">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleExport} className="flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Generate PDF</span>
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};