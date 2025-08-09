// API configuration and client for connecting to the Story Assistant backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://story-assistant.onrender.com';

// Request helper function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`API Error ${response.status}: ${errorData}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
}

// Character API functions
export const characterAPI = {
  // Get all characters
  getAll: () => apiRequest<{ success: boolean; characters: Character[]; count: number }>('/characters/'),
  
  // Get specific character
  getById: (id: string) => apiRequest<{ success: boolean; character: Character }>(`/characters/${id}`),
  
  // Create new character
  create: (character: Omit<Character, 'id'>) => 
    apiRequest<{ success: boolean; character: Character }>('/characters/', {
      method: 'POST',
      body: JSON.stringify(character),
    }),
  
  // Update character
  update: (id: string, updates: Partial<Character>) =>
    apiRequest<{ success: boolean; character: Character }>(`/characters/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),
  
  // Delete character
  delete: (id: string) =>
    apiRequest<{ success: boolean }>(`/characters/${id}`, {
      method: 'DELETE',
    }),
  
  // Generate character backstory
  generateBackstory: (character: Character) =>
    apiRequest<{ success: boolean; character: Character; backstory: string }>('/characters/backstory/', {
      method: 'POST',
      body: JSON.stringify(character),
    }),
};

// Story API functions
export const storyAPI = {
  // Get all stories
  getAll: () => apiRequest<{ success: boolean; stories: string[]; count: number }>('/stories/'),
  
  // Get specific story
  getById: (id: string) => apiRequest<{ success: boolean; story: Story }>(`/stories/${id}`),
  
  // Create new story
  create: (storyData: StoryCreationRequest) =>
    apiRequest<{ success: boolean; story: Story }>('/stories/', {
      method: 'POST',
      body: JSON.stringify(storyData),
    }),
  
  // Update story
  update: (id: string, updates: Partial<Story>) =>
    apiRequest<{ success: boolean; story: Story }>(`/stories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),
  
  // Delete story
  delete: (id: string) =>
    apiRequest<{ success: boolean }>(`/stories/${id}`, {
      method: 'DELETE',
    }),
  
  // Add character to story
  addCharacter: (storyId: string, character: Character) =>
    apiRequest<{ success: boolean }>(`/stories/${storyId}/characters/`, {
      method: 'POST',
      body: JSON.stringify(character),
    }),
  
  // Generate story segment
  generateSegment: (request: StoryGenerationRequest) =>
    apiRequest<{ success: boolean; story: Story; new_segment?: any }>('/stories/generate/', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
  
  // Edit story segment
  editSegment: (request: StoryEditRequest) =>
    apiRequest<{ success: boolean; edited_content: string }>('/stories/edit/', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
  
  // Complete story
  complete: (id: string) =>
    apiRequest<{ success: boolean }>(`/stories/${id}/complete/`, {
      method: 'POST',
    }),
};

// Chapter API functions
export const chapterAPI = {
  // Get all chapters for a story
  getAll: (storyId: string) => 
    apiRequest<{ success: boolean; chapters: Chapter[]; count: number }>(`/stories/${storyId}/chapters/`),
  
  // Get specific chapter
  getById: (storyId: string, chapterId: string) =>
    apiRequest<{ success: boolean; chapter: Chapter }>(`/stories/${storyId}/chapters/${chapterId}`),
  
  // Create new chapter
  create: (storyId: string, chapterData: ChapterRequest) =>
    apiRequest<{ success: boolean; chapter: Chapter }>(`/stories/${storyId}/chapters/`, {
      method: 'POST',
      body: JSON.stringify(chapterData),
    }),
  
  // Update chapter
  update: (storyId: string, chapterId: string, updates: Partial<Chapter>) =>
    apiRequest<{ success: boolean; chapter: Chapter }>(`/stories/${storyId}/chapters/${chapterId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),
  
  // Delete chapter
  delete: (storyId: string, chapterId: string) =>
    apiRequest<{ success: boolean }>(`/stories/${storyId}/chapters/${chapterId}`, {
      method: 'DELETE',
    }),
  
  // Generate chapter content
  generateContent: (storyId: string, chapterId: string, targetLength: string = 'medium') =>
    apiRequest<{ success: boolean; chapter: Chapter }>(`/stories/${storyId}/chapters/${chapterId}/generate/`, {
      method: 'POST',
      body: JSON.stringify({ target_length: targetLength }),
    }),
};

// Relationship API functions
export const relationshipAPI = {
  // Get all relationships
  getAll: () => apiRequest<{ success: boolean; relationships: Relationship[]; count: number }>('/relationships/'),
  
  // Get specific relationship
  getById: (id: string) =>
    apiRequest<{ success: boolean; relationship: Relationship }>(`/relationships/${id}`),
  
  // Create new relationship
  create: (relationshipData: RelationshipRequest) =>
    apiRequest<{ success: boolean; relationship: Relationship }>('/relationships/', {
      method: 'POST',
      body: JSON.stringify(relationshipData),
    }),
  
  // Update relationship
  update: (id: string, updates: Partial<Relationship>) =>
    apiRequest<{ success: boolean; relationship: Relationship }>(`/relationships/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),
  
  // Delete relationship
  delete: (id: string) =>
    apiRequest<{ success: boolean }>(`/relationships/${id}`, {
      method: 'DELETE',
    }),
  
  // Get character relationships
  getCharacterRelationships: (characterId: string) =>
    apiRequest<{ success: boolean; relationships: Relationship[]; count: number }>(`/characters/${characterId}/relationships/`),
};

// Export API functions
export const exportAPI = {
  // Export story to PDF
  exportPDF: (storyId: string) =>
    apiRequest<Blob>(`/stories/${storyId}/export/pdf/`, {
      method: 'POST',
    }),
  
  // Export story to PDF as base64
  exportPDFBase64: (storyId: string) =>
    apiRequest<{ success: boolean; pdf_base64: string; filename: string }>(`/stories/${storyId}/export/pdf/base64/`, {
      method: 'POST',
    }),
  
  // Export story to audio
  exportAudio: (storyId: string, language: string = 'en') =>
    apiRequest<Blob>(`/stories/${storyId}/export/audio/?language=${language}`, {
      method: 'POST',
    }),
  
  // Export story to audio as base64
  exportAudioBase64: (storyId: string, language: string = 'en') =>
    apiRequest<{ success: boolean; audio_base64: string; filename: string; language: string }>(`/stories/${storyId}/export/audio/base64/?language=${language}`, {
      method: 'POST',
    }),
  
  // Get supported audio languages
  getSupportedLanguages: () =>
    apiRequest<{ success: boolean; languages: string[] }>('/export/audio/languages/'),
};

// Health check function
export const healthCheck = () =>
  apiRequest<{ status: string; message: string }>('/health/');

// Type definitions to match the backend models
export interface Character {
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
  backstory?: string;
}

export interface Story {
  id: string;
  title?: string;
  base_idea: string;
  theme: StoryTheme;
  characters: Character[];
  segments: any[];
  chapters: Chapter[];
  is_completed: boolean;
  is_draft: boolean;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: string;
  title: string;
  content: string;
  order: number;
  status: ChapterStatus;
  story_id: string;
  created_at: string;
  updated_at: string;
}

export interface Relationship {
  id: string;
  character1_id: string;
  character2_id: string;
  type: string;
  description: string;
  strength: number;
  created_at: string;
  updated_at: string;
}

// Request types
export interface StoryCreationRequest {
  base_idea: string;
  theme: StoryTheme;
  characters?: Character[];
}

export interface StoryGenerationRequest {
  story_id: string;
  theme: StoryTheme;
  characters: Character[];
  previous_content?: string;
  user_choice?: string;
  auto_continue?: boolean;
}

export interface StoryEditRequest {
  story_id: string;
  segment_id: string;
  original_content: string;
  edit_instruction: string;
  characters: Character[];
}

export interface ChapterRequest {
  title: string;
  content?: string;
  status?: ChapterStatus;
}

export interface RelationshipRequest {
  character1_id: string;
  character2_id: string;
  type: string;
  description: string;
  strength: number;
}

// Enums
export enum StoryTheme {
  ADVENTURE = "Adventure",
  ROMANCE = "Romance", 
  MYSTERY = "Mystery",
  FANTASY = "Fantasy",
  SCIFI = "Science Fiction",
  HORROR = "Horror",
  DRAMA = "Drama",
  COMEDY = "Comedy",
  THRILLER = "Thriller",
  HISTORICAL = "Historical"
}

export enum ChapterStatus {
  DRAFT = "draft",
  IN_PROGRESS = "in_progress", 
  COMPLETED = "completed",
  PUBLISHED = "published"
}

export enum PersonalityType {
  BRAVE = "brave",
  SHY = "shy",
  CLEVER = "clever",
  KIND = "kind",
  MYSTERIOUS = "mysterious",
  AMBITIOUS = "ambitious",
  LOYAL = "loyal",
  REBELLIOUS = "rebellious"
}

export default {
  characterAPI,
  storyAPI,
  chapterAPI,
  relationshipAPI,
  exportAPI,
  healthCheck,
};
