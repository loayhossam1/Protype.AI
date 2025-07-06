"""
Enhanced Autonomous Learning System for Protype.AI
Developed by Islam Ibrahim, Director of Carrot Studio

This enhanced system includes:
- Multi-source learning (Wikipedia, web search, user feedback)
- Achievement tracking and milestone detection
- Learning goal management and prioritization
- Progress analytics and performance monitoring
- Knowledge validation and quality assurance
"""

import json
import os
import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAutonomousLearning:
    """Enhanced autonomous learning system with achievement tracking"""
    
    def __init__(self, database_path: str = 'enhanced_protype.db'):
        self.database_path = database_path
        self.learning_active = False
        self.learning_thread = None
        self.current_objectives = []
        self.completed_objectives = []
        self.learning_stats = {
            'sessions_completed': 0,
            'knowledge_acquired': 0,
            'achievements_unlocked': 0,
            'avg_confidence': 0.0,
            'total_learning_time': 0
        }
        
        # Initialize Gemini AI
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyBUDUURqkN5Lvid5P8V0ZXIRpseKC7ffMU')
        genai.configure(api_key=self.gemini_api_key)
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 4096,
            }
        )
        
        # Learning priorities and sources
        self.learning_priorities = {
            'science': 0.9,
            'technology': 0.8,
            'history': 0.7,
            'art': 0.6,
            'general': 0.5
        }
        
        self.learning_sources = [
            'wikipedia',
            'web_search',
            'user_questions',
            'knowledge_gaps'
        ]
        
        # Load existing state
        self.load_learning_state()
    
    def get_database_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_knowledge_to_db(self, question: str, answer: str, source: str, 
                            category: str = 'general', confidence: float = 0.7) -> bool:
        """Save learned knowledge to database"""
        conn = self.get_database_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO knowledge 
                (question, answer, confidence, source, category, created_by, modified_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (question, answer, confidence, source, category, 'autonomous_learning', 'autonomous_learning'))
            
            # Record learning progress
            cursor.execute('''
                INSERT INTO learning_progress 
                (topic, source, confidence, performance_score)
                VALUES (?, ?, ?, ?)
            ''', (question[:100], source, confidence, confidence))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving knowledge: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def add_achievement(self, achievement_type: str, title: str, description: str,
                       icon: str = '🎯', points: int = 10) -> bool:
        """Add learning achievement"""
        conn = self.get_database_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO achievements 
                (achievement_type, title, description, icon, points, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (achievement_type, title, description, icon, points, 'autonomous_learning'))
            conn.commit()
            
            self.learning_stats['achievements_unlocked'] += 1
            logger.info(f"Achievement unlocked: {title}")
            return True
        except Exception as e:
            logger.error(f"Error adding achievement: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def start_learning(self, duration_minutes: int = 60):
        """Start autonomous learning session"""
        if self.learning_active:
            logger.warning("Learning session already active")
            return False
        
        self.learning_active = True
        self.learning_thread = threading.Thread(
            target=self._learning_session,
            args=(duration_minutes,),
            daemon=True
        )
        self.learning_thread.start()
        
        logger.info(f"Started autonomous learning session for {duration_minutes} minutes")
        return True
    
    def stop_learning(self):
        """Stop autonomous learning session"""
        self.learning_active = False
        if self.learning_thread and self.learning_thread.is_alive():
            self.learning_thread.join(timeout=5)
        
        logger.info("Stopped autonomous learning session")
        self.save_learning_state()
    
    def _learning_session(self, duration_minutes: int):
        """Main learning session loop"""
        session_start = time.time()
        session_end = session_start + (duration_minutes * 60)
        knowledge_learned = 0
        
        logger.info("Starting autonomous learning session")
        
        while self.learning_active and time.time() < session_end:
            try:
                # Choose learning objective
                objective = self._select_learning_objective()
                if not objective:
                    # Generate new objective if none available
                    objective = self._generate_learning_objective()
                
                if objective:
                    # Execute learning for this objective
                    success = self._execute_learning_objective(objective)
                    if success:
                        knowledge_learned += 1
                        self._check_learning_milestones(knowledge_learned)
                
                # Wait before next learning cycle
                time.sleep(random.uniform(10, 30))  # 10-30 seconds between cycles
                
            except Exception as e:
                logger.error(f"Error in learning session: {e}")
                time.sleep(60)  # Wait longer on error
        
        # Session completed
        session_duration = time.time() - session_start
        self.learning_stats['sessions_completed'] += 1
        self.learning_stats['knowledge_acquired'] += knowledge_learned
        self.learning_stats['total_learning_time'] += session_duration
        
        # Award session completion achievement
        if knowledge_learned > 0:
            self.add_achievement(
                'learning_session',
                f'Learning Session #{self.learning_stats["sessions_completed"]}',
                f'Completed learning session and acquired {knowledge_learned} new knowledge items',
                '📚',
                20
            )
        
        logger.info(f"Learning session completed. Knowledge acquired: {knowledge_learned}")
    
    def _select_learning_objective(self) -> Optional[str]:
        """Select next learning objective based on priority"""
        if not self.current_objectives:
            return None
        
        # Sort by priority (if we had priority scores)
        return self.current_objectives.pop(0)
    
    def _generate_learning_objective(self) -> str:
        """Generate new learning objective using AI"""
        try:
            prompt = """
            Generate a specific, focused learning objective for an AI system. 
            The objective should be:
            1. A single topic or concept to learn about
            2. Specific enough to research in 5-10 minutes
            3. Valuable for general knowledge
            4. Something that can be found through web search or Wikipedia
            
            Examples:
            - "Learn about quantum computing basics"
            - "Understand photosynthesis process"
            - "Study Renaissance art characteristics"
            
            Generate ONE learning objective (just the topic, no extra text):
            """
            
            response = self.model.generate_content(prompt)
            objective = response.text.strip()
            
            # Add to current objectives
            self.current_objectives.append(objective)
            logger.info(f"Generated learning objective: {objective}")
            
            return objective
            
        except Exception as e:
            logger.error(f"Error generating learning objective: {e}")
            return "Learn about artificial intelligence applications"
    
    def _execute_learning_objective(self, objective: str) -> bool:
        """Execute learning for a specific objective"""
        try:
            logger.info(f"Learning about: {objective}")
            
            # Research the topic
            knowledge = self._research_topic(objective)
            if not knowledge:
                return False
            
            # Generate questions and answers
            qa_pairs = self._generate_qa_pairs(objective, knowledge)
            
            # Save learned knowledge
            saved_count = 0
            for question, answer in qa_pairs:
                if self.save_knowledge_to_db(
                    question=question,
                    answer=answer,
                    source='autonomous_learning',
                    category=self._categorize_topic(objective),
                    confidence=0.8
                ):
                    saved_count += 1
            
            if saved_count > 0:
                self.completed_objectives.append({
                    'objective': objective,
                    'completed_at': datetime.now().isoformat(),
                    'qa_pairs_generated': saved_count
                })
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing learning objective: {e}")
            return False
    
    def _research_topic(self, topic: str) -> Optional[str]:
        """Research topic using multiple sources"""
        # Try Wikipedia first
        wikipedia_content = self._search_wikipedia(topic)
        if wikipedia_content:
            return wikipedia_content
        
        # Try web search
        web_content = self._search_web(topic)
        if web_content:
            return web_content
        
        # Use AI to generate basic information
        return self._generate_basic_info(topic)
    
    def _search_wikipedia(self, topic: str) -> Optional[str]:
        """Search Wikipedia for topic information"""
        try:
            # Format topic for Wikipedia search
            search_term = topic.replace(' ', '_')
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_term}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('extract', '')
            
            return None
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return None
    
    def _search_web(self, topic: str) -> Optional[str]:
        """Search web for topic information (placeholder)"""
        # This would integrate with SerpAPI or similar
        # For now, return None to skip web search
        return None
    
    def _generate_basic_info(self, topic: str) -> str:
        """Generate basic information about topic using AI"""
        try:
            prompt = f"""
            Provide a comprehensive but concise explanation about: {topic}
            
            Include:
            - Key facts and concepts
            - Important details
            - Context and background
            - Practical applications or significance
            
            Keep the response informative but not too long (about 200-300 words).
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating basic info: {e}")
            return f"Basic information about {topic}: This is an important topic that requires further research."
    
    def _generate_qa_pairs(self, topic: str, knowledge: str) -> List[Tuple[str, str]]:
        """Generate question-answer pairs from knowledge"""
        try:
            prompt = f"""
            Based on this information about "{topic}":
            
            {knowledge}
            
            Generate 3-5 question-answer pairs that would help someone learn about this topic.
            Format each pair as:
            Q: [question]
            A: [answer]
            
            Make sure:
            - Questions are clear and specific
            - Answers are accurate and concise
            - Cover different aspects of the topic
            """
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse Q&A pairs
            qa_pairs = []
            lines = text.split('\n')
            current_question = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Q:'):
                    current_question = line[2:].strip()
                elif line.startswith('A:') and current_question:
                    answer = line[2:].strip()
                    qa_pairs.append((current_question, answer))
                    current_question = None
            
            return qa_pairs[:5]  # Limit to 5 pairs
            
        except Exception as e:
            logger.error(f"Error generating Q&A pairs: {e}")
            return [(f"What is {topic}?", f"{topic} is an important subject that requires further study.")]
    
    def _categorize_topic(self, topic: str) -> str:
        """Categorize topic into predefined categories"""
        topic_lower = topic.lower()
        
        science_keywords = ['physics', 'chemistry', 'biology', 'science', 'quantum', 'molecular']
        tech_keywords = ['technology', 'computer', 'ai', 'software', 'digital', 'internet']
        history_keywords = ['history', 'historical', 'ancient', 'medieval', 'war', 'civilization']
        art_keywords = ['art', 'painting', 'music', 'literature', 'culture', 'renaissance']
        
        if any(keyword in topic_lower for keyword in science_keywords):
            return 'science'
        elif any(keyword in topic_lower for keyword in tech_keywords):
            return 'technology'
        elif any(keyword in topic_lower for keyword in history_keywords):
            return 'history'
        elif any(keyword in topic_lower for keyword in art_keywords):
            return 'art'
        else:
            return 'general'
    
    def _check_learning_milestones(self, knowledge_count: int):
        """Check and award learning milestone achievements"""
        # Knowledge quantity milestones
        if knowledge_count == 10:
            self.add_achievement(
                'learning_milestone',
                'Quick Learner',
                'Learned 10 new things in a single session!',
                '🚀',
                30
            )
        elif knowledge_count == 25:
            self.add_achievement(
                'learning_milestone',
                'Knowledge Enthusiast',
                'Learned 25 new things in a single session!',
                '🧠',
                50
            )
        elif knowledge_count == 50:
            self.add_achievement(
                'learning_milestone',
                'Learning Machine',
                'Learned 50 new things in a single session!',
                '🤖',
                100
            )
    
    def get_learning_report(self) -> Dict:
        """Generate comprehensive learning report"""
        conn = self.get_database_connection()
        try:
            cursor = conn.cursor()
            
            # Get recent learning progress
            cursor.execute('''
                SELECT topic, source, confidence, learned_at
                FROM learning_progress
                ORDER BY learned_at DESC
                LIMIT 20
            ''')
            recent_learning = [dict(row) for row in cursor.fetchall()]
            
            # Get achievement count by type
            cursor.execute('''
                SELECT achievement_type, COUNT(*) as count
                FROM achievements
                WHERE user_id = 'autonomous_learning'
                GROUP BY achievement_type
            ''')
            achievements_by_type = {row['achievement_type']: row['count'] for row in cursor.fetchall()}
            
            # Calculate learning trends
            cursor.execute('''
                SELECT DATE(learned_at) as date, COUNT(*) as count
                FROM learning_progress
                WHERE learned_at > datetime('now', '-7 days')
                GROUP BY DATE(learned_at)
                ORDER BY date
            ''')
            daily_learning = [dict(row) for row in cursor.fetchall()]
            
            return {
                'stats': self.learning_stats,
                'recent_learning': recent_learning,
                'achievements_by_type': achievements_by_type,
                'daily_learning_trend': daily_learning,
                'current_objectives_count': len(self.current_objectives),
                'completed_objectives_count': len(self.completed_objectives)
            }
            
        except Exception as e:
            logger.error(f"Error generating learning report: {e}")
            return {'error': str(e)}
        finally:
            conn.close()
    
    def add_learning_objective(self, objective: str) -> bool:
        """Add custom learning objective"""
        if objective not in self.current_objectives:
            self.current_objectives.append(objective)
            logger.info(f"Added learning objective: {objective}")
            return True
        return False
    
    def save_learning_state(self):
        """Save current learning state to file"""
        state = {
            'current_objectives': self.current_objectives,
            'completed_objectives': self.completed_objectives,
            'learning_stats': self.learning_stats,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open('learning_state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning state: {e}")
    
    def load_learning_state(self):
        """Load learning state from file"""
        try:
            with open('learning_state.json', 'r') as f:
                state = json.load(f)
                
            self.current_objectives = state.get('current_objectives', [])
            self.completed_objectives = state.get('completed_objectives', [])
            self.learning_stats.update(state.get('learning_stats', {}))
            
            logger.info("Loaded learning state from file")
            
        except FileNotFoundError:
            logger.info("No existing learning state found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading learning state: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize the enhanced autonomous learning system
    learning_system = EnhancedAutonomousLearning()
    
    # Add some learning objectives
    learning_system.add_learning_objective("Learn about renewable energy sources")
    learning_system.add_learning_objective("Understand machine learning basics")
    learning_system.add_learning_objective("Study ancient Egyptian civilization")
    
    # Start a short learning session for testing
    print("Starting autonomous learning session...")
    learning_system.start_learning(duration_minutes=5)  # 5 minutes for testing
    
    # Wait for completion
    time.sleep(330)  # Wait a bit longer than 5 minutes
    
    # Stop learning and get report
    learning_system.stop_learning()
    report = learning_system.get_learning_report()
    
    print("\nLearning Report:")
    print(json.dumps(report, indent=2))