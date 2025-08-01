

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
                print(f"✅ Character {char_data['name']} created")
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
    
    def test_get_audio_languages(self):
        """Test getting supported audio languages"""
        print("\n🌍 Testing audio language support...")
        
        try:
            response = requests.get(f"{self.base_url}/export/audio/languages/")
            if response.status_code != 200:
                print(f"❌ Audio languages failed with status {response.status_code}")
                return False
                
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Audio languages returned success=False: {result}")
                return False
            
            if "languages" not in result or len(result["languages"]) < 5:
                print(f"❌ Insufficient languages: {result.get('languages', {})}")
                return False
                
            print(f"✅ Found {len(result['languages'])} supported languages")
            return True
            
        except Exception as e:
            print(f"❌ Audio languages test failed: {e}")
            return False
    
    def test_export_audio_base64(self):
        """Test audio export as base64"""
        print("\n🎵 Testing audio export (base64)...")
        
        try:
            response = requests.post(f"{self.base_url}/stories/{self.story_id}/export/audio/base64/?language=en")
            print(f"Audio base64 export status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Audio base64 export failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            result = response.json()
            if not result.get("success", False):
                print(f"❌ Audio export returned success=False: {result}")
                return False
            
            if "audio_base64" not in result or len(result["audio_base64"]) < 1000:
                print(f"❌ Invalid audio base64 data: {len(result.get('audio_base64', ''))}")
                return False
            
            # Validate base64 format
            try:
                base64.b64decode(result["audio_base64"])
                print("✅ Audio generated and base64 encoded successfully")
                return True
            except Exception as e:
                print(f"❌ Invalid base64 audio: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Audio base64 export failed: {e}")
            return False
    
    def test_export_audio_direct(self):
        """Test direct audio download"""
        print("\n🎧 Testing audio direct download...")
        
        try:
            response = requests.post(f"{self.base_url}/stories/{self.story_id}/export/audio/?language=en")
            print(f"Audio direct export status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Audio direct export failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            if response.headers.get("content-type") != "audio/mpeg":
                print(f"❌ Wrong content type: {response.headers.get('content-type')}")
                return False
            
            if len(response.content) < 1000:
                print(f"❌ Audio too small: {len(response.content)} bytes")
                return False
                
            print("✅ Audio direct download successful")
            return True
            
        except Exception as e:
            print(f"❌ Audio direct export failed: {e}")
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
            
            print("✅ Error handling working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Error case testing failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting comprehensive API testing...\n")
        
        tests = [
            self.test_health_check,
            self.test_debug_llm_service,
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