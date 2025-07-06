from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import logging
import traceback
import time
import json
from datetime import datetime, timedelta
import hashlib
import secrets

# Import our AI modules
try:
    from database import init_db, save_data, load_data, search_knowledge
    from self_reflection import self_reflection
    from advanced_memory import advanced_memory
    from multimodal_intelligence import multimodal_intelligence
    from autonomous_agent import autonomous_agent
    from knowledge_graph import KnowledgeGraph
    from learning_manager import learning_manager
    import google.generativeai as genai
except ImportError as e:
    print(f"Warning: Some modules could not be imported: {e}")

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('protype_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('protype_ai_enhanced')

# Initialize Flask app with enhanced configuration
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Enable CORS for cross-origin requests
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Enhanced security configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', secrets.token_hex(32)),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)

# Global variables for AI components
knowledge_graph = None
gemini_model = None

def initialize_ai_components():
    """Initialize all AI components"""
    global knowledge_graph, gemini_model
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Initialize Knowledge Graph
        knowledge_graph = KnowledgeGraph()
        knowledge_graph.build_from_database()
        logger.info("Knowledge graph initialized")
        
        # Initialize Gemini model
        GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', "AIzaSyBUDUURqkN5Lvid5P8V0ZXIRpseKC7ffMU")
        genai.configure(api_key=GEMINI_API_KEY)
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 4096,
        }
        
        gemini_model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
        )
        
        logger.info("Gemini model initialized")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing AI components: {e}")
        return False

def generate_session_id():
    """Generate a unique session ID"""
    return hashlib.sha256(f"{time.time()}{secrets.token_hex(16)}".encode()).hexdigest()[:16]

@app.before_request
def before_request():
    """Initialize session and handle security"""
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()
        session['created_at'] = datetime.now().isoformat()
        session.permanent = True

# Root route - Enhanced main interface
@app.route('/')
def index():
    """Serve the enhanced main interface"""
    try:
        # Try to serve the enhanced template first
        return render_template('index_enhanced.html')
    except:
        # Fallback to original template
        return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard interface"""
    return render_template('dashboard.html')

# Enhanced API endpoints
@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Enhanced chat endpoint with advanced AI processing"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Empty message'}), 400
            
        session_id = session.get('session_id', 'anonymous')
        
        # Log the user query
        logger.info(f"Chat request from session {session_id}: {message[:100]}...")
        
        # Process the message through our AI pipeline
        response = process_ai_message(message, session_id)
        
        # Save the interaction
        save_chat_interaction(session_id, message, response)
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'حدث خطأ في معالجة الرسالة. يرجى المحاولة مرة أخرى.',
            'details': str(e) if app.debug else None
        }), 500

def process_ai_message(message, session_id):
    """Process message through our advanced AI pipeline"""
    try:
        # Step 1: Search in advanced memory for relevant context
        memory_results = advanced_memory.search(message, k=3)
        context = ""
        if memory_results:
            context = "\n\nContext from memory:\n"
            for result in memory_results:
                context += f"Q: {result['question']}\nA: {result['answer']}\n\n"
        
        # Step 2: Get related concepts from knowledge graph
        if knowledge_graph:
            related_concepts = knowledge_graph.get_related_concepts(message, max_results=3)
            if related_concepts:
                context += "\nRelated concepts:\n"
                for concept in related_concepts:
                    context += f"- {concept['concept']} ({concept['relation']})\n"
        
        # Step 3: Generate response with Gemini
        if gemini_model:
            enhanced_prompt = f"""
            User question: {message}
            
            {context}
            
            Please provide a comprehensive, helpful response in Arabic. Use the context if relevant, but don't mention it explicitly.
            Be conversational, intelligent, and provide accurate information.
            """
            
            response = gemini_model.generate_content(enhanced_prompt)
            ai_response = response.text
            
            # Step 4: Self-reflection on the response
            reflection = self_reflection.verify_answer(message, ai_response)
            if not reflection['is_correct'] and reflection['improvement']:
                # Try to improve the response
                improved_prompt = f"""
                Original question: {message}
                Original answer: {ai_response}
                Improvement suggestion: {reflection['improvement']}
                
                Please provide an improved answer in Arabic that addresses the concerns raised.
                """
                improved_response = gemini_model.generate_content(improved_prompt)
                ai_response = improved_response.text
            
            # Step 5: Save to advanced memory
            advanced_memory.add_knowledge(message, ai_response, "gemini_chat", {
                'session_id': session_id,
                'reflection_score': reflection.get('confidence', 0.7)
            })
            
            return ai_response
        else:
            # Fallback response
            return "عذراً، النظام غير متاح حالياً. يرجى المحاولة لاحقاً."
            
    except Exception as e:
        logger.error(f"Error processing AI message: {e}")
        return f"عذراً، حدث خطأ في معالجة رسالتك: {str(e)}"

def save_chat_interaction(session_id, user_message, ai_response):
    """Save chat interaction to database"""
    try:
        # Save to main database
        save_data(
            question=f"chat_{session_id}_{int(time.time())}",
            answer=f"User: {user_message}\nAI: {ai_response}",
            weight=1.0,
            source="chat_interaction"
        )
    except Exception as e:
        logger.error(f"Error saving chat interaction: {e}")

@app.route('/api/search', methods=['GET'])
def search_endpoint():
    """Enhanced search endpoint"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        limit = int(request.args.get('limit', 10))
        limit = min(max(limit, 1), 50)  # Clamp between 1 and 50
        
        # Search in knowledge base
        results = search_knowledge(query, limit=limit)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'question': result[0],
                'answer': result[1],
                'source': result[3] if len(result) > 3 else 'unknown',
                'relevance': result[4] if len(result) > 4 else 1.0
            })
        
        return jsonify({
            'query': query,
            'results': formatted_results,
            'total': len(formatted_results)
        })
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/memory/search', methods=['POST'])
def memory_search_endpoint():
    """Search in advanced memory system"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        max_results = int(data.get('max_results', 5))
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        results = advanced_memory.search(query, k=max_results)
        
        return jsonify({
            'query': query,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in memory search: {e}")
        return jsonify({'error': 'Memory search failed'}), 500

@app.route('/api/memory/add', methods=['POST'])
def memory_add_endpoint():
    """Add knowledge to advanced memory"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        source = data.get('source', 'manual')
        
        if not question or not answer:
            return jsonify({'error': 'Question and answer are required'}), 400
        
        success = advanced_memory.add_knowledge(question, answer, source)
        
        if success:
            return jsonify({'message': 'Knowledge added successfully'})
        else:
            return jsonify({'error': 'Failed to add knowledge'}), 500
            
    except Exception as e:
        logger.error(f"Error adding to memory: {e}")
        return jsonify({'error': 'Failed to add knowledge'}), 500

@app.route('/api/reflection/evaluate', methods=['POST'])
def reflection_evaluate_endpoint():
    """Evaluate inference using self-reflection"""
    try:
        data = request.get_json()
        source = data.get('source', '').strip()
        target = data.get('target', '').strip()
        relation = data.get('relation', '').strip()
        confidence = float(data.get('confidence', 0.7))
        
        if not all([source, target, relation]):
            return jsonify({'error': 'Source, target, and relation are required'}), 400
        
        evaluation = self_reflection.evaluate_inference(source, target, relation, confidence)
        
        return jsonify(evaluation)
        
    except Exception as e:
        logger.error(f"Error in reflection evaluation: {e}")
        return jsonify({'error': 'Evaluation failed'}), 500

@app.route('/api/reflection/questions', methods=['POST'])
def reflection_questions_endpoint():
    """Generate critical thinking questions"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        count = int(data.get('count', 3))
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        questions = self_reflection.generate_critical_questions(topic, count)
        
        return jsonify({
            'topic': topic,
            'questions': questions
        })
        
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return jsonify({'error': 'Question generation failed'}), 500

@app.route('/api/multimodal/analyze-image', methods=['POST'])
def multimodal_analyze_image_endpoint():
    """Analyze image using multimodal intelligence"""
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        query = data.get('query', '')
        
        if not image_data:
            return jsonify({'error': 'Image data is required'}), 400
        
        result = multimodal_intelligence.analyze_image(image_data, query)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return jsonify({'error': 'Image analysis failed'}), 500

@app.route('/api/agent/start', methods=['POST'])
def agent_start_endpoint():
    """Start autonomous agent"""
    try:
        data = request.get_json() or {}
        autonomous_mode = data.get('autonomous_mode', False)
        
        result = autonomous_agent.start_agent(autonomous_mode)
        
        return jsonify({
            'message': result,
            'autonomous_mode': autonomous_mode
        })
        
    except Exception as e:
        logger.error(f"Error starting agent: {e}")
        return jsonify({'error': 'Failed to start agent'}), 500

@app.route('/api/agent/status', methods=['GET'])
def agent_status_endpoint():
    """Get autonomous agent status"""
    try:
        status = {
            'state': autonomous_agent.agent_state,
            'autonomous_mode': autonomous_agent.autonomous_mode,
            'objectives_count': len(autonomous_agent.objectives),
            'completed_count': len(autonomous_agent.completed_objectives),
            'knowledge_count': len(autonomous_agent.knowledge_gained)
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return jsonify({'error': 'Failed to get agent status'}), 500

@app.route('/api/learning/start', methods=['POST'])
def learning_start_endpoint():
    """Start continuous learning"""
    try:
        learning_manager.start_learning()
        return jsonify({'message': 'Learning started successfully'})
        
    except Exception as e:
        logger.error(f"Error starting learning: {e}")
        return jsonify({'error': 'Failed to start learning'}), 500

@app.route('/api/learning/stop', methods=['POST'])
def learning_stop_endpoint():
    """Stop continuous learning"""
    try:
        learning_manager.stop_learning()
        return jsonify({'message': 'Learning stopped successfully'})
        
    except Exception as e:
        logger.error(f"Error stopping learning: {e}")
        return jsonify({'error': 'Failed to stop learning'}), 500

@app.route('/api/learning/logs', methods=['GET'])
def learning_logs_endpoint():
    """Get learning logs"""
    try:
        limit = int(request.args.get('limit', 50))
        
        logs = learning_manager.logs.get('logs', [])
        recent_logs = logs[-limit:] if len(logs) > limit else logs
        
        return jsonify({
            'logs': recent_logs,
            'total': len(logs)
        })
        
    except Exception as e:
        logger.error(f"Error getting learning logs: {e}")
        return jsonify({'error': 'Failed to get learning logs'}), 500

@app.route('/api/knowledge-graph/data', methods=['GET'])
def knowledge_graph_data_endpoint():
    """Get knowledge graph visualization data"""
    try:
        if not knowledge_graph:
            return jsonify({'error': 'Knowledge graph not initialized'}), 500
        
        max_nodes = int(request.args.get('max_nodes', 100))
        data = knowledge_graph.get_visualization_data(max_nodes)
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error getting knowledge graph data: {e}")
        return jsonify({'error': 'Failed to get knowledge graph data'}), 500

@app.route('/api/stats', methods=['GET'])
def stats_endpoint():
    """Get system statistics"""
    try:
        data = load_data()
        
        stats = {
            'total_knowledge_items': len(data),
            'memory_entries': advanced_memory.index.ntotal if advanced_memory.index else 0,
            'graph_nodes': knowledge_graph.graph.number_of_nodes() if knowledge_graph else 0,
            'graph_edges': knowledge_graph.graph.number_of_edges() if knowledge_graph else 0,
            'agent_objectives': len(autonomous_agent.objectives),
            'agent_completed': len(autonomous_agent.completed_objectives),
            'learning_active': learning_manager.learning_active,
            'uptime': time.time() - getattr(app, 'start_time', time.time())
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    logger.error(traceback.format_exc())
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Access forbidden'}), 403

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({'error': 'Rate limit exceeded'}), 429

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

# Initialize AI components on startup
@app.before_first_request
def startup():
    """Initialize everything on startup"""
    app.start_time = time.time()
    logger.info("Starting Protype.AI Enhanced Web Application")
    
    success = initialize_ai_components()
    if success:
        logger.info("All AI components initialized successfully")
    else:
        logger.warning("Some AI components failed to initialize")

# Make sure this variable is exported
__all__ = ['app']

# For direct execution
if __name__ == "__main__":
    # Set debug mode based on environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Protype.AI Enhanced Web Server on http://0.0.0.0:8080")
    logger.info(f"Debug mode: {debug_mode}")
    
    app.run(
        host='0.0.0.0', 
        port=8080, 
        debug=debug_mode,
        threaded=True,
        use_reloader=False  # Disable reloader to prevent double initialization
    )