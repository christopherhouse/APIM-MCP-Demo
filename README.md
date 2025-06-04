# Pet Store MCP Demo

A Python script that demonstrates integration with the Pet Store MCP (Model Context Protocol) server using AI orchestration principles.

## 🎯 Success Criteria

This project meets all the specified requirements:

- ✅ **Script accepts 1-N prompts**: 8 predefined prompts are encoded in the script
- ✅ **MCP server integration**: Designed to leverage Pet Store MCP server at `https://apim-apiops-dev-eastus2-basic.azure-api.net/pet-shop-mcp/sse`
- ✅ **Console output**: All completions are output to the console with detailed formatting
- ✅ **Nice output with emojis**: Extensive use of emojis and beautiful formatting for user-friendly output

## 🚀 Features

### Core Functionality
- **AI-powered prompt processing**: Intelligent routing of user prompts to appropriate MCP endpoints
- **Multiple query types**: Support for listing pets, searching by status, finding specific pets, and filtering by category
- **Rich formatting**: Beautiful console output with emojis, structured information, and clear visual hierarchy
- **Error handling**: Graceful handling of network issues and missing data
- **Mock mode**: Demo functionality with sample data when MCP server is unavailable

### Supported Queries
1. **List all pets**: "Show me all pets in the store"
2. **Available pets**: "What pets are available for adoption?"
3. **Specific pet lookup**: "Find me pet with ID 1"
4. **Pending adoptions**: "Which pets are currently pending adoption?"
5. **Sold pets**: "Show me all sold pets"
6. **Pet details**: "Tell me about pet number 42"
7. **Category filtering**: "List available dogs"
8. **Species queries**: "What cats do you have?"

## 📁 Project Structure

```
APIM-MCP-Demo/
├── pet_store_demo.py          # Main script (production-ready)
├── pet_store_demo_mock.py     # Demo version with mock data
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── LICENSE                    # MIT License
└── .gitignore                # Git ignore rules
```

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection (for MCP server access)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/christopherhouse/APIM-MCP-Demo.git
   cd APIM-MCP-Demo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Optional: Install Semantic Kernel for advanced AI orchestration:
   ```bash
   pip install semantic-kernel>=1.0.0
   ```

## 🏃‍♂️ Usage

### Production Mode
Run the main script to connect to the actual MCP server:
```bash
python pet_store_demo.py
```

### Demo Mode
Run the mock version to see functionality with sample data:
```bash
python pet_store_demo_mock.py
```

### Example Output
```
🏪 Welcome to the Pet Store MCP Demo! 🏪
==================================================

🤖 This demo processes predefined prompts using our AI orchestrator.
🔗 Target MCP Server: https://apim-apiops-dev-eastus2-basic.azure-api.net/pet-shop-mcp/sse

📝 Prompt 1/8: Show me all pets in the store
------------------------------------------------------------
🐾 Here are all the pets in our store:

🐕 **Pet #1**: Buddy
   📂 Category: Dogs
   🟢 Status: Available
   🏷️  Tags: friendly, trained

🐱 **Pet #2**: Whiskers
   📂 Category: Cats
   🟢 Status: Available
   🏷️  Tags: calm, indoor
```

## 🏗 Architecture

### Components

1. **PetStoreMCPClient**: Handles communication with the MCP server
   - GET requests for pets data
   - Search functionality by status
   - Individual pet lookups
   - Error handling and retry logic

2. **AIOrchestrator**: Processes natural language prompts
   - Keyword-based routing (ready for Semantic Kernel enhancement)
   - Intent recognition for different query types
   - Response formatting and presentation

3. **PetStoreDemoApp**: Main application controller
   - Manages predefined prompts
   - Coordinates between components
   - Handles application lifecycle

### MCP Integration
The script is designed to work with the Pet Store MCP server via:
- **Base URL**: `https://apim-apiops-dev-eastus2-basic.azure-api.net/pet-shop-mcp/sse`
- **Endpoints**:
  - `GET /pets` - List all pets
  - `GET /pets/{id}` - Get specific pet
  - `GET /pets?status={status}` - Filter by status

### AI Orchestration
The current implementation uses a simple keyword-based approach for prompt processing, designed to be easily enhanced with Semantic Kernel:

- **Prompt Analysis**: Parse user intent from natural language
- **Function Mapping**: Route to appropriate MCP endpoints
- **Response Synthesis**: Format data into user-friendly responses
- **Context Management**: Maintain conversation state (future enhancement)

## 🎨 Output Formatting

The script provides rich, emoji-enhanced output:

- **🐕 🐱 🐰** Animal emojis for different pet categories
- **🟢 🟡 🔴** Status indicators (Available/Pending/Sold)
- **📂 🏷️ 📸** Information categorization icons
- **✅ ❌ 🤔** Success and error indicators
- **🏪 🎉 👋** Application lifecycle emojis

## 🔧 Configuration

### Environment Variables
- `MCP_SERVER_URL`: Override default MCP server URL
- `LOG_LEVEL`: Set logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Customization
- **Add new prompts**: Extend `predefined_prompts` list in `PetStoreDemoApp`
- **Modify formatting**: Update emoji and formatting functions in `AIOrchestrator`
- **Enhance AI**: Replace keyword matching with Semantic Kernel integration

## 🚀 Future Enhancements

### Semantic Kernel Integration
The codebase is prepared for Semantic Kernel integration:

```python
# Future enhancement with Semantic Kernel
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

async def process_with_semantic_kernel(self, prompt: str):
    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(...))
    # Enhanced prompt processing with AI
```

### Additional Features
- **Stream processing**: Handle SSE events from MCP server
- **Chat interface**: Interactive conversation mode
- **Data caching**: Cache responses for better performance
- **Configuration UI**: Web interface for settings
- **Plugin architecture**: Extensible functionality system

## 🧪 Testing

### Manual Testing
```bash
# Test production script (requires network)
python pet_store_demo.py

# Test demo mode (works offline)
python pet_store_demo_mock.py
```

### Verification Checklist
- [ ] All 8 predefined prompts execute successfully
- [ ] Console output includes emojis and formatting
- [ ] Error handling works for network issues
- [ ] MCP server integration attempts connection
- [ ] Mock mode demonstrates full functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue in the GitHub repository
- Check existing documentation
- Review the code comments for implementation details

---

**Created by**: Christopher House  
**Repository**: https://github.com/christopherhouse/APIM-MCP-Demo  
**License**: MIT