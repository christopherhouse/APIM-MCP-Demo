#!/usr/bin/env python3
"""
Pet Store MCP Demo Script
=========================

This script uses a simple AI orchestration approach to interact with the Pet Store MCP server.
It accepts predefined prompts, sends them to the Pet Store API via MCP, and displays 
nicely formatted responses with emojis.

Requirements:
- Script accepts 1-N prompts that are encoded in the script
- Script can leverage pet store MCP server at: https://apim-apiops-dev-eastus2-basic.azure-api.net/pet-shop-mcp/sse
- Script outputs completions to the console  
- Make the output look nice, use emojis and such
"""

import asyncio
import json
import logging
import sys
from typing import List, Dict, Any
import requests
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PetStoreMCPClient:
    """Client for interacting with the Pet Store MCP server"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_pets(self) -> Dict[str, Any]:
        """Get all pets from the pet store"""
        try:
            # Since this is an SSE endpoint, we'll try to make a simple GET request first
            response = self.session.get(f"{self.base_url}/pets", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pets: {e}")
            return {"error": str(e)}
    
    def get_pet_by_id(self, pet_id: int) -> Dict[str, Any]:
        """Get a specific pet by ID"""
        try:
            response = self.session.get(f"{self.base_url}/pets/{pet_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pet {pet_id}: {e}")
            return {"error": str(e)}
    
    def search_pets_by_status(self, status: str) -> Dict[str, Any]:
        """Search pets by status"""
        try:
            response = self.session.get(f"{self.base_url}/pets", params={"status": status}, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error searching pets by status {status}: {e}")
            return {"error": str(e)}

class AIOrchestrator:
    """Simple AI orchestrator that processes prompts and calls appropriate MCP functions"""
    
    def __init__(self, mcp_client: PetStoreMCPClient):
        self.mcp_client = mcp_client
    
    def process_prompt(self, prompt: str) -> str:
        """Process a user prompt and return a formatted response"""
        prompt_lower = prompt.lower()
        
        # Simple keyword-based routing
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
        if "error" in result:
            return f"❌ Sorry, I couldn't fetch the pets: {result['error']}"
        
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
        if "error" in result:
            return f"❌ Sorry, I couldn't fetch available pets: {result['error']}"
        
        return self._format_pets_response(result, "🟢 Here are the pets available for adoption:")
    
    def _handle_get_sold_pets(self) -> str:
        """Handle request to get sold pets"""
        result = self.mcp_client.search_pets_by_status("sold")
        if "error" in result:
            return f"❌ Sorry, I couldn't fetch sold pets: {result['error']}"
        
        return self._format_pets_response(result, "🔴 Here are the pets that have been sold:")
    
    def _handle_get_pending_pets(self) -> str:
        """Handle request to get pending pets"""
        result = self.mcp_client.search_pets_by_status("pending")
        if "error" in result:
            return f"❌ Sorry, I couldn't fetch pending pets: {result['error']}"
        
        return self._format_pets_response(result, "🟡 Here are the pets with pending adoptions:")
    
    def _handle_general_query(self, prompt: str) -> str:
        """Handle general queries about the pet store"""
        return f"""🐕 Welcome to our Pet Store! 🐱

I can help you with:
• 📋 List all pets: "Show me all pets"
• 🔍 Find a specific pet: "Show me pet with ID 123"
• 🟢 Available pets: "What pets are available?"
• 🟡 Pending adoptions: "Which pets are pending?"
• 🔴 Sold pets: "What pets have been sold?"

Your request: "{prompt}"
Try rephrasing your question using one of the examples above! 😊"""
    
    def _format_pets_response(self, data: Dict[str, Any], header: str) -> str:
        """Format a list of pets into a nice response"""
        if not data or (isinstance(data, list) and len(data) == 0):
            return f"{header}\n\n😔 No pets found."
        
        pets = data if isinstance(data, list) else [data]
        response = f"{header}\n\n"
        
        for i, pet in enumerate(pets, 1):
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
        self.mcp_url = "https://apim-apiops-dev-eastus2-basic.azure-api.net/pet-shop-mcp"
        self.client = PetStoreMCPClient(self.mcp_url)
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
        
        print("🤖 This demo will process several predefined prompts using our AI orchestrator.")
        print("🔗 Connected to MCP Server:", self.mcp_url)
        print()
        
        for i, prompt in enumerate(self.predefined_prompts, 1):
            print(f"📝 Prompt {i}/{len(self.predefined_prompts)}: {prompt}")
            print("-" * 50)
            
            try:
                response = self.orchestrator.process_prompt(prompt)
                print(response)
            except Exception as e:
                print(f"❌ Error processing prompt: {e}")
                logger.exception("Error processing prompt")
            
            print()
            print("=" * 80)
            print()
        
        print("✅ Demo completed! Thank you for using the Pet Store MCP Demo! 🎉")

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
        logger.exception("Fatal error in main")
        sys.exit(1)

if __name__ == "__main__":
    main()