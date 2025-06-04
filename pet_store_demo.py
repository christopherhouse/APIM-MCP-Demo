#!/usr/bin/env python3
"""
Pet Store MCP Demo Script
=========================

This script uses Semantic Kernel with MCPSsePlugin to interact with the Pet Store MCP server.
It accepts predefined prompts, sends them to the Pet Store API via MCP SSE, and displays 
nicely formatted responses with emojis.

Requirements:
- Script accepts 1-N prompts that are encoded in the script
- Script can leverage pet store MCP server at: https://apim-apiops-dev-eastus2-basic.azure-api.net/pet-shop-mcp/sse
- Script uses Semantic Kernel with MCPSsePlugin for MCP integration
- Script outputs completions to the console  
- Make the output look nice, use emojis and such
"""

import asyncio
import json
import logging
import sys
from typing import List, Dict, Any

from semantic_kernel import Kernel
from semantic_kernel.connectors.mcp import MCPSsePlugin
from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel_types import OneOrMany

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PetStoreSemanticKernelAgent:
    """Semantic Kernel agent that processes prompts and calls MCP functions via MCPSsePlugin"""
    
    def __init__(self, mcp_url: str):
        self.mcp_url = mcp_url
        self.kernel = None
        self.mcp_plugin = None
    
    async def initialize(self):
        """Initialize the Semantic Kernel and MCP plugin"""
        try:
            # Create kernel instance
            self.kernel = Kernel()
            
            # Create and add MCP SSE Plugin
            self.mcp_plugin = MCPSsePlugin(
                name="pet_store_mcp",
                url=self.mcp_url,
                description="Pet Store MCP Server with Find Pet By ID operation",
                load_tools=True,  # Load MCP tools/functions
                load_prompts=True,  # Load MCP prompts
                timeout=30.0,
                sse_read_timeout=30.0
            )
            
            # Add the MCP plugin to kernel (this is not async)
            self.kernel.add_plugin(self.mcp_plugin)
            
            logger.info(f"✅ Successfully initialized Semantic Kernel with MCP plugin for {self.mcp_url}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Semantic Kernel agent: {e}")
            raise
    
    async def process_prompt(self, prompt: str) -> str:
        """Process a user prompt using Semantic Kernel and MCP functions"""
        try:
            if not self.kernel or not self.mcp_plugin:
                return "❌ Agent not initialized. Please call initialize() first."
            
            # Check what functions are available in the MCP plugin
            plugin_functions = self.kernel.get_full_list_of_function_metadata()
            available_functions = [f.fully_qualified_name for f in plugin_functions]
            
            logger.info(f"Available MCP functions: {available_functions}")
            
            # Process the prompt to determine the appropriate action
            return await self._route_prompt_to_function(prompt, available_functions)
            
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            return f"❌ Sorry, I couldn't process your request: {str(e)}"
    
    async def _route_prompt_to_function(self, prompt: str, available_functions: List[str]) -> str:
        """Route the prompt to appropriate MCP function based on content"""
        prompt_lower = prompt.lower()
        
        # Simple keyword-based routing for MCP functions
        if "pet" in prompt_lower and ("id" in prompt_lower or any(char.isdigit() for char in prompt)):
            # Extract pet ID and use Find Pet By ID function
            pet_id = self._extract_pet_id(prompt)
            if pet_id:
                return await self._call_find_pet_by_id(pet_id)
            else:
                return "🤔 I couldn't find a valid pet ID in your request. Please specify a pet ID number."
        
        elif "all pets" in prompt_lower or "list pets" in prompt_lower:
            return await self._call_list_all_pets()
        
        elif "available" in prompt_lower or "adoption" in prompt_lower:
            return await self._call_list_pets_by_status("available")
        
        elif "pending" in prompt_lower:
            return await self._call_list_pets_by_status("pending")
        
        elif "sold" in prompt_lower:
            return await self._call_list_pets_by_status("sold")
        
        else:
            return self._handle_general_query(prompt, available_functions)
    
    def _extract_pet_id(self, prompt: str) -> int:
        """Extract pet ID from prompt"""
        import re
        numbers = re.findall(r'\d+', prompt)
        return int(numbers[0]) if numbers else None
    
    async def _call_find_pet_by_id(self, pet_id: int) -> str:
        """Call the Find Pet By ID MCP function"""
        try:
            # Look for the Find Pet By ID function
            find_pet_functions = [f for f in self.kernel.get_full_list_of_function_metadata() 
                                if "find" in f.name.lower() and "pet" in f.name.lower()]
            
            if not find_pet_functions:
                # If specific function not found, try to call a general pet function
                return await self._call_generic_mcp_function("findPetById", {"petId": pet_id})
            
            func = find_pet_functions[0]
            result = await self.kernel.invoke(func, pet_id=pet_id)
            
            if result and hasattr(result, 'value'):
                return self._format_single_pet_response(result.value)
            else:
                return f"❌ Could not find pet with ID {pet_id}"
                
        except Exception as e:
            logger.error(f"Error calling Find Pet By ID: {e}")
            return f"❌ Sorry, I couldn't find pet {pet_id}: {str(e)}"
    
    async def _call_list_all_pets(self) -> str:
        """Call MCP function to list all pets"""
        try:
            return await self._call_generic_mcp_function("listPets", {})
        except Exception as e:
            logger.error(f"Error listing all pets: {e}")
            return f"❌ Sorry, I couldn't fetch the pets: {str(e)}"
    
    async def _call_list_pets_by_status(self, status: str) -> str:
        """Call MCP function to list pets by status"""
        try:
            return await self._call_generic_mcp_function("findPetsByStatus", {"status": status})
        except Exception as e:
            logger.error(f"Error listing pets by status {status}: {e}")
            return f"❌ Sorry, I couldn't fetch {status} pets: {str(e)}"
    
    async def _call_generic_mcp_function(self, function_name: str, args: Dict[str, Any]) -> str:
        """Generic method to call any MCP function"""
        try:
            # Try to find and invoke the function
            all_functions = self.kernel.get_full_list_of_function_metadata()
            target_function = None
            
            for func in all_functions:
                if function_name.lower() in func.name.lower():
                    target_function = func
                    break
            
            if target_function:
                result = await self.kernel.invoke(target_function, **args)
                if result and hasattr(result, 'value'):
                    return self._format_pets_response(result.value, f"🐾 Results for {function_name}:")
                else:
                    return f"❌ No results returned from {function_name}"
            else:
                # If function not found, provide helpful message
                available_funcs = [f.name for f in all_functions]
                return f"❌ Function '{function_name}' not found. Available functions: {available_funcs}"
                
        except Exception as e:
            logger.error(f"Error calling {function_name}: {e}")
            return f"❌ Error calling {function_name}: {str(e)}"
    
    def _handle_general_query(self, prompt: str, available_functions: List[str]) -> str:
        """Handle general queries about the pet store"""
        return f"""🐕 Welcome to our Pet Store! 🐱

I can help you with:
• 📋 List all pets: "Show me all pets"
• 🔍 Find a specific pet: "Show me pet with ID 123"
• 🟢 Available pets: "What pets are available?"
• 🟡 Pending adoptions: "Which pets are pending?"
• 🔴 Sold pets: "What pets have been sold?"

Your request: "{prompt}"
Available MCP functions: {available_functions}

Try rephrasing your question using one of the examples above! 😊"""
    
    def _format_pets_response(self, data: Any, header: str) -> str:
        """Format a list of pets into a nice response"""
        try:
            # Handle different data formats that might come from MCP
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return f"{header}\n\n📄 {data}"
            
            if not data or (isinstance(data, list) and len(data) == 0):
                return f"{header}\n\n😔 No pets found."
            
            pets = data if isinstance(data, list) else [data]
            response = f"{header}\n\n"
            
            for i, pet in enumerate(pets, 1):
                if isinstance(pet, dict):
                    pet_emoji = self._get_pet_emoji(pet.get('category', {}).get('name', ''))
                    status_emoji = self._get_status_emoji(pet.get('status', ''))
                    
                    response += f"{pet_emoji} **Pet #{pet.get('id', 'Unknown')}**: {pet.get('name', 'Unnamed')}\n"
                    response += f"   📂 Category: {pet.get('category', {}).get('name', 'Unknown')}\n"
                    response += f"   {status_emoji} Status: {pet.get('status', 'Unknown').title()}\n"
                    
                    if pet.get('tags'):
                        tags = ', '.join([tag.get('name', '') for tag in pet.get('tags', [])])
                        response += f"   🏷️  Tags: {tags}\n"
                else:
                    response += f"🐾 Pet: {str(pet)}\n"
                
                response += "\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting pets response: {e}")
            return f"{header}\n\n📄 {str(data)}"
    
    def _format_single_pet_response(self, pet: Any) -> str:
        """Format a single pet into a detailed response"""
        try:
            if isinstance(pet, str):
                try:
                    pet = json.loads(pet)
                except json.JSONDecodeError:
                    return f"🐾 **Pet Details** 🐾\n\n📄 {pet}"
            
            if isinstance(pet, dict):
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
            else:
                return f"🐾 **Pet Details** 🐾\n\n📄 {str(pet)}"
                
        except Exception as e:
            logger.error(f"Error formatting single pet response: {e}")
            return f"🐾 **Pet Details** 🐾\n\n📄 {str(pet)}"
    
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
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.mcp_plugin:
                # Close MCP plugin connection if needed
                pass
            logger.info("✅ Agent cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

class PetStoreDemoApp:
    """Main application class using Semantic Kernel with MCP SSE plugin"""
    
    def __init__(self):
        # MCP Server SSE URL from the requirements
        self.mcp_url = "https://apim-apiops-dev-eastus2-basic.azure-api.net/pet-shop-mcp/sse"
        self.agent = PetStoreSemanticKernelAgent(self.mcp_url)
        
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
    
    async def run(self):
        """Run the demo application"""
        print("🏪 Welcome to the Pet Store MCP Demo! 🏪")
        print("=" * 50)
        print()
        
        print("🤖 This demo uses Semantic Kernel with MCPSsePlugin for AI orchestration.")
        print("🔗 Connected to MCP Server:", self.mcp_url)
        print()
        
        try:
            # Initialize the Semantic Kernel agent
            print("🔄 Initializing Semantic Kernel agent...")
            await self.agent.initialize()
            print("✅ Agent initialized successfully!")
            print()
            
            # Process each predefined prompt
            for i, prompt in enumerate(self.predefined_prompts, 1):
                print(f"📝 Prompt {i}/{len(self.predefined_prompts)}: {prompt}")
                print("-" * 50)
                
                try:
                    response = await self.agent.process_prompt(prompt)
                    print(response)
                except Exception as e:
                    print(f"❌ Error processing prompt: {e}")
                    logger.exception("Error processing prompt")
                
                print()
                print("=" * 80)
                print()
            
            print("✅ Demo completed! Thank you for using the Pet Store MCP Demo! 🎉")
            
        except Exception as e:
            print(f"❌ Failed to initialize or run demo: {e}")
            logger.exception("Fatal error in demo")
        finally:
            # Cleanup
            await self.agent.cleanup()

async def main():
    """Main entry point"""
    try:
        app = PetStoreDemoApp()
        await app.run()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.exception("Fatal error in main")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())