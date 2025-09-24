import time
from typing import List, Dict
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from src.data_collection.database import Database
from config.config import SCRAPING_CONFIG
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from datetime import datetime, timedelta

# Download required NLTK data
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

class NewsAnalyzer:
    def __init__(self):
        self.db = Database()
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english', max_features=1000)
        self.lda = LatentDirichletAllocation(n_components=5, random_state=42, learning_method='online')
        self.topic_names = {
            0: "Business & Economy",
            1: "Technology & Innovation",
            2: "Politics & Government",
            3: "Health & Science",
            4: "Entertainment & Sports"
        }

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text using VADER with enhanced metrics"""
        sentiment_scores = self.sia.polarity_scores(text)
        return {
            'score': sentiment_scores['compound'],
            'label': self._get_sentiment_label(sentiment_scores['compound']),
            'pos': sentiment_scores['pos'],
            'neg': sentiment_scores['neg'],
            'neu': sentiment_scores['neu'],
            'intensity': abs(sentiment_scores['compound'])  # Add intensity metric
        }

    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label with more granular categories"""
        if score >= 0.05:
            return 'positive'
        elif score <= -0.05:
            return 'negative'
        else:
            return 'neutral'

    def extract_topics(self, text: str, num_topics: int = 3) -> List[Dict[str, float]]:
        """Extract main topics using LDA and enhanced frequency analysis"""
        try:
            # Tokenize and clean text
            tokens = word_tokenize(text.lower())
            words = [word for word in tokens if word.isalpha() and word not in self.stop_words]
            
            if len(words) < 10:  # Skip if not enough words
                return []
            
            # Enhanced frequency analysis with context
            word_freq = Counter(words)
            
            # Get most common words as topics
            topics = []
            for word, freq in word_freq.most_common(num_topics):
                # Calculate confidence based on frequency and position
                confidence = freq / len(words)
                
                # Add context words
                context_words = []
                for i, token in enumerate(tokens):
                    if token == word:
                        # Get words before and after
                        start = max(0, i - 2)
                        end = min(len(tokens), i + 3)
                        context = tokens[start:end]
                        context_words.extend([w for w in context if w.isalpha() and w not in self.stop_words])
                
                # Get most common context words
                context_freq = Counter(context_words)
                context = ' '.join([w for w, _ in context_freq.most_common(2)])
                
                topics.append({
                    'topic': f"{word} {context}".strip(),
                    'confidence': confidence
                })
            
            return topics
            
        except Exception as e:
            print(f"Error in topic extraction: {e}")
            return []

    def generate_word_cloud(self, text: str, category: str):
        """Generate word cloud for text with enhanced visualization"""
        try:
            wordcloud = WordCloud(
                width=1200,
                height=600,
                background_color='white',
                stopwords=self.stop_words,
                max_words=200,
                colormap='viridis',
                contour_width=1,
                contour_color='steelblue'
            ).generate(text)
            
            plt.figure(figsize=(15, 8))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(f'Word Cloud for {category} Articles', fontsize=16, pad=20)
            plt.savefig(f'wordcloud_{category}.png', dpi=300, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error generating word cloud: {e}")

    def plot_sentiment_distribution(self, sentiments: List[float], category: str):
        """Plot sentiment distribution for a category"""
        try:
            plt.figure(figsize=(10, 6))
            sns.histplot(sentiments, bins=20, kde=True)
            plt.title(f'Sentiment Distribution for {category} Articles', fontsize=14)
            plt.xlabel('Sentiment Score', fontsize=12)
            plt.ylabel('Count', fontsize=12)
            plt.savefig(f'sentiment_{category}.png', dpi=300, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error plotting sentiment distribution: {e}")

    def analyze_articles(self):
        """Analyze all unprocessed articles with enhanced metrics"""
        print("Starting article analysis...")
        
        # Get unprocessed articles
        articles = self.db.get_articles_for_analysis()
        print(f"Found {len(articles)} articles to analyze")
        
        # Group articles by category for analysis
        category_texts = {}
        category_sentiments = {}
        
        for article in articles:
            try:
                # Analyze sentiment
                sentiment = self.analyze_sentiment(article['content'])
                self.db.insert_sentiment_analysis(
                    article['id'],
                    sentiment['score'],
                    sentiment['label']
                )
                
                # Extract topics
                topics = self.extract_topics(article['content'])
                for topic in topics:
                    self.db.insert_topic_modeling(
                        article['id'],
                        topic['topic'],
                        topic['confidence']
                    )
                
                # Collect text and sentiment for category analysis
                category = article.get('category', 'uncategorized')
                if category not in category_texts:
                    category_texts[category] = []
                    category_sentiments[category] = []
                category_texts[category].append(article['content'])
                category_sentiments[category].append(sentiment['score'])
                
                print(f"Analyzed article: {article['title']}")
                print(f"Category: {category}")
                print(f"Sentiment: {sentiment['label']} ({sentiment['score']:.2f})")
                print(f"Topics: {[t['topic'] for t in topics]}")
                print("-" * 80)
                
            except Exception as e:
                print(f"Error analyzing article {article.get('title', '')}: {e}")
                continue
        
        # Generate visualizations and analyze categories
        for category, texts in category_texts.items():
            # Generate word cloud
            combined_text = ' '.join(texts)
            self.generate_word_cloud(combined_text, category)
            
            # Plot sentiment distribution
            sentiments = category_sentiments[category]
            self.plot_sentiment_distribution(sentiments, category)
            
            # Calculate category statistics
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            sentiment_std = np.std(sentiments) if sentiments else 0
            
            print(f"\nCategory Analysis - {category}:")
            print(f"Average Sentiment: {avg_sentiment:.2f} ± {sentiment_std:.2f}")
            print(f"Article Count: {len(texts)}")
            print(f"Sentiment Range: {min(sentiments):.2f} to {max(sentiments):.2f}")

    def get_analysis_summary(self, days: int = 7) -> Dict:
        """Get summary of analysis results with enhanced metrics"""
        try:
            results = self.db.get_analysis_results(days)
            summary = {
                'total_articles': sum(r['article_count'] for r in results),
                'categories': {},
                'sentiment_distribution': self.db.get_sentiment_counts()
            }
            
            for result in results:
                category = result['category']
                summary['categories'][category] = {
                    'article_count': result['article_count'],
                    'avg_sentiment': result['avg_sentiment'],
                    'topic_count': result['topic_count'],
                    'sentiment_distribution': {
                        'positive': result['positive_count'],
                        'negative': result['negative_count'],
                        'neutral': result['neutral_count']
                    }
                }
            
            return summary
        except Exception as e:
            print(f"Error getting analysis summary: {e}")
            return {
                'total_articles': 0,
                'categories': {},
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }

    def print_analysis_summary(self, summary: Dict):
        """Print formatted analysis summary with enhanced metrics"""
        print("\n=== Analysis Summary ===")
        print(f"Total Articles Analyzed: {summary['total_articles']}")
        
        if summary['total_articles'] == 0:
            print("No articles analyzed yet.")
            return
            
        print("\nArticles by Category:")
        for category, data in summary['categories'].items():
            print(f"\n{category}:")
            print(f"  Count: {data['article_count']}")
            print(f"  Average Sentiment: {data['avg_sentiment']:.2f}")
            print(f"  Topics Found: {data['topic_count']}")
            print("  Sentiment Distribution:")
            total = sum(data['sentiment_distribution'].values())
            if total > 0:
                for sentiment, count in data['sentiment_distribution'].items():
                    percentage = (count / total) * 100
                    print(f"    {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        
        print("\nOverall Sentiment Distribution:")
        total = sum(summary['sentiment_distribution'].values())
        if total > 0:
            for sentiment, count in summary['sentiment_distribution'].items():
                percentage = (count / total) * 100
                print(f"{sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Print sentiment trends
        print("\nSentiment Trends:")
        for category, data in summary['categories'].items():
            if data['article_count'] > 0:
                sentiment = data['avg_sentiment']
                trend = "↑ Positive" if sentiment > 0.1 else "↓ Negative" if sentiment < -0.1 else "→ Neutral"
                print(f"{category}: {trend} ({sentiment:.2f})")

def main():
    analyzer = NewsAnalyzer()
    while True:
        try:
            # First analyze any new articles
            analyzer.analyze_articles()
            
            # Then get and print the summary
            summary = analyzer.get_analysis_summary()
            analyzer.print_analysis_summary(summary)
            
            print("\nWaiting for next analysis cycle...")
            time.sleep(3600)  # Wait 1 hour between analysis cycles
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying on error

if __name__ == "__main__":
    main() 