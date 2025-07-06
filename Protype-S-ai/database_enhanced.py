import os
import sqlite3
import json
import pickle
import hashlib
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
import logging

# Import redis with fallback
try:
    import redis
except ImportError:
    redis = None

# Setup logging
logger = logging.getLogger('database_enhanced')

# Check environment and configuration
USING_POSTGRES = 'DATABASE_URL' in os.environ
USING_REDIS = 'REDIS_URL' in os.environ or os.path.exists('/usr/bin/redis-server')

# Connection pools
pg_pool = None
redis_client = None

# SQLite configuration
SQLITE_DB_PATH = 'protype_e0.db'
SQLITE_POOL_SIZE = 10
sqlite_connections = []
sqlite_lock = threading.Lock()

# Cache configuration
CACHE_TTL = 3600  # 1 hour default TTL
CACHE_PREFIX = "protype_ai:"

class DatabaseError(Exception):
    """Custom database error"""
    pass

class CacheManager:
    """Enhanced cache manager with Redis fallback to memory"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.memory_cache_lock = threading.Lock()
        self.init_redis()
    
    def init_redis(self):
        """Initialize Redis connection"""
        try:
            if USING_REDIS and redis is not None:
                redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            else:
                logger.info("Redis not available, using memory cache")
        except Exception as e:
            logger.warning(f"Redis connection failed, falling back to memory cache: {e}")
            self.redis_client = None
    
    def _get_key(self, key: str) -> str:
        """Get prefixed cache key"""
        return f"{CACHE_PREFIX}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            cache_key = self._get_key(key)
            
            if self.redis_client:
                value = self.redis_client.get(cache_key)
                if value:
                    return pickle.loads(value.encode('latin1'))
            else:
                with self.memory_cache_lock:
                    cache_entry = self.memory_cache.get(cache_key)
                    if cache_entry and cache_entry['expires'] > time.time():
                        return cache_entry['value']
                    elif cache_entry:
                        del self.memory_cache[cache_key]
            
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
        """Set value in cache"""
        try:
            cache_key = self._get_key(key)
            
            if self.redis_client:
                serialized = pickle.dumps(value).decode('latin1')
                return self.redis_client.setex(cache_key, ttl, serialized)
            else:
                with self.memory_cache_lock:
                    self.memory_cache[cache_key] = {
                        'value': value,
                        'expires': time.time() + ttl
                    }
                    return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            cache_key = self._get_key(key)
            
            if self.redis_client:
                return bool(self.redis_client.delete(cache_key))
            else:
                with self.memory_cache_lock:
                    return bool(self.memory_cache.pop(cache_key, None))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(f"{CACHE_PREFIX}*")
                if keys:
                    return bool(self.redis_client.delete(*keys))
                return True
            else:
                with self.memory_cache_lock:
                    self.memory_cache.clear()
                    return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

# Global cache manager
cache = CacheManager()

def init_postgres_pool():
    """Initialize PostgreSQL connection pool"""
    global pg_pool
    
    if not USING_POSTGRES:
        return False
    
    try:
        import psycopg2
        from psycopg2 import pool
        
        database_url = os.environ['DATABASE_URL']
        pg_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            dsn=database_url
        )
        logger.info("PostgreSQL connection pool initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL pool: {e}")
        return False

def init_sqlite_pool():
    """Initialize SQLite connection pool"""
    global sqlite_connections
    
    try:
        with sqlite_lock:
            sqlite_connections = []
            for _ in range(SQLITE_POOL_SIZE):
                conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
                conn.row_factory = sqlite3.Row  # Enable dict-like access
                sqlite_connections.append(conn)
        
        logger.info(f"SQLite connection pool initialized with {SQLITE_POOL_SIZE} connections")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize SQLite pool: {e}")
        return False

@contextmanager
def get_connection():
    """Get database connection with proper resource management"""
    conn = None
    is_postgres = False
    
    try:
        if USING_POSTGRES and pg_pool:
            conn = pg_pool.getconn()
            is_postgres = True
        else:
            # Get SQLite connection from pool
            with sqlite_lock:
                if sqlite_connections:
                    conn = sqlite_connections.pop()
                else:
                    conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
                    conn.row_factory = sqlite3.Row
        
        if conn is None:
            raise DatabaseError("Failed to get database connection")
        
        yield conn, is_postgres
        
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise e
    finally:
        if conn:
            if is_postgres and pg_pool:
                pg_pool.putconn(conn)
            else:
                # Return SQLite connection to pool
                with sqlite_lock:
                    if len(sqlite_connections) < SQLITE_POOL_SIZE:
                        sqlite_connections.append(conn)
                    else:
                        conn.close()

def generate_cache_key(operation: str, **kwargs) -> str:
    """Generate cache key for operations"""
    key_parts = [operation]
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def init_db():
    """Initialize database with enhanced schema"""
    try:
        # Initialize connection pools
        if USING_POSTGRES:
            init_postgres_pool()
        else:
            init_sqlite_pool()
        
        with get_connection() as (conn, is_postgres):
            cursor = conn.cursor()
            
            if is_postgres:
                # PostgreSQL enhanced schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id SERIAL PRIMARY KEY,
                        question TEXT UNIQUE NOT NULL,
                        answer TEXT NOT NULL,
                        weight REAL DEFAULT 1.0,
                        source TEXT DEFAULT 'system',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT DEFAULT 'system',
                        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        modified_by TEXT DEFAULT 'system',
                        metadata JSONB DEFAULT '{}',
                        tags TEXT[] DEFAULT '{}',
                        access_count INTEGER DEFAULT 0,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_question ON knowledge USING gin(to_tsvector('english', question))",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_answer ON knowledge USING gin(to_tsvector('english', answer))",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge (source)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_created_at ON knowledge (created_at)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_weight ON knowledge (weight)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge USING gin(tags)"
                ]
                
                for index_sql in indexes:
                    try:
                        cursor.execute(index_sql)
                    except Exception as e:
                        logger.warning(f"Index creation warning: {e}")
                
                # Create update trigger
                cursor.execute('''
                    CREATE OR REPLACE FUNCTION update_modified_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.modified_at = CURRENT_TIMESTAMP;
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';
                ''')
                
                cursor.execute('''
                    DROP TRIGGER IF EXISTS update_knowledge_modtime ON knowledge;
                    CREATE TRIGGER update_knowledge_modtime
                    BEFORE UPDATE ON knowledge
                    FOR EACH ROW
                    EXECUTE FUNCTION update_modified_column();
                ''')
                
            else:
                # SQLite enhanced schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT UNIQUE NOT NULL,
                        answer TEXT NOT NULL,
                        weight REAL DEFAULT 1.0,
                        source TEXT DEFAULT 'system',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT DEFAULT 'system',
                        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        modified_by TEXT DEFAULT 'system',
                        metadata TEXT DEFAULT '{}',
                        tags TEXT DEFAULT '',
                        access_count INTEGER DEFAULT 0,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_question ON knowledge (question)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_answer ON knowledge (answer)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge (source)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_created_at ON knowledge (created_at)",
                    "CREATE INDEX IF NOT EXISTS idx_knowledge_weight ON knowledge (weight)"
                ]
                
                for index_sql in indexes:
                    try:
                        cursor.execute(index_sql)
                    except Exception as e:
                        logger.warning(f"Index creation warning: {e}")
                
                # Create trigger for updated timestamp
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS update_knowledge_timestamp
                    AFTER UPDATE ON knowledge
                    FOR EACH ROW
                    BEGIN
                        UPDATE knowledge SET modified_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                    END;
                ''')
            
            conn.commit()
            logger.info("Database schema initialized successfully")
            return True
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

def save_data(question: str, answer: str, weight: float = 1.0, source: str = "system", 
              user: str = "system", metadata: Optional[Dict] = None, tags: Optional[List[str]] = None) -> bool:
    """Enhanced save data with caching and metadata"""
    try:
        if not question.strip() or not answer.strip():
            raise ValueError("Question and answer cannot be empty")
        
        # Invalidate related cache entries
        cache_keys_to_delete = [
            f"search:{hashlib.md5(question.encode()).hexdigest()}",
            "all_data",
            "stats"
        ]
        for key in cache_keys_to_delete:
            cache.delete(key)
        
        with get_connection() as (conn, is_postgres):
            cursor = conn.cursor()
            
            metadata = metadata or {}
            tags = tags or []
            
            if is_postgres:
                # PostgreSQL query with JSONB and array support
                cursor.execute('''
                    INSERT INTO knowledge (question, answer, weight, source, created_by, modified_by, metadata, tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (question) 
                    DO UPDATE SET 
                        answer = EXCLUDED.answer,
                        weight = EXCLUDED.weight,
                        source = EXCLUDED.source,
                        modified_by = EXCLUDED.modified_by,
                        metadata = EXCLUDED.metadata,
                        tags = EXCLUDED.tags
                ''', (question, answer, weight, source, user, user, json.dumps(metadata), tags))
            else:
                # SQLite query
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge 
                    (question, answer, weight, source, created_by, modified_by, metadata, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (question, answer, weight, source, user, user, json.dumps(metadata), ','.join(tags)))
            
            conn.commit()
            return True
            
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

def load_data(use_cache: bool = True) -> Dict[str, List[Dict]]:
    """Enhanced load data with caching"""
    cache_key = "all_data"
    
    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
    
    try:
        with get_connection() as (conn, is_postgres):
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT question, answer, weight, source, metadata, tags, access_count, last_accessed
                FROM knowledge
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            data = {}
            
            for row in rows:
                question = row[0]
                answer = row[1]
                weight = row[2]
                source = row[3]
                metadata_str = row[4] if row[4] else '{}'
                tags_str = row[5] if row[5] else ''
                access_count = row[6] if len(row) > 6 else 0
                last_accessed = row[7] if len(row) > 7 else None
                
                try:
                    metadata = json.loads(metadata_str)
                except:
                    metadata = {}
                
                if is_postgres:
                    tags = tags_str if isinstance(tags_str, list) else []
                else:
                    tags = tags_str.split(',') if tags_str else []
                
                if question not in data:
                    data[question] = []
                
                data[question].append({
                    "answer": answer,
                    "weight": weight,
                    "source": source,
                    "metadata": metadata,
                    "tags": tags,
                    "access_count": access_count,
                    "last_accessed": last_accessed
                })
            
            # Cache the result
            if use_cache:
                cache.set(cache_key, data, ttl=1800)  # 30 minutes
            
            return data
            
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {}

def search_knowledge(query: str, limit: int = 10, use_cache: bool = True) -> List[Tuple]:
    """Enhanced search with caching and better ranking"""
    if not query.strip():
        return []
    
    cache_key = generate_cache_key("search", query=query, limit=limit)
    
    if use_cache:
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results
    
    try:
        with get_connection() as (conn, is_postgres):
            cursor = conn.cursor()
            
            if is_postgres:
                # PostgreSQL full-text search with ranking
                search_query = '''
                    SELECT question, answer, weight, source,
                           ts_rank(
                               to_tsvector('english', question || ' ' || answer), 
                               plainto_tsquery('english', %s)
                           ) AS rank,
                           access_count
                    FROM knowledge
                    WHERE to_tsvector('english', question || ' ' || answer) @@ plainto_tsquery('english', %s)
                    ORDER BY rank DESC, weight DESC, access_count DESC
                    LIMIT %s
                '''
                cursor.execute(search_query, (query, query, limit))
            else:
                # SQLite basic search with ranking
                search_query = '''
                    SELECT question, answer, weight, source,
                           (CASE 
                               WHEN question LIKE ? THEN 3
                               WHEN answer LIKE ? THEN 2
                               ELSE 1
                           END) * weight * (access_count + 1) AS rank,
                           access_count
                    FROM knowledge
                    WHERE question LIKE ? OR answer LIKE ?
                    ORDER BY rank DESC, weight DESC, access_count DESC
                    LIMIT ?
                '''
                search_param = f"%{query}%"
                cursor.execute(search_query, (search_param, search_param, search_param, search_param, limit))
            
            results = cursor.fetchall()
            
            # Update access count for found results
            if results:
                question_list = [row[0] for row in results]
                update_access_count(question_list)
            
            # Cache results
            if use_cache:
                cache.set(cache_key, results, ttl=900)  # 15 minutes
            
            return results
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

def update_access_count(questions: List[str]):
    """Update access count for questions"""
    try:
        with get_connection() as (conn, is_postgres):
            cursor = conn.cursor()
            
            if is_postgres:
                cursor.execute('''
                    UPDATE knowledge 
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE question = ANY(%s)
                ''', (questions,))
            else:
                placeholders = ','.join(['?' for _ in questions])
                cursor.execute(f'''
                    UPDATE knowledge 
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE question IN ({placeholders})
                ''', questions)
            
            conn.commit()
            
    except Exception as e:
        logger.error(f"Error updating access count: {e}")

def get_statistics(use_cache: bool = True) -> Dict[str, Any]:
    """Get enhanced database statistics"""
    cache_key = "stats"
    
    if use_cache:
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return cached_stats
    
    try:
        with get_connection() as (conn, is_postgres):
            cursor = conn.cursor()
            
            # Basic statistics
            cursor.execute('SELECT COUNT(*) FROM knowledge')
            total_knowledge = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT source) FROM knowledge')
            unique_sources = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(access_count) FROM knowledge')
            total_accesses = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT AVG(weight) FROM knowledge')
            avg_weight = cursor.fetchone()[0] or 0
            
            # Recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM knowledge 
                WHERE created_at > datetime('now', '-1 day')
            ''')
            recent_additions = cursor.fetchone()[0]
            
            # Top sources
            cursor.execute('''
                SELECT source, COUNT(*) as count
                FROM knowledge 
                GROUP BY source 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            top_sources = cursor.fetchall()
            
            stats = {
                'total_knowledge': total_knowledge,
                'unique_sources': unique_sources,
                'total_accesses': total_accesses,
                'average_weight': round(avg_weight, 2),
                'recent_additions_24h': recent_additions,
                'top_sources': dict(top_sources),
                'cache_info': {
                    'redis_available': cache.redis_client is not None,
                    'using_postgres': is_postgres
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the stats
            if use_cache:
                cache.set(cache_key, stats, ttl=300)  # 5 minutes
            
            return stats
            
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {}

def cleanup_old_data(max_age_days: int = 90, min_access_count: int = 0) -> int:
    """Clean up old, unused data"""
    try:
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        with get_connection() as (conn, is_postgres):
            cursor = conn.cursor()
            
            if is_postgres:
                cursor.execute('''
                    DELETE FROM knowledge 
                    WHERE created_at < %s AND access_count <= %s
                    RETURNING id
                ''', (cutoff_date, min_access_count))
            else:
                cursor.execute('''
                    DELETE FROM knowledge 
                    WHERE created_at < ? AND access_count <= ?
                ''', (cutoff_date.isoformat(), min_access_count))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            # Clear cache after cleanup
            cache.clear()
            
            logger.info(f"Cleaned up {deleted_count} old knowledge entries")
            return deleted_count
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return -1

def backup_database(backup_path: Optional[str] = None) -> bool:
    """Create database backup"""
    try:
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_protype_{timestamp}.json"
        
        data = load_data(use_cache=False)
        stats = get_statistics(use_cache=False)
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'statistics': stats,
            'knowledge': data
        }
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Database backup created: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False

# Initialize database on import
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database on import: {e}")