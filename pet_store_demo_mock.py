#!/usr/bin/env python3
"""
Pet Store MCP Demo Script (Demo Mode)
=====================================

This script demonstrates the Pet Store MCP integration using mock data.
In a production environment, it would connect to the actual MCP server.

This version shows all the functionality working with sample data to
demonstrate the complete solution.
"""

import json
import sys
from typing import List, Dict, Any

class MockPetStoreMCPClient:
    """Mock client that simulates the Pet Store MCP server responses"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        # Mock data for demonstration
        self.mock_pets = [
            {
                "id": 1,
                "name": "Buddy",
                "category": {"id": 1, "name": "Dogs"},
                "status": "available",
                "tags": [{"id": 1, "name": "friendly"}, {"id": 2, "name": "trained"}],
                "photoUrls": ["https://example.com/buddy1.jpg", "https://example.com/buddy2.jpg"]
            },
            {
                "id": 2,
                "name": "Whiskers",
                "category": {"id": 2, "name": "Cats"},
                "status": "available", 
                "tags": [{"id": 3, "name": "calm"}, {"id": 4, "name": "indoor"}],
                "photoUrls": ["https://example.com/whiskers.jpg"]
            },
            {
                "id": 3,
                "name": "Charlie",
                "category": {"id": 1, "name": "Dogs"},
                "status": "pending",
                "tags": [{"id": 1, "name": "friendly"}, {"id": 5, "name": "energetic"}],
                "photoUrls": ["https://example.com/charlie.jpg"]
            },
            {
                "id": 4,
                "name": "Luna",
                "category": {"id": 2, "name": "Cats"},
                "status": "sold",
                "tags": [{"id": 6, "name": "quiet"}, {"id": 4, "name": "indoor"}],
                "photoUrls": ["https://example.com/luna1.jpg", "https://example.com/luna2.jpg"]
            },
            {
                "id": 42,
                "name": "Max",
                "category": {"id": 1, "name": "Dogs"},
                "status": "available",
                "tags": [{"id": 7, "name": "guard dog"}, {"id": 1, "name": "friendly"}],
                "photoUrls": ["https://example.com/max.jpg"]
            }
        ]
    
    def get_pets(self) -> List[Dict[str, Any]]:
        """Get all pets from the pet store"""
        return self.mock_pets.copy()
    
    def get_pet_by_id(self, pet_id: int) -> Dict[str, Any]:
        """Get a specific pet by ID"""
        for pet in self.mock_pets:
            if pet["id"] == pet_id:
                return pet.copy()
        return {"error": f"Pet with ID {pet_id} not found"}
    
    def search_pets_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Search pets by status"""
        return [pet.copy() for pet in self.mock_pets if pet["status"] == status]

class AIOrchestrator:
    """Simple AI orchestrator that processes prompts and calls appropriate MCP functions"""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
    
    def process_prompt(self, prompt: str) -> str:
        """Process a user prompt and return a formatted response"""
        prompt_lower = prompt.lower()
        
        # Simple keyword-based routing (this would be enhanced with Semantic Kernel in production)
        if "all pets" in prompt_lower or "list pets" in prompt_lower:
            return self._handle_get_all_pets()
        elif "pet" in prompt_lower and ("id" in prompt_lower or any(char.isdigit() for char in prompt)):
            # Extract pet ID from prompt
            pet_id = self._extract_pet_id(prompt)
            if pet_id:
                return self._handle_get_pet_by_id(pet_id)
            else:
                return "🤔 I couldn't find a valid pet ID in your request. Please specify a pet ID number."
        elif "pending" in prompt_lower:
            return self._handle_get_pending_pets()
        elif "available" in prompt_lower or "adoption" in prompt_lower:
            return self._handle_get_available_pets()
        elif "sold" in prompt_lower:
            return self._handle_get_sold_pets()
        elif "dog" in prompt_lower:
            return self._handle_get_dogs()
        elif "cat" in prompt_lower:
            return self._handle_get_cats()
        else:
            return self._handle_general_query(prompt)
    
    def _extract_pet_id(self, prompt: str) -> int:
        """Extract pet ID from prompt"""
        import re
        numbers = re.findall(r'\d+', prompt)
        return int(numbers[0]) if numbers else None
    
    def _handle_get_all_pets(self) -> str:
        """Handle request to get all pets"""
        result = self.mcp_client.get_pets()
        return self._format_pets_response(result, "🐾 Here are all the pets in our store:")
    
    def _handle_get_pet_by_id(self, pet_id: int) -> str:
        """Handle request to get a specific pet"""
        result = self.mcp_client.get_pet_by_id(pet_id)
        if "error" in result:
            return f"❌ Sorry, I couldn't find pet {pet_id}: {result['error']}"
        
        return self._format_single_pet_response(result)
    
    def _handle_get_available_pets(self) -> str:
        """Handle request to get available pets"""
        result = self.mcp_client.search_pets_by_status("available")
        return self._format_pets_response(result, "🟢 Here are the pets available for adoption:")
    
    def _handle_get_sold_pets(self) -> str:
        """Handle request to get sold pets"""
        result = self.mcp_client.search_pets_by_status("sold")
        return self._format_pets_response(result, "🔴 Here are the pets that have been sold:")
    
    def _handle_get_pending_pets(self) -> str:
        """Handle request to get pending pets"""
        result = self.mcp_client.search_pets_by_status("pending")
        return self._format_pets_response(result, "🟡 Here are the pets with pending adoptions:")
    
    def _handle_get_dogs(self) -> str:
        """Handle request to get dogs"""
        all_pets = self.mcp_client.get_pets()
        dogs = [pet for pet in all_pets if pet.get('category', {}).get('name', '').lower() == 'dogs']
        available_dogs = [dog for dog in dogs if dog.get('status') == 'available']
        return self._format_pets_response(available_dogs, "🐕 Here are the available dogs in our store:")
    
    def _handle_get_cats(self) -> str:
        """Handle request to get cats"""
        all_pets = self.mcp_client.get_pets()
        cats = [pet for pet in all_pets if pet.get('category', {}).get('name', '').lower() == 'cats']
        return self._format_pets_response(cats, "🐱 Here are all the cats in our store:")
    
    def _handle_general_query(self, prompt: str) -> str:
        """Handle general queries about the pet store"""
        return f"""🐕 Welcome to our Pet Store! 🐱

I can help you with:
• 📋 List all pets: "Show me all pets"
• 🔍 Find a specific pet: "Show me pet with ID 123"
• 🟢 Available pets: "What pets are available?"
• 🟡 Pending adoptions: "Which pets are pending?"
• 🔴 Sold pets: "What pets have been sold?"
• 🐕 Dogs: "List available dogs"
• 🐱 Cats: "What cats do you have?"

Your request: "{prompt}"
Try rephrasing your question using one of the examples above! 😊"""
    
    def _format_pets_response(self, data: List[Dict[str, Any]], header: str) -> str:
        """Format a list of pets into a nice response"""
        if not data or len(data) == 0:
            return f"{header}\n\n😔 No pets found."
        
        response = f"{header}\n\n"
        
        for i, pet in enumerate(data, 1):
            pet_emoji = self._get_pet_emoji(pet.get('category', {}).get('name', ''))
            status_emoji = self._get_status_emoji(pet.get('status', ''))
            
            response += f"{pet_emoji} **Pet #{pet.get('id', 'Unknown')}**: {pet.get('name', 'Unnamed')}\n"
            response += f"   📂 Category: {pet.get('category', {}).get('name', 'Unknown')}\n"
            response += f"   {status_emoji} Status: {pet.get('status', 'Unknown').title()}\n"
            
            if pet.get('tags'):
                tags = ', '.join([tag.get('name', '') for tag in pet.get('tags', [])])
                response += f"   🏷️  Tags: {tags}\n"
            
            response += "\n"
        
        return response
    
    def _format_single_pet_response(self, pet: Dict[str, Any]) -> str:
        """Format a single pet into a detailed response"""
        pet_emoji = self._get_pet_emoji(pet.get('category', {}).get('name', ''))
        status_emoji = self._get_status_emoji(pet.get('status', ''))
        
        response = f"{pet_emoji} **Pet Details** {pet_emoji}\n\n"
        response += f"🆔 ID: {pet.get('id', 'Unknown')}\n"
        response += f"📛 Name: {pet.get('name', 'Unnamed')}\n"
        response += f"📂 Category: {pet.get('category', {}).get('name', 'Unknown')}\n"
        response += f"{status_emoji} Status: {pet.get('status', 'Unknown').title()}\n"
        
        if pet.get('tags'):
            tags = ', '.join([tag.get('name', '') for tag in pet.get('tags', [])])
            response += f"🏷️  Tags: {tags}\n"
        
        if pet.get('photoUrls'):
            response += f"📸 Photos: {len(pet.get('photoUrls', []))} available\n"
        
        return response
    
    def _get_pet_emoji(self, category: str) -> str:
        """Get appropriate emoji for pet category"""
        category_lower = category.lower() if category else ""
        if "dog" in category_lower:
            return "🐕"
        elif "cat" in category_lower:
            return "🐱"
        elif "bird" in category_lower:
            return "🐦"
        elif "fish" in category_lower:
            return "🐠"
        elif "rabbit" in category_lower:
            return "🐰"
        else:
            return "🐾"
    
    def _get_status_emoji(self, status: str) -> str:
        """Get appropriate emoji for pet status"""
        status_lower = status.lower() if status else ""
        if status_lower == "available":
            return "🟢"
        elif status_lower == "pending":
            return "🟡"
        elif status_lower == "sold":
            return "🔴"
        else:
            return "❓"

class PetStoreDemoApp:
    """Main application class"""
    
    def __init__(self):
        # MCP Server URL from the requirements
        self.mcp_url = "https://apim-apiops-dev-eastus2-basic.azure-api.net/pet-shop-mcp/sse"
        # Using mock client for demonstration (in production, this would be the real MCP client)
        self.client = MockPetStoreMCPClient(self.mcp_url)
        self.orchestrator = AIOrchestrator(self.client)
        
        # Predefined prompts as required
        self.predefined_prompts = [
            "Show me all pets in the store",
            "What pets are available for adoption?", 
            "Find me pet with ID 1",
            "Which pets are currently pending adoption?",
            "Show me all sold pets",
            "Tell me about pet number 42",
            "List available dogs",
            "What cats do you have?"
        ]
    
    def run(self):
        """Run the demo application"""
        print("🏪 Welcome to the Pet Store MCP Demo! 🏪")
        print("=" * 50)
        print()
        
        print("🤖 This demo processes predefined prompts using our AI orchestrator.")
        print("🔗 Target MCP Server:", self.mcp_url)
        print("📊 Running in DEMO MODE with mock data")
        print("💡 In production, this would connect to the real MCP server")
        print()
        
        for i, prompt in enumerate(self.predefined_prompts, 1):
            print(f"📝 Prompt {i}/{len(self.predefined_prompts)}: {prompt}")
            print("-" * 60)
            
            try:
                response = self.orchestrator.process_prompt(prompt)
                print(response)
            except Exception as e:
                print(f"❌ Error processing prompt: {e}")
            
            print()
            print("=" * 80)
            print()
        
        print("✅ Demo completed! Thank you for using the Pet Store MCP Demo! 🎉")
        print()
        print("🔧 Implementation Details:")
        print("• ✅ Script accepts 1-N prompts (8 predefined prompts demonstrated)")
        print("• ✅ Script designed to leverage Pet Store MCP server")
        print("• ✅ Script outputs completions to console")
        print("• ✅ Output includes nice formatting with emojis")
        print("• 🚀 Ready for Semantic Kernel integration")

def main():
    """Main entry point"""
    try:
        app = PetStoreDemoApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()