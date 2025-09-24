import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Set
from datetime import datetime
from config.config import DATABASE_CONFIG

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'news_analyzer'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'malhar1234')
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        self._create_tables()
        self._update_schema()

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                published_at TIMESTAMP,
                source TEXT,
                content TEXT,
                category TEXT DEFAULT 'uncategorized' NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_length INTEGER,
                content_quality INTEGER DEFAULT 0
            );
        """)
        self.conn.commit()

    def _update_schema(self):
        """Update database schema to add category column if it doesn't exist"""
        try:
            # First ensure the category column exists
            self.cur.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'articles' 
                        AND column_name = 'category'
                    ) THEN
                        ALTER TABLE articles ADD COLUMN category TEXT DEFAULT 'uncategorized' NOT NULL;
                    END IF;
                END $$;
            """)
            
            # Add content_length column if it doesn't exist
            self.cur.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'articles' 
                        AND column_name = 'content_length'
                    ) THEN
                        ALTER TABLE articles ADD COLUMN content_length INTEGER;
                    END IF;
                END $$;
            """)
            
            # Add content_quality column if it doesn't exist
            self.cur.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'articles' 
                        AND column_name = 'content_quality'
                    ) THEN
                        ALTER TABLE articles ADD COLUMN content_quality INTEGER DEFAULT 0;
                    END IF;
                END $$;
            """)
            
            self.conn.commit()
        except Exception as e:
            print(f"Error updating schema: {e}")
            self.conn.rollback()

    def insert_article(self, article: Dict):
        """Insert a single article into the database"""
        try:
            # Ensure category is not None
            category = article.get('category', 'uncategorized')
            if category is None:
                category = 'uncategorized'
            
            # Get and validate content
            content = article.get('content', '')
            content_length = len(content) if content else 0
            
            # Determine content quality
            content_quality = 0  # Default to poor
            if content_length > 500:
                content_quality = 2  # Excellent
            elif content_length > 200:
                content_quality = 1  # Good
                
            self.cur.execute("""
                INSERT INTO articles (
                    title, url, published_at, source, 
                    content, category, content_length,
                    content_quality
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET
                    content = EXCLUDED.content,
                    content_length = EXCLUDED.content_length,
                    content_quality = EXCLUDED.content_quality,
                    category = EXCLUDED.category
            """, (
                article['title'],
                article['url'],
                article['published_at'],
                article['source'],
                content,
                category,
                content_length,
                content_quality
            ))
            self.conn.commit()
            print(f"Successfully inserted article: {article['title']}")
        except Exception as e:
            print(f"Error inserting article {article.get('url', 'Unknown URL')}: {e}")
            self.conn.rollback()

    def get_all_article_urls(self) -> Set[str]:
        """Get all existing article URLs from the database"""
        try:
            self.cur.execute("SELECT url FROM articles")
            return {row['url'] for row in self.cur.fetchall()}
        except Exception as e:
            print(f"Error fetching article URLs: {e}")
            return set()

    def get_articles_for_analysis(self, limit: int = 100) -> List[Dict]:
        """Get articles that haven't been analyzed yet"""
        self.cur.execute("""
            SELECT a.* FROM articles a
            LEFT JOIN sentiment_analysis sa ON a.id = sa.article_id
            WHERE sa.id IS NULL
            ORDER BY a.published_at DESC
            LIMIT %s
        """, (limit,))
        return self.cur.fetchall()

    def insert_sentiment_analysis(self, article_id: int, score: float, label: str):
        """Store sentiment analysis results"""
        self.cur.execute("""
            INSERT INTO sentiment_analysis (article_id, sentiment_score, sentiment_label)
            VALUES (%s, %s, %s)
        """, (article_id, score, label))
        self.conn.commit()

    def insert_topic_modeling(self, article_id: int, topic: str, confidence: float):
        """Store topic modeling results"""
        self.cur.execute("""
            INSERT INTO topic_modeling (article_id, topic, confidence)
            VALUES (%s, %s, %s)
        """, (article_id, topic, confidence))
        self.conn.commit()

    def get_analysis_results(self, days: int = 7) -> List[Dict]:
        """Get analysis results for the last N days with sentiment counts"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                
                # Get articles analyzed in the last N days
                cursor.execute("""
                    SELECT 
                        COALESCE(a.category, 'uncategorized') as category,
                        COUNT(DISTINCT a.id) as article_count,
                        AVG(sa.sentiment_score) as avg_sentiment,
                        COUNT(DISTINCT tm.id) as topic_count,
                        SUM(CASE WHEN sa.sentiment_label = 'positive' THEN 1 ELSE 0 END) as positive_count,
                        SUM(CASE WHEN sa.sentiment_label = 'negative' THEN 1 ELSE 0 END) as negative_count,
                        SUM(CASE WHEN sa.sentiment_label = 'neutral' THEN 1 ELSE 0 END) as neutral_count
                    FROM articles a
                    LEFT JOIN sentiment_analysis sa ON a.id = sa.article_id
                    LEFT JOIN topic_modeling tm ON a.id = tm.article_id
                    WHERE a.created_at >= NOW() - INTERVAL '%s days'
                    GROUP BY a.category
                    ORDER BY article_count DESC
                """, (days,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'category': row[0],
                        'article_count': row[1],
                        'avg_sentiment': row[2] if row[2] is not None else 0.0,
                        'topic_count': row[3],
                        'positive_count': row[4] or 0,
                        'negative_count': row[5] or 0,
                        'neutral_count': row[6] or 0
                    })
                
                return results
        except Exception as e:
            print(f"Error getting analysis results: {e}")
            return []

    def get_sentiment_counts(self, category: str = None) -> Dict[str, int]:
        """Get sentiment counts for all articles or a specific category"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                
                query = """
                    SELECT 
                        sa.sentiment_label,
                        COUNT(*) as count
                    FROM sentiment_analysis sa
                    JOIN articles a ON sa.article_id = a.id
                """
                
                params = []
                if category:
                    query += " WHERE a.category = %s"
                    params.append(category)
                
                query += " GROUP BY sa.sentiment_label"
                
                cursor.execute(query, params)
                
                counts = {'positive': 0, 'negative': 0, 'neutral': 0}
                for row in cursor.fetchall():
                    counts[row[0]] = row[1]
                
                return counts
        except Exception as e:
            print(f"Error getting sentiment counts: {e}")
            return {'positive': 0, 'negative': 0, 'neutral': 0}

    def update_article_categories(self, articles: List[Dict]):
        """Update categories for existing articles"""
        for article in articles:
            try:
                url = article['url']
                category = article.get('category', 'uncategorized')
                if category is None:
                    category = 'uncategorized'
                    
                self.cur.execute("""
                    UPDATE articles 
                    SET category = %s 
                    WHERE url = %s
                """, (category, url))
            except Exception as e:
                print(f"Error updating category for article {url}: {e}")
                continue
        self.conn.commit()

    def get_uncategorized_articles(self) -> List[Dict]:
        """Get all uncategorized articles"""
        try:
            self.cur.execute("""
                SELECT id, title, content, category
                FROM articles
                WHERE category IS NULL OR category = 'uncategorized' OR category = 'general'
            """)
            articles = []
            for row in self.cur.fetchall():
                articles.append({
                    'id': row['id'],
                    'title': row['title'],
                    'content': row['content'],
                    'category': row['category']
                })
            return articles
        except Exception as e:
            print(f"Error getting uncategorized articles: {e}")
            return []

    def update_article_category(self, article_id: int, category: str):
        """Update article category"""
        try:
            self.cur.execute("""
                UPDATE articles
                SET category = %s
                WHERE id = %s
            """, (category, article_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error updating article category: {e}")
            self.conn.rollback()

    def get_articles_by_startup(self, startup_name: str) -> List[Dict]:
        """Get all articles mentioning a specific startup"""
        try:
            self.cur.execute("""
                SELECT a.*, sa.sentiment_label, sa.sentiment_score
                FROM articles a
                LEFT JOIN sentiment_analysis sa ON a.id = sa.article_id
                WHERE LOWER(a.content) LIKE LOWER(%s)
                OR LOWER(a.title) LIKE LOWER(%s)
                ORDER BY a.published_at DESC
            """, (f'%{startup_name}%', f'%{startup_name}%'))
            
            articles = []
            for row in self.cur.fetchall():
                article = {
                    'id': row['id'],
                    'title': row['title'],
                    'content': row['content'],
                    'url': row['url'],
                    'published_at': row['published_at'],
                    'category': row['category'],
                    'sentiment_label': row['sentiment_label'],
                    'sentiment_score': row['sentiment_score']
                }
                articles.append(article)
            return articles
            
        except Exception as e:
            print(f"Error getting articles by startup: {e}")
            return []

    def close(self):
        """Close database connection"""
        self.cur.close()
        self.conn.close() 