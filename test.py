

import pytest
import requests
import json
import time
from typing import Dict, Any
import base64

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.story_id = None
        self.segment_ids = []
        self.characters = []
        self.character_ids = []
        self.chapter_ids = []
        self.relationship_ids = []
        self.created_characters = []
        
    def test_health_check(self):
        """Test API health endpoint"""
        print("🔍 Testing health check...")
        try:
            response = requests.get(f"{self.base_url}/health/")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            print("✅ Health check passed")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_create_characters(self):
        """Test character creation"""
        print("\n👤 Testing character creation...")
        
        characters_data = [
            {
                "name": "Elena Brightblade",
                "age": 25,
                "occupation": "Royal Mage",
                "primary_trait": "brave",
                "secondary_trait": "wise",
                "fatal_flaw": "Overconfident in her abilities",
                "motivation": "To prove herself worthy of the royal court",
                "appearance": "A tall woman with silver hair and piercing blue eyes, wearing elegant robes",
                "speaking_style": "formal",
                "special_abilities": ["Fire magic", "Telepathy"],
                "relationships": ["Marcus (childhood friend)"]
            },
            {
                "name": "Marcus Ironheart",
                "age": 30,
                "occupation": "Knight Captain",
                "primary_trait": "aggressive",
                "secondary_trait": "brave",
                "fatal_flaw": "Quick to anger",
                "motivation": "To protect the innocent at all costs",
                "appearance": "A muscular man with dark hair and battle scars",
                "speaking_style": "casual",
                "special_abilities": ["Swordsmanship", "Leadership"],
                "relationships": ["Elena (childhood friend)"]
            }
        ]
        
        try:
            for char_data in characters_data:
                response = requests.post(f"{self.base_url}/characters/", json=char_data)
                if response.status_code != 200:
                    print(f"❌ Character creation failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
                result = response.json()
                assert result["success"] == True
                assert result["character"]["name"] == char_data["name"]
                self.characters.append(char_data)
                self.created_characters.append(result["character"])
                self.character_ids.append(result["character"]["id"])
                print(f"✅ Character {char_data['name']} created with ID: {result['character']['id']}")
            return True
        except Exception as e:
            print(f"❌ Character creation failed: {e}")
            return False
    
    def test_debug_llm_service(self):
        """Debug LLM service status"""
        print("\n🔍 Testing LLM service debug info...")
        try:
            response = requests.get(f"{self.base_url}/debug/llm/")
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                debug_info = response.json()
                print(f"LLM Service Type: {debug_info.get('llm_service_type', 'Unknown')}")
                print(f"Service is None: {debug_info.get('llm_service_is_none', 'Unknown')}")
                print(f"Has generate method: {debug_info.get('has_generate_method', 'Unknown')}")
            else:
                print(f"Debug endpoint failed: {response.text}")
            return True
        except Exception as e:
            print(f"❌ Debug test failed: {e}")
            return False
    
    def test_generate_backstories(self):
        """Test character backstory generation"""
        print("\n📚 Testing backstory generation...")
        
        for char in self.characters:
            try:
                response = requests.post(f"{self.base_url}/characters/backstory/", json=char)
                print(f"Response status for {char['name']}: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Backstory generation failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                
                result = response.json()
                if not result.get("success", False):
                    print(f"❌ Backstory generation returned success=False")
                    print(f"Response: {result}")
                    return False
                
                if "backstory" not in result or len(result["backstory"]) < 50:
                    print(f"❌ Invalid backstory returned: {result.get('backstory', 'None')}")
                    return False
                    
                print(f"✅ Backstory generated for {char['name']}")
                print(f"   Preview: {result['backstory'][:100]}...")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed for {char['name']}: {e}")
                return False
            except Exception as e:
                print(f"❌ Unexpected error for {char['name']}: {e}")
                return False
        
        return True
    
    def test_create_story(self):
        """Test story creation"""
        print("\n📖 Testing story creation...")
        
        story_data = {
            "base_idea": "In the mystical kingdom of Aethermoor, an ancient evil stirs beneath the Crystal Caves. Two unlikely heroes must unite their powers to prevent the realm from falling into eternal darkness.",
            "theme": "fantasy",
            "characters": self.characters
        }
        
        try:
            response = requests.post(f"{self.base_url}/stories/", json=story_data)
            if response.status_code != 200:
                print(f"❌ Story creation failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Story creation returned success=False: {result}")
                return False
            
            self.story_id = result["story"]["id"]
            print(f"✅ Story created with ID: {self.story_id}")
            return True
            
        except Exception as e:
            print(f"❌ Story creation failed: {e}")
            return False
    
    def test_get_story(self):
        """Test story retrieval"""
        print("\n📋 Testing story retrieval...")
        
        try:
            response = requests.get(f"{self.base_url}/stories/{self.story_id}")
            if response.status_code != 200:
                print(f"❌ Story retrieval failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Story retrieval returned success=False: {result}")
                return False
                
            assert result["story"]["id"] == self.story_id
            assert result["story"]["theme"] == "fantasy"
            print("✅ Story retrieved successfully")
            return True
            
        except Exception as e:
            print(f"❌ Story retrieval failed: {e}")
            return False
    
    def test_add_character_to_story(self):
        """Test adding character to existing story"""
        print("\n➕ Testing add character to story...")
        
        new_character = {
            "name": "Zara Shadowdancer",
            "age": 22,
            "occupation": "Rogue",
            "primary_trait": "cunning",
            "appearance": "A lithe figure with dark hair and green eyes",
            "motivation": "To find her missing brother"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/stories/{self.story_id}/characters/", 
                json=new_character
            )
            if response.status_code != 200:
                print(f"❌ Add character failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Add character returned success=False: {result}")
                return False
                
            print(f"✅ Character {new_character['name']} added to story")
            return True
            
        except Exception as e:
            print(f"❌ Add character failed: {e}")
            return False
    
    def test_generate_story_with_user_choice(self):
        """Test story generation with user input"""
        print("\n✍️ Testing story generation with user choice...")
        
        generation_request = {
            "story_id": self.story_id,
            "theme": "fantasy",
            "characters": self.characters,
            "previous_content": "In the mystical kingdom of Aethermoor, an ancient evil stirs beneath the Crystal Caves.",
            "user_choice": "Elena discovers a glowing map hidden in the royal library that shows the location of three ancient artifacts needed to seal the evil.",
            "auto_continue": False
        }
        
        try:
            response = requests.post(f"{self.base_url}/stories/generate/", json=generation_request)
            print(f"Story generation response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Story generation failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Story generation returned success=False")
                print(f"Response: {result}")
                return False
            
            if "new_segment" not in result or not result["new_segment"].get("content"):
                print(f"❌ No content in generated segment: {result}")
                return False
            
            self.segment_ids.append(result["new_segment"]["id"])
            print("✅ Story segment generated with user choice")
            print(f"   Content preview: {result['new_segment']['content'][:100]}...")
            return True
            
        except Exception as e:
            print(f"❌ Story generation failed: {e}")
            return False
    
    def test_edit_story_segment(self):
        """Test story segment editing"""
        print("\n✏️ Testing story segment editing...")
        
        if not self.segment_ids:
            print("❌ No segments available for editing")
            return False
        
        try:
            # Get current story to get segment content
            response = requests.get(f"{self.base_url}/stories/{self.story_id}")
            if response.status_code != 200:
                print(f"❌ Failed to get story for editing: {response.status_code}")
                return False
                
            current_story = response.json()["story"]
            if not current_story["segments"]:
                print("❌ No segments found in story for editing")
                return False
                
            segment_content = current_story["segments"][0]["content"]
            
            edit_request = {
                "story_id": self.story_id,
                "segment_id": self.segment_ids[0],
                "edit_instruction": "Add more dramatic tension and include dialogue between Elena and Marcus discussing their fears about the upcoming quest.",
                "original_content": segment_content,
                "characters": self.characters
            }
            
            response = requests.post(f"{self.base_url}/stories/edit/", json=edit_request)
            print(f"Edit response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Story edit failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Story edit returned success=False: {result}")
                return False
            
            if "edited_content" not in result:
                print(f"❌ No edited content returned: {result}")
                return False
                
            print("✅ Story segment edited successfully")
            print(f"   Edit preview: {result['edited_content'][:100]}...")
            return True
            
        except Exception as e:
            print(f"❌ Story edit failed: {e}")
            return False
    
    def test_auto_continue_story(self):
        """Test automatic story continuation"""
        print("\n🤖 Testing automatic story continuation...")
        
        try:
            # Get current story content
            response = requests.get(f"{self.base_url}/stories/{self.story_id}")
            if response.status_code != 200:
                print(f"❌ Failed to get story for auto-continue: {response.status_code}")
                return False
                
            current_story = response.json()["story"]
            full_content = " ".join([seg["content"] for seg in current_story["segments"]])
            
            auto_request = {
                "story_id": self.story_id,
                "theme": "fantasy",
                "characters": self.characters,
                "previous_content": full_content,
                "auto_continue": True
            }
            
            response = requests.post(f"{self.base_url}/stories/generate/", json=auto_request)
            print(f"Auto-continue response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Auto-continue failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Auto-continue returned success=False: {result}")
                return False
            
            if "new_segment" not in result:
                print(f"❌ No new segment in auto-continue: {result}")
                return False
            
            self.segment_ids.append(result["new_segment"]["id"])
            print("✅ Auto-continuation generated")
            print(f"   Content preview: {result['new_segment']['content'][:100]}...")
            return True
            
        except Exception as e:
            print(f"❌ Auto-continue failed: {e}")
            return False
    
    def test_complete_story(self):
        """Test story completion"""
        print("\n🏁 Testing story completion...")
        
        try:
            response = requests.post(f"{self.base_url}/stories/{self.story_id}/complete/")
            if response.status_code != 200:
                print(f"❌ Story completion failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Story completion returned success=False: {result}")
                return False
                
            print("✅ Story marked as completed")
            return True
            
        except Exception as e:
            print(f"❌ Story completion failed: {e}")
            return False
    
    def test_export_pdf_base64(self):
        """Test PDF export as base64"""
        print("\n📄 Testing PDF export (base64)...")
        
        try:
            response = requests.post(f"{self.base_url}/stories/{self.story_id}/export/pdf/base64/")
            print(f"PDF base64 export status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ PDF base64 export failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            result = response.json()
            if not result.get("success", False):
                print(f"❌ PDF export returned success=False: {result}")
                return False
            
            if "pdf_base64" not in result or len(result["pdf_base64"]) < 1000:
                print(f"❌ Invalid PDF base64 data: {len(result.get('pdf_base64', ''))}")
                return False
            
            # Validate base64 format
            try:
                base64.b64decode(result["pdf_base64"])
                print("✅ PDF generated and base64 encoded successfully")
                return True
            except Exception as e:
                print(f"❌ Invalid base64 PDF: {e}")
                return False
                
        except Exception as e:
            print(f"❌ PDF base64 export failed: {e}")
            return False
    
    def test_export_pdf_direct(self):
        """Test direct PDF download"""
        print("\n📁 Testing PDF direct download...")
        
        try:
            response = requests.post(f"{self.base_url}/stories/{self.story_id}/export/pdf/")
            print(f"PDF direct export status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ PDF direct export failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            if response.headers.get("content-type") != "application/pdf":
                print(f"❌ Wrong content type: {response.headers.get('content-type')}")
                return False
            
            if len(response.content) < 1000:
                print(f"❌ PDF too small: {len(response.content)} bytes")
                return False
                
            print("✅ PDF direct download successful")
            return True
            
        except Exception as e:
            print(f"❌ PDF direct export failed: {e}")
            return False
    
    def test_list_stories(self):
        """Test listing all stories"""
        print("\n📚 Testing story listing...")
        
        try:
            response = requests.get(f"{self.base_url}/stories/")
            if response.status_code != 200:
                print(f"❌ Story listing failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Story listing returned success=False: {result}")
                return False
            
            if "stories" not in result or self.story_id not in result["stories"]:
                print(f"❌ Current story not in list: {result}")
                return False
                
            print(f"✅ Found {result['count']} stories in system")
            return True
            
        except Exception as e:
            print(f"❌ Story listing failed: {e}")
            return False
    
    def test_error_cases(self):
        """Test error handling"""
        print("\n⚠️ Testing error cases...")
        
        try:
            # Test non-existent story
            response = requests.get(f"{self.base_url}/stories/nonexistent-id")
            if response.status_code != 404:
                print(f"❌ Expected 404 for non-existent story, got {response.status_code}")
                return False
            
            # Test non-existent character
            response = requests.get(f"{self.base_url}/characters/nonexistent-id")
            if response.status_code != 404:
                print(f"❌ Expected 404 for non-existent character, got {response.status_code}")
                return False
            
            # Test non-existent chapter
            response = requests.get(f"{self.base_url}/stories/{self.story_id}/chapters/nonexistent-id")
            if response.status_code != 404:
                print(f"❌ Expected 404 for non-existent chapter, got {response.status_code}")
                return False
            
            # Test non-existent relationship
            response = requests.get(f"{self.base_url}/relationships/nonexistent-id")
            if response.status_code != 404:
                print(f"❌ Expected 404 for non-existent relationship, got {response.status_code}")
                return False
            
            # Test invalid edit request
            invalid_edit = {
                "story_id": "invalid",
                "segment_id": "invalid",
                "edit_instruction": "test",
                "original_content": "test"
            }
            response = requests.post(f"{self.base_url}/stories/edit/", json=invalid_edit)
            if response.status_code != 404:
                print(f"❌ Expected 404 for invalid edit, got {response.status_code}")
                return False
            
            # Test creating relationship with non-existent characters
            invalid_relationship = {
                "character1_id": "nonexistent1",
                "character2_id": "nonexistent2",
                "type": "friend",
                "description": "test"
            }
            response = requests.post(f"{self.base_url}/relationships/", json=invalid_relationship)
            if response.status_code != 404:
                print(f"❌ Expected 404 for relationship with non-existent characters, got {response.status_code}")
                return False
            
            # Test updating non-existent character
            response = requests.put(f"{self.base_url}/characters/nonexistent-id", json={"age": 30})
            if response.status_code != 404:
                print(f"❌ Expected 404 for updating non-existent character, got {response.status_code}")
                return False
            
            # Test deleting non-existent chapter
            print(f"Testing delete with story_id: {self.story_id}")
            non_existent_chapter_id = "99999999-9999-9999-9999-999999999999"
            url = f"{self.base_url}/stories/{self.story_id}/chapters/{non_existent_chapter_id}"
            print(f"DEBUG: Calling DELETE {url}")
            response = requests.delete(url)
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            if response.status_code != 404:
                print(f"❌ Expected 404 for deleting non-existent chapter, got {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            # Test deleting chapter from non-existent story
            response = requests.delete(f"{self.base_url}/stories/nonexistent-story-id/chapters/{non_existent_chapter_id}")
            if response.status_code != 404:
                print(f"❌ Expected 404 for deleting chapter from non-existent story, got {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            print("✅ Error handling working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Error case testing failed: {e}")
            return False
    
    # Extended Character Management Tests
    def test_list_characters(self):
        """Test listing all characters"""
        print("\n👥 Testing character listing...")
        
        try:
            response = requests.get(f"{self.base_url}/characters/")
            if response.status_code != 200:
                print(f"❌ Character listing failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Character listing returned success=False: {result}")
                return False
            
            if "characters" not in result or len(result["characters"]) < len(self.character_ids):
                print(f"❌ Expected at least {len(self.character_ids)} characters, got {len(result.get('characters', []))}")
                return False
                
            print(f"✅ Found {result['count']} characters in system")
            return True
            
        except Exception as e:
            print(f"❌ Character listing failed: {e}")
            return False
    
    def test_get_character(self):
        """Test getting specific character"""
        print("\n🎭 Testing character retrieval...")
        
        if not self.character_ids:
            print("⚠️ Skipping character retrieval - no characters available")
            return True
        
        try:
            character_id = self.character_ids[0]
            response = requests.get(f"{self.base_url}/characters/{character_id}")
            if response.status_code != 200:
                print(f"❌ Character retrieval failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Character retrieval returned success=False: {result}")
                return False
            
            if result["character"]["id"] != character_id:
                print(f"❌ Retrieved wrong character: expected {character_id}, got {result['character']['id']}")
                return False
                
            print(f"✅ Character {result['character']['name']} retrieved successfully")
            return True
            
        except Exception as e:
            print(f"❌ Character retrieval failed: {e}")
            return False
    
    def test_update_character(self):
        """Test updating character details"""
        print("\n✏️ Testing character update...")
        
        if not self.character_ids:
            print("⚠️ Skipping character update - no characters available")
            return True
        
        try:
            character_id = self.character_ids[0]
            update_data = {
                "motivation": "Updated motivation: To save the world from ancient darkness",
                "age": 26,
                "personality": "Brave, determined, and slightly reckless in pursuit of justice"
            }
            
            response = requests.put(f"{self.base_url}/characters/{character_id}", json=update_data)
            if response.status_code != 200:
                print(f"❌ Character update failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Character update returned success=False: {result}")
                return False
            
            if result["character"]["motivation"] != update_data["motivation"]:
                print(f"❌ Character update failed: motivation not updated")
                return False
                
            print("✅ Character updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Character update failed: {e}")
            return False
    
    # Chapter Management Tests
    def test_create_chapters(self):
        """Test creating chapters in story"""
        print("\n📖 Testing chapter creation...")
        
        if not self.story_id:
            print("❌ No story ID available for chapter testing")
            return False
        
        try:
            chapters_data = [
                {
                    "title": "Chapter 1: The Awakening",
                    "content": "In the mystical kingdom of Aethermoor, Elena Brightblade felt the ancient magic stirring...",
                    "status": "completed"
                },
                {
                    "title": "Chapter 2: The Discovery",
                    "content": "",
                    "status": "draft"
                },
                {
                    "title": "Chapter 3: The Quest Begins",
                    "content": "Marcus Ironheart joined Elena as they prepared to venture into the unknown...",
                    "status": "in-progress"
                }
            ]
            
            for chapter_data in chapters_data:
                response = requests.post(f"{self.base_url}/stories/{self.story_id}/chapters/", json=chapter_data)
                if response.status_code != 200:
                    print(f"❌ Chapter creation failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
                result = response.json()
                if not result.get("success", False):
                    print(f"❌ Chapter creation returned success=False: {result}")
                    return False
                
                self.chapter_ids.append(result["chapter"]["id"])
                print(f"✅ Chapter created: {chapter_data['title']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Chapter creation failed: {e}")
            return False
            
    def test_list_chapters(self):
        """Test listing story chapters"""
        print("\n📚 Testing chapter listing...")
        
        try:
            response = requests.get(f"{self.base_url}/stories/{self.story_id}/chapters/")
            if response.status_code != 200:
                print(f"❌ Chapter listing failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Chapter listing returned success=False: {result}")
                return False
            
            if len(result["chapters"]) != len(self.chapter_ids):
                print(f"❌ Expected {len(self.chapter_ids)} chapters, got {len(result['chapters'])}")
                return False
                
            print(f"✅ Found {result['count']} chapters in story")
            return True
            
        except Exception as e:
            print(f"❌ Chapter listing failed: {e}")
            return False
    
    def test_get_chapter(self):
        """Test getting specific chapter"""
        print("\n📄 Testing chapter retrieval...")
        
        if not self.chapter_ids:
            print("❌ No chapter IDs available for testing")
            return False
        
        try:
            chapter_id = self.chapter_ids[0]
            response = requests.get(f"{self.base_url}/stories/{self.story_id}/chapters/{chapter_id}")
            if response.status_code != 200:
                print(f"❌ Chapter retrieval failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Chapter retrieval returned success=False: {result}")
                return False
            
            if result["chapter"]["id"] != chapter_id:
                print(f"❌ Retrieved wrong chapter")
                return False
                
            print(f"✅ Chapter retrieved: {result['chapter']['title']}")
            return True
                
        except Exception as e:
            print(f"❌ Chapter retrieval failed: {e}")
            return False
    
    def test_update_chapter(self):
        """Test updating chapter content"""
        print("\n✏️ Testing chapter update...")
        
        if not self.chapter_ids:
            print("❌ No chapter IDs available for testing")
            return False
        
        try:
            chapter_id = self.chapter_ids[1]  # Use the empty chapter
            update_data = {
                "title": "Chapter 2: The Discovery",
                "content": "The ancient library held secrets that Elena had never imagined. As she touched the glowing tome, visions of the past flooded her mind...",
                "status": "in-progress"
            }
            
            response = requests.put(f"{self.base_url}/stories/{self.story_id}/chapters/{chapter_id}", json=update_data)
            if response.status_code != 200:
                print(f"❌ Chapter update failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Chapter update returned success=False: {result}")
                return False
            
            if not result["chapter"]["content"]:
                print(f"❌ Chapter content not updated")
                return False
                
            print("✅ Chapter updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Chapter update failed: {e}")
            return False
    
    def test_generate_chapter_content(self):
        """Test AI chapter content generation"""
        print("\n🤖 Testing AI chapter generation...")
        
        if not self.chapter_ids:
            print("❌ No chapter IDs available for testing")
            return False
        
        try:
            # Use the last chapter for generation
            chapter_id = self.chapter_ids[-1]
            response = requests.post(f"{self.base_url}/stories/{self.story_id}/chapters/{chapter_id}/generate/?target_length=short")
            print(f"Chapter generation response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Chapter generation failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Chapter generation returned success=False: {result}")
                return False
            
            if not result["chapter"]["content"] or len(result["chapter"]["content"]) < 100:
                print(f"❌ Generated content too short or empty")
                return False
                
            print("✅ Chapter content generated successfully")
            print(f"   Content preview: {result['chapter']['content'][:100]}...")
            return True
            
        except Exception as e:
            print(f"❌ Chapter generation failed: {e}")
            return False
    
    # Relationship Management Tests
    def test_create_relationships(self):
        """Test creating character relationships"""
        print("\n💫 Testing relationship creation...")
        
        if len(self.character_ids) < 2:
            print("⚠️ Skipping relationship testing - need at least 2 characters")
            return True  # Return True to not fail the test, just skip it
        
        try:
            relationships_data = [
                {
                    "character1_id": self.character_ids[0],
                    "character2_id": self.character_ids[1],
                    "type": "childhood friend",
                    "description": "Elena and Marcus grew up together in the royal academy",
                    "strength": 8
                },
                {
                    "character1_id": self.character_ids[1],
                    "character2_id": self.character_ids[0],
                    "type": "trusted ally",
                    "description": "Marcus trusts Elena's magical abilities completely",
                    "strength": 9
                }
            ]
            
            for rel_data in relationships_data:
                response = requests.post(f"{self.base_url}/relationships/", json=rel_data)
                if response.status_code != 200:
                    print(f"❌ Relationship creation failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
                result = response.json()
                if not result.get("success", False):
                    print(f"❌ Relationship creation returned success=False: {result}")
                    return False
                
                self.relationship_ids.append(result["relationship"]["id"])
                print(f"✅ Relationship created: {rel_data['type']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Relationship creation failed: {e}")
            return False
    
    def test_list_relationships(self):
        """Test listing all relationships"""
        print("\n🔗 Testing relationship listing...")
        
        try:
            response = requests.get(f"{self.base_url}/relationships/")
            if response.status_code != 200:
                print(f"❌ Relationship listing failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Relationship listing returned success=False: {result}")
                return False
            
            if len(result["relationships"]) < len(self.relationship_ids):
                print(f"❌ Expected at least {len(self.relationship_ids)} relationships")
                return False
                
            print(f"✅ Found {result['count']} relationships in system")
            return True
            
        except Exception as e:
            print(f"❌ Relationship listing failed: {e}")
            return False
    
    def test_get_character_relationships(self):
        """Test getting relationships for specific character"""
        print("\n🎭 Testing character relationship retrieval...")
        
        if not self.character_ids:
            print("⚠️ Skipping character relationship retrieval - no characters available")
            return True
        
        try:
            character_id = self.character_ids[0]
            response = requests.get(f"{self.base_url}/characters/{character_id}/relationships/")
            if response.status_code != 200:
                print(f"❌ Character relationships failed with status {response.status_code}")
                return False
            
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Character relationships returned success=False: {result}")
                return False
            
            print(f"✅ Found {result['count']} relationships for character")
            return True
            
        except Exception as e:
            print(f"❌ Character relationships failed: {e}")
            return False
    
    # Story Management Tests
    def test_update_story(self):
        """Test updating story details"""
        print("\n📝 Testing story update...")
        
        if not self.story_id:
            print("❌ No story ID available for testing")
            return False
        
        try:
            update_data = {
                "title": "The Crystal Chronicles: Awakening",
                "genre": "Epic Fantasy",
                "description": "An epic tale of magic, friendship, and the battle against ancient darkness",
                "setting": "The mystical kingdom of Aethermoor",
                "target_audience": "Young Adult",
                "is_draft": False
            }
            
            response = requests.put(f"{self.base_url}/stories/{self.story_id}", json=update_data)
            if response.status_code != 200:
                print(f"❌ Story update failed with status {response.status_code}")
                return False
            
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Story update returned success=False: {result}")
                return False
            
            if result["story"]["title"] != update_data["title"]:
                print(f"❌ Story title not updated correctly")
                return False
                
            print("✅ Story updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Story update failed: {e}")
            return False
    
    def test_save_draft(self):
        """Test saving story as draft"""
        print("\n💾 Testing draft save...")
        
        try:
            response = requests.post(f"{self.base_url}/stories/{self.story_id}/draft/")
            if response.status_code != 200:
                print(f"❌ Draft save failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Draft save returned success=False: {result}")
                return False
                
            print("✅ Story saved as draft")
            return True
            
        except Exception as e:
            print(f"❌ Draft save failed: {e}")
            return False
    
    def test_list_drafts(self):
        """Test listing draft stories"""
        print("\n📄 Testing draft listing...")
        
        try:
            response = requests.get(f"{self.base_url}/drafts/")
            if response.status_code != 200:
                print(f"❌ Draft listing failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Draft listing returned success=False: {result}")
                return False
            
            # Should find at least our story since we saved it as draft
            draft_ids = [draft["id"] for draft in result["drafts"]]
            if self.story_id not in draft_ids:
                print(f"❌ Our story not found in drafts")
                return False
                
            print(f"✅ Found {result['count']} draft stories")
            return True
            
        except Exception as e:
            print(f"❌ Draft listing failed: {e}")
            return False
    
    # Cleanup Tests
    def test_delete_chapter(self):
        """Test deleting a chapter"""
        print("\n🗑️ Testing chapter deletion...")
        
        if not self.chapter_ids:
            print("❌ No chapter IDs available for deletion testing")
            return False
        
        try:
            # Delete the last chapter
            chapter_id = self.chapter_ids[-1]
            response = requests.delete(f"{self.base_url}/stories/{self.story_id}/chapters/{chapter_id}")
            if response.status_code != 200:
                print(f"❌ Chapter deletion failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Chapter deletion returned success=False: {result}")
                return False
                
            print("✅ Chapter deleted successfully")
            self.chapter_ids.remove(chapter_id)  # Remove from our tracking
            return True
            
        except Exception as e:
            print(f"❌ Chapter deletion failed: {e}")
            return False
    
    def test_delete_relationship(self):
        """Test deleting a relationship"""
        print("\n💔 Testing relationship deletion...")
        
        if not self.relationship_ids:
            print("⚠️ Skipping relationship deletion - no relationships available")
            return True
        
        try:
            relationship_id = self.relationship_ids[0]
            response = requests.delete(f"{self.base_url}/relationships/{relationship_id}")
            if response.status_code != 200:
                print(f"❌ Relationship deletion failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Relationship deletion returned success=False: {result}")
                return False
                
            print("✅ Relationship deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Relationship deletion failed: {e}")
            return False
    
    def test_delete_character(self):
        """Test deleting a character"""
        print("\n👻 Testing character deletion...")
        
        if len(self.character_ids) < 2:
            print("⚠️ Skipping character deletion - need at least 2 characters")
            return True
        
        try:
            # Delete the last character
            character_id = self.character_ids[-1]
            response = requests.delete(f"{self.base_url}/characters/{character_id}")
            if response.status_code != 200:
                print(f"❌ Character deletion failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Character deletion returned success=False: {result}")
                return False
                
            print("✅ Character deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Character deletion failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting comprehensive API testing...\n")
        
        tests = [
            # Basic health and setup
            self.test_health_check,
            self.test_debug_llm_service,
            
            # Character management tests
            self.test_create_characters,
            self.test_list_characters,
            self.test_get_character,
            self.test_update_character,
            self.test_generate_backstories,
            
            # Story creation and basic management
            self.test_create_story,
            self.test_get_story,
            self.test_update_story,
            self.test_add_character_to_story,
            
            # Chapter management tests
            self.test_create_chapters,
            self.test_list_chapters,
            self.test_get_chapter,
            self.test_update_chapter,
            self.test_generate_chapter_content,
            
            # Relationship management tests
            self.test_create_relationships,
            self.test_list_relationships,
            self.test_get_character_relationships,
            
            # Story generation and editing (existing functionality)
            self.test_generate_story_with_user_choice,
            self.test_edit_story_segment,
            self.test_auto_continue_story,
            
            # Draft management
            self.test_save_draft,
            self.test_list_drafts,
            
            # Story completion
            self.test_complete_story,
            
            # Export functionality
            self.test_export_pdf_base64,
            self.test_export_pdf_direct,
            
            # Listing and cleanup tests
            self.test_list_stories,
            self.test_delete_chapter,
            self.test_delete_relationship,
            self.test_delete_character,
            
            # Error handling
            self.test_error_cases
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
                    print(f"❌ {test.__name__} failed")
            except Exception as e:
                failed += 1
                print(f"❌ {test.__name__} failed with error: {e}")
            
            time.sleep(0.5)  # Small delay between tests
        
        print(f"\n📊 Test Results:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 All tests passed! API is fully functional.")
            print("✅ Tested endpoints:")
            print("   • Character Management (CRUD + Backstory)")
            print("   • Chapter Management (CRUD + AI Generation)")
            print("   • Relationship Management (CRUD)")
            print("   • Story Management (CRUD + Generation + Editing)")
            print("   • Draft Management")
            print("   • PDF Export Services")
            print("   • Error Handling")
        else:
            print(f"\n⚠️ {failed} tests failed. Check the logs above for details.")
        
        return failed == 0

def run_performance_test(base_url: str = "http://localhost:8000"):
    """Test API performance under load"""
    print("\n⚡ Running performance tests...")
    
    import concurrent.futures
    import time
    
    def make_health_request():
        start = time.time()
        response = requests.get(f"{base_url}/health/")
        end = time.time()
        return response.status_code == 200, end - start
    
    # Test concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_health_request) for _ in range(20)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    success_count = sum(1 for success, _ in results if success)
    avg_time = sum(time for _, time in results) / len(results)
    
    print(f"✅ Concurrent requests: {success_count}/20 successful")
    print(f"⏱️ Average response time: {avg_time:.3f}s")

if __name__ == "__main__":
    print("🧪 Interactive Storytelling API Comprehensive Test Suite")
    print("=" * 60)
    print("Testing 25+ API endpoints:")
    print("• Character Management (CRUD + AI)")
    print("• Chapter Management (CRUD + AI)")  
    print("• Relationship Management (CRUD)")
    print("• Story Management (CRUD + AI)")
    print("• Draft & PDF Export Services")
    print("=" * 60)
    
    # Initialize tester
    tester = APITester()
    
    # Run comprehensive tests
    success = tester.run_comprehensive_test()
    
    # Run performance tests if basic tests pass
    if success:
        run_performance_test()
    
    print("\n🏁 Testing completed!")