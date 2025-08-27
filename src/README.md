# Story Assistant Backend

This is the backend implementation for the AI-powered Story Assistant, featuring multi-agent orchestration, vector-based context management, and intelligent story generation.

## 🚀 Quick Start

### Option 1: Quick Setup (10 minutes)
For a fast setup, follow the [Quick Start Guide](QUICKSTART.md):

```bash
# Clone and setup
git clone <repository-url>
cd Story_Assistant/src

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.template .env
# Edit .env with your API keys

# Run setup and start
python setup.py
python main.py --reload
```

### Option 2: Detailed Setup
For comprehensive setup instructions, see the [Technical Setup Guide](docs/setup_guide.md).

### Required API Keys
- **Groq API** - Required for LLM operations
- **Supabase** - Required for database
- **OpenAI API** - Required for embeddings
- **Gemini API** - Optional for image analysis

### Quick Test
```bash
# Test health endpoint
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

## 🏗️ Architecture Overview

### Core Components

- **Multi-Agent System**: 6 specialized AI agents for different aspects of story generation
- **Vector Database**: ChromaDB for semantic search and context management
- **LLM Integration**: Multi-provider support with fallback logic
- **Image Generation**: DALL-E 3 integration for visual storytelling
- **Workflow Engine**: LangGraph-based orchestration for complex generation tasks

### Key Features

- ✅ **Story Generation**: AI-powered narrative creation with character consistency
- ✅ **Chapter Continuation**: Seamless story progression with context awareness
- ✅ **Character Management**: Rich character profiles with relationship tracking
- ✅ **Visual Elements**: Scene images and story posters
- ✅ **Quality Assurance**: Multi-metric validation and improvement suggestions
- ✅ **Unlimited Content**: Segment-based generation for long-form stories

## 🔧 Service Dependencies

### Required Services

1. **Supabase**: Database and authentication
2. **ChromaDB**: Vector database for semantic search
3. **LLM Provider**: OpenAI, Anthropic, or Groq API

### Optional Services

1. **Redis**: For future scaling (not required for MVP)
2. **Stability AI**: Alternative image generation

## 📁 Project Structure

```
src/
├── agents/                 # AI agent implementations
│   ├── creative_director_agent.py
│   ├── narrative_intelligence_agent.py
│   ├── continuation_context_agent.py
│   ├── quality_assurance_agent.py
│   ├── world_building_agent.py
│   └── visual_storytelling_agent.py
├── api/                   # REST API endpoints
│   ├── api_routes.py
│   └── api_dependencies.py
├── config/                # Configuration management
│   ├── settings.py
│   └── database_config.py
├── models/                # Data models
│   ├── story_models.py
│   ├── character_models.py
│   └── generation_models.py
├── services/              # Core services
│   ├── llm_service.py
│   ├── vector_service.py
│   └── image_service.py
├── workflows/             # Generation workflows
│   ├── story_generation.py
│   └── chapter_continuation.py
└── utils/                 # Utility functions
    ├── embeddings.py
    └── helpers.py
```

## 🎯 API Endpoints

### Story Management
- `POST /api/v1/stories` - Create new story
- `GET /api/v1/stories` - List user stories
- `GET /api/v1/stories/{id}` - Get story with chapters
- `PUT /api/v1/stories/{id}` - Update story

### Content Generation
- `POST /api/v1/stories/{id}/generate` - Generate story content
- `POST /api/v1/stories/{id}/chapters/{id}/continue` - Continue chapter
- `GET /api/v1/tasks/{id}` - Check generation progress

### Character Management
- `POST /api/v1/characters` - Create character
- `GET /api/v1/characters` - List characters
- `POST /api/v1/stories/{id}/characters/{id}` - Add character to story

### Visual Elements
- `POST /api/v1/stories/{id}/generate-image` - Generate scene image
- `POST /api/v1/stories/{id}/generate-poster` - Generate story poster

## 🔍 Health Checks

- `GET /health` - Public health check
- `GET /api/v1/health` - Detailed service health
- `GET /api/v1/stats` - System statistics

## 🚀 Deployment

### Local Development
```bash
python main.py --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
python main.py --host 0.0.0.0 --port 8000 --workers 4
```

## 🧪 Testing & Setup

### Automated Setup and Testing
Run the comprehensive setup script to test all components:

```bash
python setup.py
```

This script will:
- ✅ Validate environment configuration
- ✅ Test database connectivity
- ✅ Initialize vector database
- ✅ Verify LLM service connectivity
- ✅ Test image generation service
- ✅ Validate all AI agents
- ✅ Generate detailed setup report

### Manual Testing
```bash
# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health

# Test API documentation
open http://localhost:8000/docs
```

## 📚 Documentation

- API documentation available at `/docs` when running in debug mode
- Technical architecture details in `docs/tech.md`
- Feature specifications in `docs/idea.md`

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify Supabase credentials in `.env`
   - Check if Supabase project is active

2. **LLM Service Unavailable**
   - Verify API keys are set correctly
   - Check API quota and billing status

3. **Vector Service Issues**
   - Ensure ChromaDB is running on configured host/port
   - Check if embedding model can be downloaded

### Getting Help

- Check the setup script output for specific error messages
- Verify all environment variables are set correctly
- Ensure all required services are running

## 🔮 Future Enhancements

- MongoDB integration for rich context storage
- Advanced image consistency management
- User preference learning and adaptation
- Advanced analytics and insights
- Multi-language support
- Collaborative story creation

---

**The Story Assistant backend is production-ready for 100 concurrent users and provides a solid foundation for AI-powered storytelling.**
noteId: "4f43620080d911f0a0f23f31356492b2"
tags: []

---

