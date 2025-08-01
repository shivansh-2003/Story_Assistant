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
        
    def test_health_check(self):
        """Test API health endpoint"""
        print("🔍 Testing health check...")
        response = requests.get(f"{self.base_url}/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")
        return True
    
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
                "relationships": {"Marcus": "childhood friend"}
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
                "relationships": {"Elena": "childhood friend"}
            }
        ]
        
        for char_data in characters_data:
            response = requests.post(f"{self.base_url}/characters/", json=char_data)
            assert response.status_code == 200
            result = response.json()
            assert result["success"] == True
            assert result["character"]["name"] == char_data["name"]
            self.characters.append(char_data)
            print(f"✅ Character {char_data['name']} created")
        
        return True
    
    def test_generate_backstories(self):
        """Test character backstory generation"""
        print("\n📚 Testing backstory generation...")
        
        for char in self.characters:
            response = requests.post(f"{self.base_url}/characters/backstory/", json=char)
            assert response.status_code == 200
            result = response.json()
            assert result["success"] == True
            assert "backstory" in result
            assert len(result["backstory"]) > 50  # Ensure meaningful backstory
            print(f"✅ Backstory generated for {char['name']}")
        
        return True
    
    def test_create_story(self):
        """Test story creation"""
        print("\n📖 Testing story creation...")
        
        story_data = {
            "base_idea": "In the mystical kingdom of Aethermoor, an ancient evil stirs beneath the Crystal Caves. Two unlikely heroes must unite their powers to prevent the realm from falling into eternal darkness.",
            "theme": "fantasy",
            "characters": self.characters
        }
        
        response = requests.post(f"{self.base_url}/stories/", json=story_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "story" in result
        
        self.story_id = result["story"]["id"]
        assert len(self.story_id) > 0
        print(f"✅ Story created with ID: {self.story_id}")
        
        return True
    
    def test_get_story(self):
        """Test story retrieval"""
        print("\n📋 Testing story retrieval...")
        
        response = requests.get(f"{self.base_url}/stories/{self.story_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert result["story"]["id"] == self.story_id
        assert result["story"]["theme"] == "fantasy"
        print("✅ Story retrieved successfully")
        
        return True
    
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
        
        response = requests.post(
            f"{self.base_url}/stories/{self.story_id}/characters/", 
            json=new_character
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        print(f"✅ Character {new_character['name']} added to story")
        
        return True
    
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
        
        response = requests.post(f"{self.base_url}/stories/generate/", json=generation_request)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "new_segment" in result
        assert len(result["new_segment"]["content"]) > 100
        
        self.segment_ids.append(result["new_segment"]["id"])
        print("✅ Story segment generated with user choice")
        print(f"   Content preview: {result['new_segment']['content'][:100]}...")
        
        return True
    
    def test_edit_story_segment(self):
        """Test story segment editing"""
        print("\n✏️ Testing story segment editing...")
        
        if not self.segment_ids:
            print("❌ No segments available for editing")
            return False
        
        # Get current story to get segment content
        response = requests.get(f"{self.base_url}/stories/{self.story_id}")
        current_story = response.json()["story"]
        segment_content = current_story["segments"][0]["content"]
        
        edit_request = {
            "story_id": self.story_id,
            "segment_id": self.segment_ids[0],
            "edit_instruction": "Add more dramatic tension and include dialogue between Elena and Marcus discussing their fears about the upcoming quest.",
            "original_content": segment_content,
            "characters": self.characters
        }
        
        response = requests.post(f"{self.base_url}/stories/edit/", json=edit_request)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "edited_content" in result
        assert result["edited_content"] != result["original_content"]
        print("✅ Story segment edited successfully")
        print(f"   Edit preview: {result['edited_content'][:100]}...")
        
        return True
    
    def test_auto_continue_story(self):
        """Test automatic story continuation"""
        print("\n🤖 Testing automatic story continuation...")
        
        # Get current story content
        response = requests.get(f"{self.base_url}/stories/{self.story_id}")
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
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "new_segment" in result
        
        self.segment_ids.append(result["new_segment"]["id"])
        print("✅ Auto-continuation generated")
        print(f"   Content preview: {result['new_segment']['content'][:100]}...")
        
        return True
    
    def test_complete_story(self):
        """Test story completion"""
        print("\n🏁 Testing story completion...")
        
        response = requests.post(f"{self.base_url}/stories/{self.story_id}/complete/")
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        print("✅ Story marked as completed")
        
        return True
    
    def test_export_pdf_base64(self):
        """Test PDF export as base64"""
        print("\n📄 Testing PDF export (base64)...")
        
        response = requests.post(f"{self.base_url}/stories/{self.story_id}/export/pdf/base64/")
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "pdf_base64" in result
        assert len(result["pdf_base64"]) > 1000  # Ensure substantial PDF content
        
        # Validate base64 format
        try:
            base64.b64decode(result["pdf_base64"])
            print("✅ PDF generated and base64 encoded successfully")
        except Exception as e:
            print(f"❌ Invalid base64 PDF: {e}")
            return False
        
        return True
    
    def test_export_pdf_direct(self):
        """Test direct PDF download"""
        print("\n📁 Testing PDF direct download...")
        
        response = requests.post(f"{self.base_url}/stories/{self.story_id}/export/pdf/")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 1000
        print("✅ PDF direct download successful")
        
        return True
    
    def test_get_audio_languages(self):
        """Test getting supported audio languages"""
        print("\n🌍 Testing audio language support...")
        
        response = requests.get(f"{self.base_url}/export/audio/languages/")
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "languages" in result
        assert len(result["languages"]) >= 5  # Should have multiple languages
        print(f"✅ Found {len(result['languages'])} supported languages")
        
        return True
    
    def test_export_audio_base64(self):
        """Test audio export as base64"""
        print("\n🎵 Testing audio export (base64)...")
        
        response = requests.post(f"{self.base_url}/stories/{self.story_id}/export/audio/base64/?language=en")
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "audio_base64" in result
        assert len(result["audio_base64"]) > 1000
        
        # Validate base64 format
        try:
            base64.b64decode(result["audio_base64"])
            print("✅ Audio generated and base64 encoded successfully")
        except Exception as e:
            print(f"❌ Invalid base64 audio: {e}")
            return False
        
        return True
    
    def test_export_audio_direct(self):
        """Test direct audio download"""
        print("\n🎧 Testing audio direct download...")
        
        response = requests.post(f"{self.base_url}/stories/{self.story_id}/export/audio/?language=en")
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert len(response.content) > 1000
        print("✅ Audio direct download successful")
        
        return True
    
    def test_list_stories(self):
        """Test listing all stories"""
        print("\n📚 Testing story listing...")
        
        response = requests.get(f"{self.base_url}/stories/")
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "stories" in result
        assert self.story_id in result["stories"]
        print(f"✅ Found {result['count']} stories in system")
        
        return True
    
    def test_error_cases(self):
        """Test error handling"""
        print("\n⚠️ Testing error cases...")
        
        # Test non-existent story
        response = requests.get(f"{self.base_url}/stories/nonexistent-id")
        assert response.status_code == 404
        
        # Test invalid edit request
        invalid_edit = {
            "story_id": "invalid",
            "segment_id": "invalid",
            "edit_instruction": "test",
            "original_content": "test"
        }
        response = requests.post(f"{self.base_url}/stories/edit/", json=invalid_edit)
        assert response.status_code == 404
        
        print("✅ Error handling working correctly")
        return True
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting comprehensive API testing...\n")
        
        tests = [
            self.test_health_check,
            self.test_create_characters,
            self.test_generate_backstories,
            self.test_create_story,
            self.test_get_story,
            self.test_add_character_to_story,
            self.test_generate_story_with_user_choice,
            self.test_edit_story_segment,
            self.test_auto_continue_story,
            self.test_complete_story,
            self.test_export_pdf_base64,
            self.test_export_pdf_direct,
            self.test_get_audio_languages,
            self.test_export_audio_base64,
            self.test_export_audio_direct,
            self.test_list_stories,
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
    print("🧪 Interactive Storytelling API Test Suite")
    print("=" * 50)
    
    # Initialize tester
    tester = APITester()
    
    # Run comprehensive tests
    success = tester.run_comprehensive_test()
    
    # Run performance tests if basic tests pass
    if success:
        run_performance_test()
    
    print("\n🏁 Testing completed!")