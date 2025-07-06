#!/usr/bin/env python3
"""
Advanced Learning System for Protype.AI
A simplified but more effective learning system that can learn from:
1. Attached data files (txt, json, md, csv, pdf)
2. Internet sources (web search, articles, etc.)
3. Self-directed learning based on knowledge gaps

Author: Enhanced by AI Assistant
"""

import os
import json
import time
import sqlite3
import requests
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib
import re

# AI and NLP libraries
try:
    import google.generativeai as genai
    from bs4 import BeautifulSoup
    import spacy
    # Try to load spaCy model, download if not available
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("SpaCy model not found. Installing...")
        os.system("python -m spacy download en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Please install required packages: pip install google-generativeai beautifulsoup4 spacy")

class SmartLearningSystem:
    def __init__(self, db_path: str = "smart_knowledge.db"):
        self.db_path = db_path
        self.learning_active = False
        self.learning_thread = None
        self.knowledge_cache = {}
        self.learning_log = []
        
        # Initialize Gemini API
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY', "AIzaSyBUDUURqkN5Lvid5P8V0ZXIRpseKC7ffMU")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize database
        self.init_database()
        
        # Load existing knowledge
        self.load_knowledge_cache()
        
        print("Smart Learning System initialized successfully!")
    
    def init_database(self):
        """Initialize the knowledge database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create knowledge table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL DEFAULT 0.7,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                keywords TEXT,
                content_hash TEXT UNIQUE
            )
        ''')
        
        # Create learning log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create indexes for faster search
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_topic ON knowledge(topic)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords ON knowledge(keywords)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON knowledge(source)')
        
        conn.commit()
        conn.close()
    
    def load_knowledge_cache(self):
        """Load knowledge into memory for faster access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT topic, content, source, confidence FROM knowledge ORDER BY confidence DESC LIMIT 1000')
        results = cursor.fetchall()
        
        for topic, content, source, confidence in results:
            if topic not in self.knowledge_cache:
                self.knowledge_cache[topic] = []
            self.knowledge_cache[topic].append({
                'content': content,
                'source': source,
                'confidence': confidence
            })
        
        conn.close()
        print(f"Loaded {len(results)} knowledge entries into cache")
    
    def log_learning_activity(self, action: str, details: str = "", success: bool = True):
        """Log learning activities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_log (action, details, success)
            VALUES (?, ?, ?)
        ''', (action, details, success))
        
        conn.commit()
        conn.close()
        
        # Also keep in memory log
        self.learning_log.append({
            'action': action,
            'details': details,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using spaCy"""
        try:
            doc = nlp(text)
            keywords = []
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT', 'WORK_OF_ART']:
                    keywords.append(ent.text.lower())
            
            # Extract important nouns and adjectives
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                    len(token.text) > 2 and 
                    not token.is_stop and 
                    token.is_alpha):
                    keywords.append(token.lemma_.lower())
            
            return list(set(keywords))
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def store_knowledge(self, topic: str, content: str, source: str, confidence: float = 0.7):
        """Store knowledge in database"""
        try:
            # Create content hash to avoid duplicates
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Extract keywords
            keywords = self.extract_keywords(content)
            keywords_str = ",".join(keywords)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if content already exists
            cursor.execute('SELECT id FROM knowledge WHERE content_hash = ?', (content_hash,))
            if cursor.fetchone():
                conn.close()
                return False  # Already exists
            
            cursor.execute('''
                INSERT INTO knowledge (topic, content, source, confidence, keywords, content_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (topic, content, source, confidence, keywords_str, content_hash))
            
            conn.commit()
            conn.close()
            
            # Update cache
            if topic not in self.knowledge_cache:
                self.knowledge_cache[topic] = []
            self.knowledge_cache[topic].append({
                'content': content,
                'source': source,
                'confidence': confidence
            })
            
            self.log_learning_activity("store_knowledge", f"Stored knowledge about '{topic}' from {source}")
            return True
            
        except Exception as e:
            print(f"Error storing knowledge: {e}")
            self.log_learning_activity("store_knowledge", f"Failed to store knowledge: {e}", False)
            return False
    
    def learn_from_attached_files(self, directory: str = "attached_assets"):
        """Learn from all attached files in the directory"""
        try:
            assets_path = Path(directory)
            if not assets_path.exists():
                self.log_learning_activity("learn_from_files", f"Directory {directory} not found", False)
                return
            
            files_processed = 0
            
            # Process all text files
            for file_path in assets_path.glob("**/*"):
                if file_path.is_file():
                    try:
                        # Skip binary files
                        if file_path.suffix.lower() in ['.txt', '.md', '.json', '.csv', '.py', '.js', '.html']:
                            content = file_path.read_text(encoding='utf-8')
                            
                            # Extract topic from filename
                            topic = file_path.stem.replace('-', ' ').replace('_', ' ')
                            
                            # Break content into chunks if it's too large
                            if len(content) > 5000:
                                chunks = self.chunk_text(content, 3000)
                                for i, chunk in enumerate(chunks):
                                    self.store_knowledge(
                                        topic=f"{topic} (part {i+1})",
                                        content=chunk,
                                        source=f"file:{file_path.name}",
                                        confidence=0.9  # High confidence for user files
                                    )
                            else:
                                self.store_knowledge(
                                    topic=topic,
                                    content=content,
                                    source=f"file:{file_path.name}",
                                    confidence=0.9
                                )
                            
                            files_processed += 1
                            
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        continue
            
            self.log_learning_activity("learn_from_files", f"Processed {files_processed} files from {directory}")
            
        except Exception as e:
            print(f"Error learning from files: {e}")
            self.log_learning_activity("learn_from_files", f"Error: {e}", False)
    
    def chunk_text(self, text: str, max_length: int = 3000) -> List[str]:
        """Split text into chunks for better processing"""
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def web_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search the web for information"""
        try:
            # Use a simple search approach (can be enhanced with Google API)
            search_url = f"https://www.google.com/search?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Extract search results
            for result in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd')[:max_results]:
                text = result.get_text()
                if len(text) > 50:  # Filter out short/useless results
                    results.append({
                        'title': text[:100],
                        'content': text,
                        'source': 'web_search'
                    })
            
            return results
            
        except Exception as e:
            print(f"Error in web search: {e}")
            return []
    
    def learn_from_web(self, topics: List[str]):
        """Learn from web search results"""
        try:
            for topic in topics:
                self.log_learning_activity("web_search", f"Searching for: {topic}")
                
                # Search for the topic
                search_results = self.web_search(topic)
                
                if search_results:
                    # Combine search results
                    combined_content = "\n\n".join([r['content'] for r in search_results])
                    
                    # Store the knowledge
                    self.store_knowledge(
                        topic=topic,
                        content=combined_content,
                        source="web_search",
                        confidence=0.6
                    )
                    
                    print(f"Learned about '{topic}' from web search")
                else:
                    print(f"No web results found for '{topic}'")
                    
                # Small delay to be respectful
                time.sleep(1)
                
        except Exception as e:
            print(f"Error learning from web: {e}")
            self.log_learning_activity("web_search", f"Error: {e}", False)
    
    def learn_with_ai(self, topics: List[str]):
        """Learn using AI model (Gemini)"""
        try:
            if not hasattr(self, 'gemini_model'):
                print("Gemini API not available")
                return
                
            for topic in topics:
                prompt = f"""
                Please provide comprehensive information about '{topic}'. 
                Include:
                1. A clear explanation of what it is
                2. Key concepts and principles
                3. Important facts and details
                4. Current developments or trends
                5. Why it's important or relevant
                
                Make the information educational and easy to understand.
                """
                
                try:
                    response = self.gemini_model.generate_content(prompt)
                    
                    if response.text:
                        self.store_knowledge(
                            topic=topic,
                            content=response.text,
                            source="gemini_ai",
                            confidence=0.8
                        )
                        
                        print(f"Learned about '{topic}' using AI")
                        self.log_learning_activity("ai_learning", f"Learned about: {topic}")
                    
                except Exception as e:
                    print(f"Error learning about '{topic}' with AI: {e}")
                    continue
                    
                # Small delay to respect API limits
                time.sleep(2)
                
        except Exception as e:
            print(f"Error in AI learning: {e}")
            self.log_learning_activity("ai_learning", f"Error: {e}", False)
    
    def identify_knowledge_gaps(self) -> List[str]:
        """Identify areas where knowledge is lacking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get topics with low confidence or few entries
            cursor.execute('''
                SELECT topic, COUNT(*) as count, AVG(confidence) as avg_confidence
                FROM knowledge
                GROUP BY topic
                HAVING count < 3 OR avg_confidence < 0.7
                ORDER BY count ASC, avg_confidence ASC
                LIMIT 10
            ''')
            
            weak_topics = [row[0] for row in cursor.fetchall()]
            
            # Also suggest related topics based on keywords
            cursor.execute('''
                SELECT keywords FROM knowledge
                WHERE keywords IS NOT NULL AND keywords != ""
                ORDER BY confidence DESC
                LIMIT 50
            ''')
            
            all_keywords = []
            for row in cursor.fetchall():
                all_keywords.extend(row[0].split(','))
            
            # Find most common keywords that don't have dedicated topics
            from collections import Counter
            keyword_counts = Counter(all_keywords)
            
            suggested_topics = []
            for keyword, count in keyword_counts.most_common(5):
                if keyword not in [t.lower() for t in weak_topics] and len(keyword) > 3:
                    suggested_topics.append(keyword.title())
            
            conn.close()
            
            return weak_topics + suggested_topics
            
        except Exception as e:
            print(f"Error identifying knowledge gaps: {e}")
            return []
    
    def start_autonomous_learning(self):
        """Start autonomous learning process"""
        if self.learning_active:
            print("Learning already active")
            return
        
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        self.learning_thread.start()
        
        print("Autonomous learning started!")
        self.log_learning_activity("start_learning", "Autonomous learning started")
    
    def stop_learning(self):
        """Stop autonomous learning"""
        self.learning_active = False
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
        
        print("Learning stopped")
        self.log_learning_activity("stop_learning", "Autonomous learning stopped")
    
    def _learning_loop(self):
        """Main learning loop"""
        cycle_count = 0
        
        while self.learning_active:
            try:
                cycle_count += 1
                print(f"Learning cycle {cycle_count}")
                
                # Step 1: Learn from attached files (every cycle)
                self.learn_from_attached_files()
                
                # Step 2: Identify knowledge gaps
                gaps = self.identify_knowledge_gaps()
                
                if gaps:
                    print(f"Found {len(gaps)} knowledge gaps: {gaps[:3]}...")
                    
                    # Step 3: Learn from web (every other cycle)
                    if cycle_count % 2 == 0:
                        self.learn_from_web(gaps[:3])
                    
                    # Step 4: Learn with AI (every third cycle)
                    if cycle_count % 3 == 0:
                        self.learn_with_ai(gaps[:2])
                
                # Step 5: Clean up and optimize (every 10 cycles)
                if cycle_count % 10 == 0:
                    self.optimize_knowledge_base()
                
                # Wait before next cycle
                time.sleep(30)  # 30 seconds between cycles
                
            except Exception as e:
                print(f"Error in learning loop: {e}")
                self.log_learning_activity("learning_loop", f"Error: {e}", False)
                time.sleep(60)  # Wait longer on error
    
    def optimize_knowledge_base(self):
        """Optimize the knowledge base by removing duplicates and improving quality"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove entries with very low confidence
            cursor.execute('DELETE FROM knowledge WHERE confidence < 0.3')
            
            # Update cache
            self.load_knowledge_cache()
            
            conn.commit()
            conn.close()
            
            self.log_learning_activity("optimization", "Knowledge base optimized")
            
        except Exception as e:
            print(f"Error optimizing knowledge base: {e}")
    
    def search_knowledge(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search the knowledge base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search by topic, content, and keywords
            cursor.execute('''
                SELECT topic, content, source, confidence
                FROM knowledge
                WHERE topic LIKE ? OR content LIKE ? OR keywords LIKE ?
                ORDER BY confidence DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', max_results))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'topic': row[0],
                    'content': row[1],
                    'source': row[2],
                    'confidence': row[3]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []
    
    def get_learning_statistics(self) -> Dict:
        """Get statistics about the learning system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute('SELECT COUNT(*) FROM knowledge')
            total_knowledge = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT topic) FROM knowledge')
            unique_topics = cursor.fetchone()[0]
            
            cursor.execute('SELECT source, COUNT(*) FROM knowledge GROUP BY source')
            sources = dict(cursor.fetchall())
            
            cursor.execute('SELECT AVG(confidence) FROM knowledge')
            avg_confidence = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(*) FROM learning_log WHERE success = 1')
            successful_activities = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM learning_log WHERE success = 0')
            failed_activities = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_knowledge_entries': total_knowledge,
                'unique_topics': unique_topics,
                'sources': sources,
                'average_confidence': round(avg_confidence, 2),
                'successful_activities': successful_activities,
                'failed_activities': failed_activities,
                'learning_active': self.learning_active
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def teach_custom_knowledge(self, topic: str, content: str):
        """Allow users to teach custom knowledge"""
        success = self.store_knowledge(
            topic=topic,
            content=content,
            source="user_input",
            confidence=0.95  # High confidence for user input
        )
        
        if success:
            print(f"Successfully learned about '{topic}'")
            return True
        else:
            print(f"Failed to learn about '{topic}' (might be duplicate)")
            return False

# Create singleton instance
smart_learning_system = SmartLearningSystem()

# Example usage and simple interface
def main():
    """Simple interface for testing the learning system"""
    print("=== Smart Learning System ===")
    print("1. Start learning from attached files")
    print("2. Start autonomous learning")
    print("3. Search knowledge")
    print("4. Get statistics")
    print("5. Teach custom knowledge")
    print("6. Stop learning")
    
    while True:
        choice = input("\nEnter your choice (1-6, or 'q' to quit): ").strip()
        
        if choice == 'q':
            smart_learning_system.stop_learning()
            break
        elif choice == '1':
            smart_learning_system.learn_from_attached_files()
        elif choice == '2':
            smart_learning_system.start_autonomous_learning()
        elif choice == '3':
            query = input("Enter search query: ")
            results = smart_learning_system.search_knowledge(query)
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['topic']} (confidence: {result['confidence']})")
                print(f"   Source: {result['source']}")
                print(f"   Content: {result['content'][:200]}...")
        elif choice == '4':
            stats = smart_learning_system.get_learning_statistics()
            print("\nLearning Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        elif choice == '5':
            topic = input("Enter topic: ")
            content = input("Enter content: ")
            smart_learning_system.teach_custom_knowledge(topic, content)
        elif choice == '6':
            smart_learning_system.stop_learning()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()