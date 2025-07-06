"""
Enhanced Protype.AI Web Application
Developed by Islam Ibrahim, Director of Carrot Studio

This enhanced version includes:
- Modern Material Design UI with dark/light themes
- Achievement tracking system
- Real-time learning analytics
- Enhanced database with user progress
- Professional dashboard with advanced features
- Better AI learning capabilities
- Knowledge graph visualization
- Responsive design for all devices
"""

import json
import os
import random
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
import sqlite3
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests
import networkx as nx
import uuid
import hashlib
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with enhanced configuration
app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
CORS(app)  # Enable CORS for API access

# Enhanced Database Schema
DATABASE_PATH = 'enhanced_protype.db'

class EnhancedDatabase:
    """Enhanced database manager with achievement tracking and analytics"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize enhanced database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Enhanced knowledge table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT UNIQUE NOT NULL,
                    answer TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    source TEXT DEFAULT 'user',
                    category TEXT DEFAULT 'general',
                    tags TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT DEFAULT 'system',
                    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_by TEXT DEFAULT 'system',
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 1.0,
                    is_validated BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # User sessions and interactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id TEXT DEFAULT 'anonymous',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_queries INTEGER DEFAULT 0,
                    total_time_spent INTEGER DEFAULT 0,
                    satisfaction_score REAL DEFAULT NULL
                )
            ''')
            
            # AI Learning Progress
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    subtopic TEXT DEFAULT '',
                    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT DEFAULT 'autonomous',
                    confidence REAL DEFAULT 0.5,
                    related_questions INTEGER DEFAULT 0,
                    performance_score REAL DEFAULT 0.5,
                    is_milestone BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Achievement System
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    achievement_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    icon TEXT DEFAULT '🏆',
                    points INTEGER DEFAULT 10,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    criteria_met TEXT,
                    user_id TEXT DEFAULT 'system'
                )
            ''')
            
            # Knowledge Graph Relationships
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_concept TEXT NOT NULL,
                    target_concept TEXT NOT NULL,
                    relationship_type TEXT DEFAULT 'related',
                    strength REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    validated BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # AI Performance Metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    context TEXT DEFAULT '',
                    source TEXT DEFAULT 'system'
                )
            ''')
            
            # Create indexes for better performance
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_knowledge_question ON knowledge(question)',
                'CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category)',
                'CREATE INDEX IF NOT EXISTS idx_knowledge_created_at ON knowledge(created_at)',
                'CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)',
                'CREATE INDEX IF NOT EXISTS idx_learning_topic ON learning_progress(topic)',
                'CREATE INDEX IF NOT EXISTS idx_achievements_type ON achievements(achievement_type)',
                'CREATE INDEX IF NOT EXISTS idx_relationships_concepts ON knowledge_relationships(source_concept, target_concept)',
                'CREATE INDEX IF NOT EXISTS idx_metrics_type ON performance_metrics(metric_type)'
            ]
            
            for index in indexes:
                cursor.execute(index)
            
            conn.commit()
            logger.info("Enhanced database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def save_knowledge(self, question: str, answer: str, source: str = 'user', 
                      category: str = 'general', confidence: float = 0.5,
                      created_by: str = 'system') -> bool:
        """Save knowledge with enhanced metadata"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if question exists
            cursor.execute('SELECT id FROM knowledge WHERE question = ?', (question,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing knowledge
                cursor.execute('''
                    UPDATE knowledge 
                    SET answer = ?, confidence = ?, source = ?, category = ?,
                        modified_at = CURRENT_TIMESTAMP, modified_by = ?,
                        usage_count = usage_count + 1
                    WHERE question = ?
                ''', (answer, confidence, source, category, created_by, question))
            else:
                # Insert new knowledge
                cursor.execute('''
                    INSERT INTO knowledge 
                    (question, answer, confidence, source, category, created_by, modified_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (question, answer, confidence, source, category, created_by, created_by))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving knowledge: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def search_knowledge(self, query: str, limit: int = 10) -> List[Dict]:
        """Enhanced knowledge search with ranking"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Enhanced search with multiple criteria
            search_query = '''
                SELECT question, answer, confidence, source, category, usage_count, success_rate
                FROM knowledge 
                WHERE question LIKE ? OR answer LIKE ? OR category LIKE ?
                ORDER BY confidence DESC, usage_count DESC, success_rate DESC
                LIMIT ?
            '''
            
            search_term = f'%{query}%'
            cursor.execute(search_query, (search_term, search_term, search_term, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'question': row['question'],
                    'answer': row['answer'],
                    'confidence': row['confidence'],
                    'source': row['source'],
                    'category': row['category'],
                    'usage_count': row['usage_count'],
                    'success_rate': row['success_rate']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
        finally:
            conn.close()
    
    def get_analytics_data(self) -> Dict:
        """Get comprehensive analytics data"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Knowledge statistics
            cursor.execute('SELECT COUNT(*) as total FROM knowledge')
            total_knowledge = cursor.fetchone()['total']
            
            cursor.execute('SELECT COUNT(DISTINCT category) as categories FROM knowledge')
            total_categories = cursor.fetchone()['categories']
            
            cursor.execute('SELECT AVG(confidence) as avg_confidence FROM knowledge')
            avg_confidence = cursor.fetchone()['avg_confidence'] or 0
            
            # Learning progress
            cursor.execute('SELECT COUNT(*) as learned_topics FROM learning_progress')
            learned_topics = cursor.fetchone()['learned_topics']
            
            # Achievements
            cursor.execute('SELECT COUNT(*) as total_achievements FROM achievements')
            total_achievements = cursor.fetchone()['total_achievements']
            
            # Recent activity
            cursor.execute('''
                SELECT COUNT(*) as recent_activity 
                FROM knowledge 
                WHERE created_at > datetime('now', '-7 days')
            ''')
            recent_activity = cursor.fetchone()['recent_activity']
            
            return {
                'total_knowledge': total_knowledge,
                'total_categories': total_categories,
                'avg_confidence': round(avg_confidence, 2),
                'learned_topics': learned_topics,
                'total_achievements': total_achievements,
                'recent_activity': recent_activity,
                'knowledge_growth_rate': round(recent_activity / 7, 1)  # per day
            }
            
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {}
        finally:
            conn.close()
    
    def add_achievement(self, achievement_type: str, title: str, description: str = '',
                       icon: str = '🏆', points: int = 10, user_id: str = 'system') -> bool:
        """Add new achievement"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO achievements (achievement_type, title, description, icon, points, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (achievement_type, title, description, icon, points, user_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding achievement: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

# Initialize enhanced database
db = EnhancedDatabase()

# Enhanced AI Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBUDUURqkN5Lvid5P8V0ZXIRpseKC7ffMU')
genai.configure(api_key=GEMINI_API_KEY)

# Enhanced Gemini model configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

gemini_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

class EnhancedAIManager:
    """Enhanced AI manager with learning capabilities"""
    
    def __init__(self):
        self.chat_session = gemini_model.start_chat(history=[])
        self.learning_active = False
        self.learning_thread = None
    
    def process_query(self, question: str, session_id: str = None) -> Dict:
        """Process user query with enhanced response"""
        start_time = time.time()
        
        # First, search local knowledge
        local_results = db.search_knowledge(question, limit=3)
        
        if local_results and local_results[0]['confidence'] > 0.7:
            # Use local knowledge with high confidence
            best_result = local_results[0]
            response = best_result['answer']
            source = f"local_knowledge_{best_result['source']}"
            confidence = best_result['confidence']
        else:
            # Query Gemini for new information
            try:
                gemini_response = self.chat_session.send_message(question)
                response = gemini_response.text.strip()
                source = "gemini_ai"
                confidence = 0.8
                
                # Save new knowledge to database
                db.save_knowledge(question, response, source, 'general', confidence, 'ai_system')
                
                # Check for achievement
                self._check_learning_achievements()
                
            except Exception as e:
                logger.error(f"Gemini query error: {e}")
                response = "I apologize, but I'm having trouble processing your request right now. Please try again later."
                source = "error"
                confidence = 0.1
        
        processing_time = time.time() - start_time
        
        # Record performance metrics
        self._record_performance_metric('response_time', processing_time)
        self._record_performance_metric('confidence_score', confidence)
        
        return {
            'response': response,
            'source': source,
            'confidence': confidence,
            'processing_time': round(processing_time, 3),
            'suggestions': self._get_related_suggestions(question)
        }
    
    def _get_related_suggestions(self, question: str) -> List[str]:
        """Get related question suggestions"""
        related = db.search_knowledge(question, limit=5)
        suggestions = []
        
        for item in related:
            if item['question'].lower() != question.lower():
                suggestions.append(item['question'])
        
        return suggestions[:3]
    
    def _check_learning_achievements(self):
        """Check and award learning achievements"""
        analytics = db.get_analytics_data()
        
        # Knowledge milestones
        if analytics['total_knowledge'] >= 100 and analytics['total_knowledge'] % 100 == 0:
            db.add_achievement(
                'knowledge_milestone',
                f'Knowledge Master {analytics["total_knowledge"]}',
                f'Accumulated {analytics["total_knowledge"]} pieces of knowledge!',
                '🧠',
                50
            )
        
        # Learning streak achievements
        if analytics['knowledge_growth_rate'] > 10:
            db.add_achievement(
                'learning_streak',
                'Learning Enthusiast',
                'Learning more than 10 new things per day!',
                '🔥',
                25
            )
    
    def _record_performance_metric(self, metric_type: str, value: float):
        """Record performance metric"""
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO performance_metrics (metric_type, metric_value)
                VALUES (?, ?)
            ''', (metric_type, value))
            conn.commit()
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
        finally:
            conn.close()

# Initialize AI manager
ai_manager = EnhancedAIManager()

# Enhanced Routes
@app.route('/')
def index():
    """Enhanced main page"""
    return render_template('enhanced_index.html')

@app.route('/dashboard')
def dashboard():
    """Enhanced dashboard with analytics"""
    analytics = db.get_analytics_data()
    return render_template('enhanced_dashboard.html', analytics=analytics)

@app.route('/api/chat', methods=['POST'])
def enhanced_chat():
    """Enhanced chat endpoint with session tracking"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        session_id = session.get('session_id')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Generate session ID if not exists
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Process the query
        result = ai_manager.process_query(question, session_id or str(uuid.uuid4()))
        
        return jsonify({
            'success': True,
            'answer': result['response'],
            'source': result['source'],
            'confidence': result['confidence'],
            'processing_time': result['processing_time'],
            'suggestions': result['suggestions'],
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        analytics = db.get_analytics_data()
        return jsonify({'success': True, 'data': analytics})
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({'error': 'Failed to get analytics'}), 500

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    """Get user achievements"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT achievement_type, title, description, icon, points, unlocked_at
            FROM achievements
            ORDER BY unlocked_at DESC
            LIMIT 20
        ''')
        
        achievements = []
        for row in cursor.fetchall():
            achievements.append({
                'type': row['achievement_type'],
                'title': row['title'],
                'description': row['description'],
                'icon': row['icon'],
                'points': row['points'],
                'unlocked_at': row['unlocked_at']
            })
        
        conn.close()
        return jsonify({'success': True, 'achievements': achievements})
        
    except Exception as e:
        logger.error(f"Achievements error: {e}")
        return jsonify({'error': 'Failed to get achievements'}), 500

@app.route('/api/teach', methods=['POST'])
def teach_ai():
    """Enhanced teaching endpoint"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        category = data.get('category', 'general')
        confidence = float(data.get('confidence', 0.8))
        
        if not question or not answer:
            return jsonify({'error': 'Question and answer are required'}), 400
        
        success = db.save_knowledge(question, answer, 'user_taught', category, confidence, 'user')
        
        if success:
            # Award teaching achievement
            db.add_achievement(
                'teaching',
                'Knowledge Contributor',
                f'Taught the AI about: {question[:50]}...',
                '👨‍🏫',
                15
            )
            
            return jsonify({'success': True, 'message': 'Knowledge added successfully'})
        else:
            return jsonify({'error': 'Failed to save knowledge'}), 500
            
    except Exception as e:
        logger.error(f"Teaching error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/search', methods=['POST'])
def enhanced_search():
    """Enhanced search endpoint"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = int(data.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        results = db.search_knowledge(query, limit)
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('enhanced_404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('enhanced_500.html'), 500

if __name__ == '__main__':
    # Initialize database and start the application
    logger.info("Starting Enhanced Protype.AI Web Application")
    app.run(host='0.0.0.0', port=8080, debug=True)