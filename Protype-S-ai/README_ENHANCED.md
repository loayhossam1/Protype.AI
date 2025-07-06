# Protype.AI Enhanced 🚀

**Advanced Conversational AI Platform with Self-Reflection and Learning**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-red.svg)](VERSION)

---

## 🎯 Overview

Protype.AI Enhanced is a sophisticated conversational AI platform that combines cutting-edge artificial intelligence with professional web interface design. Originally developed by **Islam Ibrahim, Director of Carrot Studio**, this enhanced version provides a comprehensive AI solution with advanced capabilities.

### ✨ Key Features

- **🧠 Self-Reflection**: Advanced Chain of Thought reasoning for better decision making
- **💾 Advanced Memory**: FAISS-powered vector storage with RAG (Retrieval-Augmented Generation)
- **🎨 Multimodal Intelligence**: Process text, images, and audio seamlessly
- **🤖 Autonomous Agent**: Self-directed learning and knowledge acquisition
- **📊 Knowledge Graph**: Neural network-based concept relationships
- **🌐 Professional Web Interface**: Modern, responsive design with dark/light themes
- **⚡ Enhanced Performance**: Redis caching and PostgreSQL support
- **📈 Real-time Analytics**: Comprehensive monitoring and reporting

---

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Protype.AI Enhanced                 │
├─────────────────────────────────────────────────────────┤
│  Web Interface (Flask + Modern UI)                     │
├─────────────────────────────────────────────────────────┤
│  API Layer (RESTful + WebSocket)                       │
├─────────────────────────────────────────────────────────┤
│  AI Processing Pipeline                                 │
│  ├── Self-Reflection Engine                            │
│  ├── Advanced Memory (FAISS + RAG)                     │
│  ├── Multimodal Intelligence                           │
│  ├── Autonomous Learning Agent                         │
│  └── Knowledge Graph                                   │
├─────────────────────────────────────────────────────────┤
│  Data Layer                                             │
│  ├── PostgreSQL / SQLite (Primary)                     │
│  ├── Redis (Caching)                                   │
│  └── Vector Storage (FAISS)                            │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.8+
- Flask 2.3.3 (Web Framework)
- Google Gemini API (AI Processing)
- FAISS (Vector Search)
- PostgreSQL/SQLite (Database)
- Redis (Caching)
- Celery (Background Tasks)

**Frontend:**
- Modern HTML5/CSS3
- Vanilla JavaScript
- Font Awesome Icons
- AOS Animation Library
- Responsive Design

**AI/ML:**
- Transformers (Hugging Face)
- Sentence Transformers
- spaCy (NLP)
- NetworkX (Graph Processing)
- scikit-learn (ML Utilities)

---

## 🚀 Quick Start

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd Protype-S-ai

# Run the enhanced installation script
python3 install_enhanced.py
```

### Option 2: Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from database_enhanced import init_db; init_db()"

# Start the application
python web_app_enhanced.py
```

### 📋 System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- Internet connection

**Recommended:**
- Python 3.10+
- 8GB+ RAM
- 5GB+ free disk space
- GPU (for advanced AI features)

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# AI API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/protype_ai
REDIS_URL=redis://localhost:6379/0

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key

# Application Settings
PROTYPE_VERSION=2.0.0
LOG_LEVEL=INFO
```

### Database Setup

**PostgreSQL (Recommended for Production):**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb protype_ai
sudo -u postgres createuser protype_user
sudo -u postgres psql -c "ALTER USER protype_user PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE protype_ai TO protype_user;"
```

**SQLite (Default for Development):**
```bash
# Automatic setup - no additional configuration needed
# Database file: protype_e0.db
```

---

## 🎮 Usage

### Starting the Application

**Using Startup Scripts:**
```bash
# Linux/macOS
./start_protype.sh

# Windows
start_protype.bat
```

**Manual Start:**
```bash
source venv/bin/activate
python web_app_enhanced.py
```

### Accessing the Interface

- **Main Interface**: http://localhost:8080
- **Dashboard**: http://localhost:8080/dashboard
- **API Health Check**: http://localhost:8080/health
- **API Documentation**: http://localhost:8080/api/docs

### Basic Usage Examples

**Chat Interface:**
```javascript
// Send a message via API
fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Hello, how are you?' })
})
.then(response => response.json())
.then(data => console.log(data.response));
```

**Search Knowledge:**
```bash
curl "http://localhost:8080/api/search?q=artificial%20intelligence&limit=5"
```

**Add Knowledge:**
```bash
curl -X POST http://localhost:8080/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?", "answer": "AI is artificial intelligence..."}'
```

---

## 🧠 AI Features

### Self-Reflection Engine

The self-reflection system evaluates its own responses using Chain of Thought reasoning:

```python
# Example: Evaluate an inference
evaluation = self_reflection.evaluate_inference(
    source="artificial intelligence",
    target="machine learning", 
    relation="includes",
    confidence=0.8
)
```

### Advanced Memory System

FAISS-powered vector storage with semantic search:

```python
# Add knowledge to memory
advanced_memory.add_knowledge(
    question="What is quantum computing?",
    answer="Quantum computing uses quantum mechanics...",
    source="research_paper"
)

# Search similar knowledge
results = advanced_memory.search("quantum computing", k=5)
```

### Multimodal Intelligence

Process different types of content:

```python
# Analyze an image
result = multimodal_intelligence.analyze_image(
    image_data=base64_image,
    query="What do you see in this image?"
)

# Convert text to speech
audio = multimodal_intelligence.text_to_speech(
    text="Hello, this is Protype.AI",
    voice_id="default"
)
```

### Autonomous Learning Agent

The agent can learn independently:

```python
# Start autonomous learning
autonomous_agent.start_agent(autonomous_mode=True)

# Add learning objectives
autonomous_agent.add_objective("Learn about renewable energy")
```

---

## 📊 API Reference

### Chat Endpoints

```http
POST /api/chat
Content-Type: application/json

{
    "message": "Your question here"
}
```

**Response:**
```json
{
    "response": "AI response",
    "session_id": "unique_session_id",
    "timestamp": "2025-01-01T12:00:00Z"
}
```

### Memory Management

```http
POST /api/memory/search
Content-Type: application/json

{
    "query": "search term",
    "max_results": 5
}
```

```http
POST /api/memory/add
Content-Type: application/json

{
    "question": "Question",
    "answer": "Answer", 
    "source": "manual"
}
```

### Self-Reflection

```http
POST /api/reflection/evaluate
Content-Type: application/json

{
    "source": "concept1",
    "target": "concept2",
    "relation": "is_related_to",
    "confidence": 0.8
}
```

### System Information

```http
GET /api/stats
```

**Response:**
```json
{
    "total_knowledge_items": 1500,
    "memory_entries": 800,
    "graph_nodes": 2000,
    "graph_edges": 5000,
    "learning_active": true,
    "uptime": 86400
}
```

---

## 🛠️ Development

### Project Structure

```
Protype-S-ai/
├── 📁 templates/              # HTML templates
│   ├── index_enhanced.html    # Main interface
│   └── dashboard.html         # Analytics dashboard
├── 📁 static/                # Static assets
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   └── images/               # Images and icons
├── 📄 web_app_enhanced.py    # Enhanced Flask application
├── 📄 database_enhanced.py   # Enhanced database layer
├── 📄 self_reflection.py     # Self-reflection engine
├── 📄 advanced_memory.py     # Memory management
├── 📄 multimodal_intelligence.py # Multimodal processing
├── 📄 autonomous_agent.py    # Learning agent
├── 📄 knowledge_graph.py     # Graph processing
├── 📄 install_enhanced.py    # Installation script
└── 📄 README_ENHANCED.md     # This file
```

### Adding New Features

1. **Create a new module:**
```python
# my_feature.py
class MyFeature:
    def __init__(self):
        self.name = "My Feature"
    
    def process(self, input_data):
        # Your feature logic here
        return processed_data
```

2. **Integrate with the web app:**
```python
# In web_app_enhanced.py
from my_feature import MyFeature

my_feature = MyFeature()

@app.route('/api/my-feature', methods=['POST'])
def my_feature_endpoint():
    data = request.get_json()
    result = my_feature.process(data)
    return jsonify(result)
```

3. **Add frontend interface:**
```javascript
// In your HTML/JavaScript
async function useMyFeature(inputData) {
    const response = await fetch('/api/my-feature', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputData)
    });
    return response.json();
}
```

### Testing

```bash
# Run basic system test
python -c "from install_enhanced import run_system_test; run_system_test()"

# Test individual components
python -c "from database_enhanced import get_statistics; print(get_statistics())"
python -c "from self_reflection import self_reflection; print(self_reflection.generate_critical_questions('AI', 3))"
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check database status
python -c "from database_enhanced import get_statistics; print(get_statistics())"

# Reinitialize database
python -c "from database_enhanced import init_db; init_db()"
```

**2. Missing Dependencies**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**3. API Key Issues**
```bash
# Check environment variables
python -c "import os; print('GEMINI_API_KEY:', bool(os.getenv('GEMINI_API_KEY')))"
```

**4. Port Already in Use**
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>
```

### Performance Optimization

**Database Performance:**
```python
# Enable query optimization
from database_enhanced import cleanup_old_data
cleanup_old_data(max_age_days=30, min_access_count=1)
```

**Memory Management:**
```python
# Clear cache
from database_enhanced import cache
cache.clear()
```

**AI Model Optimization:**
```python
# Use GPU acceleration (if available)
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

---

## 📈 Monitoring and Analytics

### System Health

Access the health endpoint to monitor system status:
```bash
curl http://localhost:8080/health
```

### Analytics Dashboard

The enhanced dashboard provides:
- **Real-time Statistics**: Knowledge base growth, user interactions
- **Performance Metrics**: Response times, error rates
- **Learning Progress**: Autonomous agent activity
- **Memory Usage**: Database and cache utilization
- **AI Model Performance**: Accuracy and confidence scores

### Logging

Logs are stored in:
- **Application Log**: `protype_ai.log`
- **Error Log**: Console output
- **Learning Log**: `learning_logs.json`
- **Agent Decisions**: `agent_decisions.json`

---

## 🛡️ Security

### Best Practices

1. **API Keys**: Store in environment variables, never in code
2. **Database**: Use strong passwords and connection encryption
3. **Network**: Use HTTPS in production
4. **Input Validation**: All user inputs are sanitized
5. **Rate Limiting**: Implemented for API endpoints

### Production Deployment

```bash
# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Use PostgreSQL for production
export DATABASE_URL=postgresql://user:pass@localhost:5432/protype_ai

# Enable Redis caching
export REDIS_URL=redis://localhost:6379/0

# Start with production server
gunicorn -w 4 -b 0.0.0.0:8080 web_app_enhanced:app
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/Protype-S-ai.git
cd Protype-S-ai

# Install development dependencies
pip install -r requirements.txt
pip install black flake8 pytest

# Run code formatting
black .

# Run linting
flake8 .

# Run tests
pytest
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Original Developer**: Islam Ibrahim, Director of Carrot Studio
- **Enhanced by**: AI Assistant
- **Inspiration**: The vision of creating truly intelligent AI systems
- **Community**: All contributors and users who make this project better

### Special Thanks

- Google for the Gemini API
- OpenAI for inspiration and research
- The Python community for excellent libraries
- All beta testers and early adopters

---

## 📞 Support

- **Documentation**: This README and inline code comments
- **Issues**: Please use GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions and ideas
- **Email**: Contact through GitHub profile

---

## 🗺️ Roadmap

### Version 2.1.0 (Planned)
- [ ] Enhanced mobile interface
- [ ] Voice conversation support
- [ ] Custom model fine-tuning
- [ ] Multi-language support
- [ ] Docker containerization

### Version 2.2.0 (Future)
- [ ] Federated learning capabilities
- [ ] Advanced visualization tools
- [ ] Integration with more AI models
- [ ] Enterprise features
- [ ] Cloud deployment options

---

**Built with ❤️ by Islam Ibrahim and enhanced by AI**

*Protype.AI Enhanced - Where artificial intelligence meets human creativity*