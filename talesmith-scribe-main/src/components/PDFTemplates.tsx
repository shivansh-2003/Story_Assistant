import React from 'react';
import { Document, Page, Text, View, StyleSheet, Font, Image } from '@react-pdf/renderer';

// Professional PDF styles
const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    padding: 40,
    fontFamily: 'Helvetica',
  },
  coverPage: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a2e',
    color: '#FFFFFF',
  },
  title: {
    fontSize: 32,
    marginBottom: 20,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#4f46e5',
  },
  subtitle: {
    fontSize: 18,
    marginBottom: 10,
    textAlign: 'center',
    color: '#64748b',
  },
  coverTitle: {
    fontSize: 40,
    marginBottom: 30,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#FFFFFF',
  },
  coverSubtitle: {
    fontSize: 20,
    marginBottom: 20,
    textAlign: 'center',
    color: '#e2e8f0',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
    paddingBottom: 10,
    borderBottomWidth: 2,
    borderBottomColor: '#4f46e5',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#1e293b',
    backgroundColor: '#f1f5f9',
    padding: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#4f46e5',
  },
  text: {
    fontSize: 11,
    lineHeight: 1.5,
    marginBottom: 6,
    color: '#374151',
  },
  characterName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
    color: '#1e293b',
  },
  characterRole: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 20,
    backgroundColor: '#e0e7ff',
    padding: 8,
    borderRadius: 4,
    color: '#3730a3',
  },
  infoGrid: {
    flexDirection: 'row',
    marginBottom: 15,
  },
  infoLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    width: 80,
    color: '#475569',
  },
  infoValue: {
    fontSize: 12,
    flex: 1,
    color: '#1e293b',
  },
  relationshipCard: {
    backgroundColor: '#f8fafc',
    padding: 12,
    marginBottom: 10,
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#4f46e5',
  },
  relationshipHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  relationshipType: {
    fontSize: 10,
    fontWeight: 'bold',
    backgroundColor: '#4f46e5',
    color: '#FFFFFF',
    padding: 4,
    borderRadius: 3,
  },
  chapterTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
    color: '#1e293b',
    backgroundColor: '#f1f5f9',
    padding: 12,
  },
  chapterContent: {
    fontSize: 12,
    lineHeight: 1.6,
    textAlign: 'justify',
    color: '#374151',
  },
  pageNumber: {
    position: 'absolute',
    fontSize: 10,
    bottom: 30,
    left: 0,
    right: 0,
    textAlign: 'center',
    color: '#64748b',
  },
  watermark: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%) rotate(-45deg)',
    fontSize: 80,
    color: '#f1f5f9',
    zIndex: -1,
  },
});

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

// Professional Character Profile PDF
export const CharacterProfilePDF = ({ character, relationships, allCharacters }: {
  character: Character;
  relationships: Relationship[];
  allCharacters: Character[];
}) => (
  <Document>
    {/* Cover Page */}
    <Page size="A4" style={styles.coverPage}>
      <Text style={styles.coverTitle}>CHARACTER PROFILE</Text>
      <Text style={styles.coverSubtitle}>{character.name}</Text>
      <Text style={{ fontSize: 14, color: '#cbd5e1' }}>{character.archetype}</Text>
    </Page>

    {/* Profile Page */}
    <Page size="A4" style={styles.page}>
      <View style={styles.header}>
        <Text style={{ fontSize: 14, fontWeight: 'bold' }}>CHARACTER DOSSIER</Text>
        <Text style={{ fontSize: 10, color: '#64748b' }}>
          Generated on {new Date().toLocaleDateString()}
        </Text>
      </View>

      <Text style={styles.characterName}>{character.name}</Text>
      <Text style={styles.characterRole}>{character.role} • {character.archetype}</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>BASIC INFORMATION</Text>
        <View style={styles.infoGrid}>
          <Text style={styles.infoLabel}>Age:</Text>
          <Text style={styles.infoValue}>{character.age} years old</Text>
        </View>
        <View style={styles.infoGrid}>
          <Text style={styles.infoLabel}>Role:</Text>
          <Text style={styles.infoValue}>{character.role}</Text>
        </View>
        <View style={styles.infoGrid}>
          <Text style={styles.infoLabel}>Archetype:</Text>
          <Text style={styles.infoValue}>{character.archetype}</Text>
        </View>
      </View>

      {character.personality && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>PERSONALITY</Text>
          <Text style={styles.text}>{character.personality}</Text>
        </View>
      )}

      {character.background && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>BACKGROUND</Text>
          <Text style={styles.text}>{character.background}</Text>
        </View>
      )}

      {character.appearance && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>PHYSICAL APPEARANCE</Text>
          <Text style={styles.text}>{character.appearance}</Text>
        </View>
      )}

      {character.motivation && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>MOTIVATION & GOALS</Text>
          <Text style={styles.text}>{character.motivation}</Text>
        </View>
      )}

      <Text style={styles.pageNumber}>Page 1 of 2</Text>
    </Page>

    {/* Relationships Page */}
    {relationships.length > 0 && (
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={{ fontSize: 14, fontWeight: 'bold' }}>CHARACTER RELATIONSHIPS</Text>
          <Text style={{ fontSize: 10, color: '#64748b' }}>{character.name}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>RELATIONSHIP NETWORK</Text>
          {relationships.map((rel) => {
            const otherCharId = rel.character1Id === character.id ? rel.character2Id : rel.character1Id;
            const otherChar = allCharacters.find(c => c.id === otherCharId);
            
            return (
              <View key={rel.id} style={styles.relationshipCard}>
                <View style={styles.relationshipHeader}>
                  <Text style={{ fontSize: 12, fontWeight: 'bold' }}>
                    {otherChar?.name || 'Unknown Character'}
                  </Text>
                  <Text style={styles.relationshipType}>{rel.type}</Text>
                </View>
                {rel.description && (
                  <Text style={{ fontSize: 10, color: '#475569', fontStyle: 'italic' }}>
                    "{rel.description}"
                  </Text>
                )}
                <Text style={{ fontSize: 9, color: '#64748b', marginTop: 4 }}>
                  Strength: {rel.strength}/10
                </Text>
              </View>
            );
          })}
        </View>

        <Text style={styles.pageNumber}>Page 2 of 2</Text>
      </Page>
    )}
  </Document>
);

// Professional Story PDF
export const StoryPDF = ({ story, characters }: {
  story: Story;
  characters: Character[];
}) => (
  <Document>
    {/* Title Page */}
    <Page size="A4" style={styles.coverPage}>
      <Text style={styles.coverTitle}>{story.title}</Text>
      <Text style={styles.coverSubtitle}>{story.genre}</Text>
      {story.description && (
        <Text style={{ fontSize: 14, color: '#cbd5e1', textAlign: 'center', marginTop: 20, maxWidth: 400 }}>
          {story.description}
        </Text>
      )}
      <Text style={{ fontSize: 12, color: '#94a3b8', marginTop: 40 }}>
        {story.chapters.length} Chapters • {story.chapters.reduce((total, ch) => total + ch.wordCount, 0).toLocaleString()} Words
      </Text>
    </Page>

    {/* Characters Page */}
    {characters.length > 0 && (
      <Page size="A4" style={styles.page}>
        <Text style={styles.title}>DRAMATIS PERSONAE</Text>
        {characters.map((character, index) => (
          <View key={character.id} style={{
            ...styles.section,
            backgroundColor: index % 2 === 0 ? '#f8fafc' : 'transparent',
            padding: 12,
            borderRadius: 6,
          }}>
            <View style={{
              flexDirection: 'row',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 4,
            }}>
              <Text style={{ fontSize: 14, fontWeight: 'bold' }}>{character.name}</Text>
              <Text style={{
                fontSize: 10,
                backgroundColor: '#4f46e5',
                color: '#FFFFFF',
                padding: 4,
                borderRadius: 3,
              }}>
                {character.role}
              </Text>
            </View>
            <Text style={{ fontSize: 10, color: '#64748b', marginBottom: 4 }}>
              {character.archetype}
            </Text>
            {character.personality && (
              <Text style={{ fontSize: 10, color: '#374151' }}>
                {character.personality.length > 150 
                  ? character.personality.substring(0, 150) + '...'
                  : character.personality
                }
              </Text>
            )}
          </View>
        ))}
      </Page>
    )}

    {/* Story Chapters */}
    {story.chapters.map((chapter, index) => (
      <Page key={chapter.id} size="A4" style={styles.page}>
        <Text style={styles.chapterTitle}>{chapter.title}</Text>
        <Text style={styles.chapterContent}>{chapter.content}</Text>
        <Text style={styles.pageNumber}>
          Chapter {index + 1} • Page {index + (characters.length > 0 ? 3 : 2)}
        </Text>
      </Page>
    ))}
  </Document>
);

// Relationship Network PDF
export const RelationshipNetworkPDF = ({ characters, relationships }: {
  characters: Character[];
  relationships: Relationship[];
}) => (
  <Document>
    <Page size="A4" style={styles.coverPage}>
      <Text style={styles.coverTitle}>RELATIONSHIP NETWORK</Text>
      <Text style={styles.coverSubtitle}>Character Dynamics & Connections</Text>
      <Text style={{ fontSize: 14, color: '#cbd5e1', marginTop: 20 }}>
        {characters.length} Characters • {relationships.length} Relationships
      </Text>
    </Page>

    <Page size="A4" style={styles.page}>
      <Text style={styles.title}>CHARACTER OVERVIEW</Text>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>CAST OF CHARACTERS</Text>
        {characters.map((character) => (
          <View key={character.id} style={styles.infoGrid}>
            <Text style={{ ...styles.infoLabel, width: 120 }}>{character.name}:</Text>
            <Text style={styles.infoValue}>{character.role} ({character.archetype})</Text>
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>RELATIONSHIP DYNAMICS</Text>
        {relationships.map((rel) => {
          const char1 = characters.find(c => c.id === rel.character1Id);
          const char2 = characters.find(c => c.id === rel.character2Id);
          
          return (
            <View key={rel.id} style={styles.relationshipCard}>
              <View style={styles.relationshipHeader}>
                <Text style={{ fontSize: 12, fontWeight: 'bold' }}>
                  {char1?.name || 'Unknown'} ⇄ {char2?.name || 'Unknown'}
                </Text>
                <Text style={styles.relationshipType}>{rel.type}</Text>
              </View>
              {rel.description && (
                <Text style={{ fontSize: 10, color: '#475569', fontStyle: 'italic', marginTop: 4 }}>
                  "{rel.description}"
                </Text>
              )}
              <View style={{
                flexDirection: 'row',
                justifyContent: 'space-between',
                marginTop: 6,
                paddingTop: 6,
                borderTopWidth: 1,
                borderTopColor: '#e2e8f0',
              }}>
                <Text style={{ fontSize: 9, color: '#64748b' }}>
                  Strength: {rel.strength}/10
                </Text>
                <Text style={{ fontSize: 9, color: '#64748b' }}>
                  {rel.type === 'Romantic' ? '💕' : 
                   rel.type === 'Enemy' ? '⚔️' : 
                   rel.type === 'Family' ? '👑' : 
                   rel.type === 'Friend' ? '🤝' : '👥'}
                </Text>
              </View>
            </View>
          );
        })}
      </View>

      <Text style={styles.pageNumber}>Relationship Network Analysis</Text>
    </Page>
  </Document>
);