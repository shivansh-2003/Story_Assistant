import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

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

export const exportCharacterProfile = async (character: Character): Promise<void> => {
  const pdf = new jsPDF();
  const pageWidth = pdf.internal.pageSize.getWidth();
  let yPosition = 20;

  // Title
  pdf.setFontSize(20);
  pdf.setFont('helvetica', 'bold');
  pdf.text('Character Profile', pageWidth / 2, yPosition, { align: 'center' });
  yPosition += 20;

  // Character Name
  pdf.setFontSize(16);
  pdf.text(character.name, pageWidth / 2, yPosition, { align: 'center' });
  yPosition += 15;

  // Basic Info
  pdf.setFontSize(12);
  pdf.setFont('helvetica', 'normal');
  const basicInfo = [
    `Age: ${character.age}`,
    `Role: ${character.role}`,
    `Archetype: ${character.archetype}`
  ];

  basicInfo.forEach(info => {
    pdf.text(info, 20, yPosition);
    yPosition += 8;
  });

  yPosition += 10;

  // Sections
  const sections = [
    { title: 'Personality', content: character.personality },
    { title: 'Background', content: character.background },
    { title: 'Appearance', content: character.appearance },
    { title: 'Motivation', content: character.motivation }
  ];

  sections.forEach(section => {
    if (section.content) {
      pdf.setFont('helvetica', 'bold');
      pdf.text(section.title + ':', 20, yPosition);
      yPosition += 8;

      pdf.setFont('helvetica', 'normal');
      const lines = pdf.splitTextToSize(section.content, pageWidth - 40);
      pdf.text(lines, 20, yPosition);
      yPosition += lines.length * 6 + 10;
    }
  });

  // Relationships
  if (character.relationships.length > 0) {
    pdf.setFont('helvetica', 'bold');
    pdf.text('Relationships:', 20, yPosition);
    yPosition += 8;

    pdf.setFont('helvetica', 'normal');
    character.relationships.forEach(relationship => {
      pdf.text(`• ${relationship}`, 25, yPosition);
      yPosition += 6;
    });
  }

  pdf.save(`${character.name.replace(/\s+/g, '_')}_Profile.pdf`);
};

export const exportAllCharacters = async (characters: Character[]): Promise<void> => {
  const pdf = new jsPDF();
  let pageNum = 1;

  characters.forEach((character, index) => {
    if (index > 0) {
      pdf.addPage();
      pageNum++;
    }

    const pageWidth = pdf.internal.pageSize.getWidth();
    let yPosition = 20;

    // Title
    pdf.setFontSize(18);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Character Profile', pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 15;

    // Character Name
    pdf.setFontSize(14);
    pdf.text(character.name, pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 12;

    // Basic Info
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    const basicInfo = [
      `Age: ${character.age} | Role: ${character.role} | Archetype: ${character.archetype}`
    ];

    basicInfo.forEach(info => {
      pdf.text(info, pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 8;
    });

    yPosition += 8;

    // Sections
    const sections = [
      { title: 'Personality', content: character.personality },
      { title: 'Background', content: character.background },
      { title: 'Appearance', content: character.appearance },
      { title: 'Motivation', content: character.motivation }
    ];

    sections.forEach(section => {
      if (section.content) {
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(11);
        pdf.text(section.title + ':', 20, yPosition);
        yPosition += 6;

        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(10);
        const lines = pdf.splitTextToSize(section.content, pageWidth - 40);
        pdf.text(lines, 20, yPosition);
        yPosition += lines.length * 5 + 6;
      }
    });

    // Page number
    pdf.setFontSize(8);
    pdf.text(`Page ${pageNum}`, pageWidth - 30, pdf.internal.pageSize.getHeight() - 10);
  });

  pdf.save('Character_Profiles.pdf');
};

export const exportStory = async (story: Story): Promise<void> => {
  const pdf = new jsPDF();
  let pageNum = 1;

  // Title Page
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  
  pdf.setFontSize(24);
  pdf.setFont('helvetica', 'bold');
  pdf.text(story.title, pageWidth / 2, pageHeight / 2 - 20, { align: 'center' });
  
  pdf.setFontSize(14);
  pdf.setFont('helvetica', 'normal');
  pdf.text(story.genre, pageWidth / 2, pageHeight / 2, { align: 'center' });
  
  if (story.description) {
    pdf.setFontSize(12);
    const descLines = pdf.splitTextToSize(story.description, pageWidth - 60);
    pdf.text(descLines, pageWidth / 2, pageHeight / 2 + 20, { align: 'center' });
  }

  // Chapters
  story.chapters.forEach((chapter, index) => {
    pdf.addPage();
    pageNum++;

    let yPosition = 30;

    // Chapter Title
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text(chapter.title, pageWidth / 2, yPosition, { align: 'center' });
    yPosition += 20;

    // Chapter Content
    if (chapter.content) {
      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'normal');
      const contentLines = pdf.splitTextToSize(chapter.content, pageWidth - 40);
      
      contentLines.forEach((line: string) => {
        if (yPosition > pageHeight - 30) {
          pdf.addPage();
          pageNum++;
          yPosition = 30;
        }
        pdf.text(line, 20, yPosition);
        yPosition += 6;
      });
    }

    // Page number
    pdf.setFontSize(8);
    pdf.text(`Page ${pageNum}`, pageWidth - 30, pageHeight - 10);
  });

  pdf.save(`${story.title.replace(/\s+/g, '_')}.pdf`);
};

export const exportCharacterRelationships = async (
  characters: Character[],
  relationships: any[]
): Promise<void> => {
  const pdf = new jsPDF();
  const pageWidth = pdf.internal.pageSize.getWidth();
  let yPosition = 20;

  // Title
  pdf.setFontSize(18);
  pdf.setFont('helvetica', 'bold');
  pdf.text('Character Relationships', pageWidth / 2, yPosition, { align: 'center' });
  yPosition += 20;

  // Character List
  pdf.setFontSize(14);
  pdf.text('Characters:', 20, yPosition);
  yPosition += 10;

  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'normal');
  characters.forEach(character => {
    pdf.text(`• ${character.name} (${character.role})`, 25, yPosition);
    yPosition += 6;
  });

  yPosition += 10;

  // Relationships
  pdf.setFontSize(14);
  pdf.setFont('helvetica', 'bold');
  pdf.text('Relationships:', 20, yPosition);
  yPosition += 10;

  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'normal');
  relationships.forEach(rel => {
    const char1 = characters.find(c => c.id === rel.character1Id)?.name || 'Unknown';
    const char2 = characters.find(c => c.id === rel.character2Id)?.name || 'Unknown';
    
    pdf.text(`${char1} ⇄ ${char2} (${rel.type})`, 25, yPosition);
    yPosition += 6;
    
    if (rel.description) {
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'italic');
      const descLines = pdf.splitTextToSize(`"${rel.description}"`, pageWidth - 60);
      pdf.text(descLines, 30, yPosition);
      yPosition += descLines.length * 5 + 3;
      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'normal');
    }
    
    yPosition += 3;
  });

  pdf.save('Character_Relationships.pdf');
};