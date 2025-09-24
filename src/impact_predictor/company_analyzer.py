import re
from typing import List, Dict, Set, Tuple
from src.data_collection.database import Database
from src.impact_predictor.predictor import ImpactPredictor
from src.impact_predictor.market_analyzer import MarketAnalyzer
from dataclasses import dataclass
from src.impact_predictor.models import Event, EventType
import spacy
from collections import Counter
from difflib import SequenceMatcher
import unicodedata
from textblob import TextBlob
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from bs4 import BeautifulSoup
import time

@dataclass
class FinancialMetric:
    name: str
    description: str
    metric_data: dict

@dataclass
class CompanySentiment:
    company: str
    sentiment_score: float
    confidence: float
    article_count: int
    recent_trend: str
    key_topics: List[str]

class CompanyAnalyzer:
    def __init__(self):
        self.db = Database()
        self.predictor = ImpactPredictor()
        self.market_analyzer = MarketAnalyzer()
        self.nlp = spacy.load('en_core_web_sm')
        
        # Enhanced company indicators with industry-specific terms
        self.company_indicators = {
            # Tech companies
            'technologies', 'tech', 'software', 'systems', 'solutions', 'digital', 'cloud', 'data', 'ai', 'ml',
            # Financial companies
            'financial', 'banking', 'capital', 'investments', 'securities', 'trading', 'funds', 'wealth',
            # Healthcare companies
            'healthcare', 'medical', 'pharmaceutical', 'biotech', 'life sciences', 'clinical', 'therapeutics',
            # Manufacturing companies
            'manufacturing', 'industries', 'production', 'engineering', 'materials', 'automotive', 'aerospace',
            # Retail companies
            'retail', 'commerce', 'stores', 'shopping', 'marketplace', 'consumer', 'brands',
            # Common suffixes
            'inc', 'corporation', 'corp', 'ltd', 'limited', 'llc', 'company', 'co', 'group', 'holdings'
        }
        
        # Enhanced non-company organizations
        self.non_company_orgs = {
            'university', 'college', 'school', 'institute', 'hospital', 'clinic',
            'government', 'ministry', 'department', 'agency', 'foundation', 'association',
            'research', 'laboratory', 'observatory', 'station', 'facility', 'center',
            'museum', 'library', 'gallery', 'theater', 'stadium', 'arena', 'park',
            'council', 'committee', 'board', 'commission', 'authority', 'bureau',
            'academy', 'society', 'club', 'union', 'federation', 'alliance', 'coalition'
        }
        
        # Common words that shouldn't appear in company names
        self.invalid_words = {
            'the', 'and', 'or', 'but', 'for', 'nor', 'yet', 'so', 'a', 'an',
            'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'like', 'through',
            'over', 'before', 'between', 'after', 'since', 'without', 'under',
            'within', 'along', 'following', 'across', 'behind', 'beyond', 'plus',
            'minus', 'times', 'divided', 'equals', 'percent', 'dollar', 'euro'
        }
        
        # Company name patterns with improved regex
        self.company_patterns = [
            # Standard company names with suffixes
            r'(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc\.?|Corp\.?|Ltd\.?|LLC|Co\.?|Group|Tech|Systems|Solutions))$',
            # International/Global companies
            r'(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:International|Global|Worldwide|National|Regional))$',
            # Technology companies
            r'(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Technologies|Solutions|Systems|Software|Services))$',
            # Financial companies
            r'(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Holdings|Ventures|Capital|Partners|Group|Fund|Trust))$',
            # Manufacturing companies
            r'(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Manufacturing|Industries|Production|Engineering))$',
            # Healthcare companies
            r'(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Health|Medical|Pharmaceutical|Biotech|Therapeutics))$',
            # Retail companies
            r'(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Retail|Commerce|Stores|Brands|Products))$'
        ]
        
        # Known company name variations
        self.company_variations = {
            'inc': ['incorporated', 'inc.', 'inc'],
            'corp': ['corporation', 'corp.', 'corp'],
            'ltd': ['limited', 'ltd.', 'ltd'],
            'llc': ['limited liability company', 'llc'],
            'co': ['company', 'co.', 'co'],
            'group': ['group', 'holdings', 'holdings group'],
            'tech': ['technologies', 'technology', 'tech'],
            'systems': ['systems', 'system solutions'],
            'solutions': ['solutions', 'solution providers']
        }
        
        # Define financial metrics with detailed descriptions and industry-specific indicators
        self.financial_metrics = [
            FinancialMetric(
                "Revenue",
                "Total income generated from business operations",
                {
                    "positive": [
                        "revenue growth", "sales increase", "higher sales", "revenue up", "increased revenue",
                        "record sales", "strong demand", "market expansion", "new customers", "product adoption"
                    ],
                    "negative": [
                        "revenue decline", "sales drop", "lower sales", "revenue down", "decreased revenue",
                        "weak demand", "market contraction", "customer loss", "product decline"
                    ],
                    "weight": 0.7,
                    "industry_factors": {
                        "tech": 1.2,
                        "retail": 1.1,
                        "healthcare": 0.9,
                        "manufacturing": 1.0
                    }
                }
            ),
            FinancialMetric(
                "Net Profit",
                "Total profit after all expenses",
                {
                    "positive": [
                        "profit growth", "earnings increase", "higher profit", "profit up", "increased earnings",
                        "margin improvement", "cost efficiency", "operational excellence", "profitability"
                    ],
                    "negative": [
                        "profit decline", "earnings drop", "lower profit", "profit down", "decreased earnings",
                        "margin pressure", "cost inflation", "operational challenges"
                    ],
                    "weight": 0.8,
                    "industry_factors": {
                        "tech": 1.1,
                        "retail": 0.9,
                        "healthcare": 1.2,
                        "manufacturing": 1.0
                    }
                }
            ),
            FinancialMetric(
                "Valuation",
                "Company's estimated market value",
                {
                    "positive": [
                        "valuation increase", "market cap growth", "higher valuation", "valuation up",
                        "investor confidence", "market leadership", "growth potential", "strategic position"
                    ],
                    "negative": [
                        "valuation decrease", "market cap drop", "lower valuation", "valuation down",
                        "investor concerns", "market challenges", "growth uncertainty"
                    ],
                    "weight": 0.6,
                    "industry_factors": {
                        "tech": 1.3,
                        "retail": 0.8,
                        "healthcare": 1.1,
                        "manufacturing": 0.9
                    }
                }
            ),
            FinancialMetric(
                "Churn Rate",
                "Rate at which customers leave",
                {
                    "positive": [
                        "churn decrease", "customer retention", "lower churn", "churn down",
                        "customer loyalty", "satisfaction improvement", "service quality"
                    ],
                    "negative": [
                        "churn increase", "customer loss", "higher churn", "churn up",
                        "customer dissatisfaction", "service issues", "competition"
                    ],
                    "weight": 0.75,
                    "industry_factors": {
                        "tech": 1.2,
                        "retail": 0.9,
                        "healthcare": 1.1,
                        "manufacturing": 0.8
                    }
                }
            ),
            FinancialMetric(
                "EBITDA",
                "Earnings before interest, taxes, depreciation, and amortization",
                {
                    "positive": [
                        "EBITDA growth", "earnings increase", "higher EBITDA", "EBITDA up",
                        "operational efficiency", "margin expansion", "cost control"
                    ],
                    "negative": [
                        "EBITDA decline", "earnings drop", "lower EBITDA", "EBITDA down",
                        "operational challenges", "margin pressure", "cost increases"
                    ],
                    "weight": 0.65,
                    "industry_factors": {
                        "tech": 1.1,
                        "retail": 0.9,
                        "healthcare": 1.2,
                        "manufacturing": 1.0
                    }
                }
            ),
            FinancialMetric(
                "Operating Expenses",
                "Costs of running the business",
                {
                    "positive": [
                        "cost reduction", "expense decrease", "lower costs", "expenses down",
                        "efficiency improvement", "optimization", "resource management"
                    ],
                    "negative": [
                        "cost increase", "expense growth", "higher costs", "expenses up",
                        "inflation impact", "resource constraints", "operational challenges"
                    ],
                    "weight": 0.7,
                    "industry_factors": {
                        "tech": 1.0,
                        "retail": 1.1,
                        "healthcare": 0.9,
                        "manufacturing": 1.2
                    }
                }
            )
        ]
        
        self.companies = self._extract_companies()

    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name by handling common variations."""
        name = name.strip()
        words = name.split()
        
        # Handle common variations
        for i, word in enumerate(words):
            word_lower = word.lower().rstrip('.')
            for standard, variations in self.company_variations.items():
                if word_lower in variations:
                    words[i] = standard.capitalize()
        
        return ' '.join(words)

    def _is_likely_company(self, text: str) -> bool:
        """Enhanced check if the text is likely to be a company name."""
        text = text.strip()
        text_lower = text.lower()
        
        # Basic validation
        if len(text.split()) < 2 or len(text.split()) > 5:
            return False
            
        # Check for common non-company terms
        if any(term in text_lower for term in self.non_company_orgs):
            return False
            
        # Check for invalid words
        if any(word in text_lower.split() for word in self.invalid_words):
            return False
            
        # Check for company indicators
        has_company_indicator = any(indicator in text_lower for indicator in self.company_indicators)
        
        # Check for company name patterns
        has_company_pattern = any(bool(re.search(pattern, text, re.IGNORECASE)) 
                                for pattern in self.company_patterns)
        
        # Check for proper capitalization
        words = text.split()
        has_proper_capitalization = all(word[0].isupper() for word in words)
        
        # Check for common company name characteristics
        has_valid_length = 2 <= len(text) <= 50
        has_no_special_chars = not any(c in text for c in '!@#$%^&*()_+{}[]|\\:;"\'<>,.?/~`')
        has_no_numbers = not any(c.isdigit() for c in text)
        
        # Check for common company name structure
        has_valid_structure = (
            has_proper_capitalization and
            has_valid_length and
            has_no_special_chars and
            has_no_numbers and
            (has_company_indicator or has_company_pattern)
        )
        
        return has_valid_structure

    def _extract_companies(self) -> list:
        """Extract and validate company names from articles."""
        try:
            self.db.cur.execute("SELECT title, content FROM articles")
            rows = self.db.cur.fetchall()
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []

        orgs = []
        for row in rows:
            text = f"{row['title']} {row['content']}"
            doc = self.nlp(text)
            
            # Get potential company names
            potential_companies = [ent.text.strip() for ent in doc.ents if ent.label_ == 'ORG']
            
            # Filter and validate companies
            companies = [company for company in potential_companies 
                       if self._is_likely_company(company)]
            
            # Normalize company names
            companies = [self._normalize_company_name(company) for company in companies]
            
            orgs.extend(companies)

        # Count and sort by frequency
        org_counts = Counter(orgs)
        
        # Filter out low-frequency mentions (likely false positives)
        min_mentions = 2
        companies = [company for company, count in org_counts.items() 
                   if count >= min_mentions]
        
        # Sort by frequency and name
        companies = sorted(companies, key=lambda x: (-org_counts[x], x.lower()))
        return companies

    def print_companies(self):
        """Print the list of companies with serial numbers."""
        print("Companies mentioned in articles:")
        for i, company in enumerate(self.companies, 1):
            print(f"{i}. {company}")

    def print_metrics(self):
        print("Financial metrics:")
        for i, metric in enumerate(self.financial_metrics, 1):
            print(f"{i}. {metric.name}")

    def _detect_industry(self, company_name: str, articles: list) -> str:
        """Detect the industry of a company based on its name and articles."""
        industry_keywords = {
            "tech": ["software", "technology", "digital", "cloud", "ai", "data", "platform"],
            "retail": ["retail", "store", "shop", "consumer", "brand", "product"],
            "healthcare": ["health", "medical", "pharma", "biotech", "clinical", "therapeutic"],
            "manufacturing": ["manufacturing", "production", "industrial", "factory", "plant"]
        }
        
        # Check company name
        company_lower = company_name.lower()
        for industry, keywords in industry_keywords.items():
            if any(keyword in company_lower for keyword in keywords):
                return industry
        
        # Check articles
        article_text = " ".join([f"{a.get('title', '')} {a.get('content', '')}" for a in articles]).lower()
        industry_scores = {industry: 0 for industry in industry_keywords.keys()}
        
        for industry, keywords in industry_keywords.items():
            for keyword in keywords:
                industry_scores[industry] += article_text.count(keyword)
        
        return max(industry_scores.items(), key=lambda x: x[1])[0]

    def _summarize_article(self, article: dict, max_length: int = 150) -> str:
        """Generate a concise summary of an article."""
        title = article.get('title', '')
        content = article.get('content', '')
        
        # Combine title and content
        text = f"{title} {content}"
        
        # Use TextBlob for basic summarization
        blob = TextBlob(text)
        
        # Get the most important sentences (based on length and position)
        sentences = blob.sentences
        if not sentences:
            return "No content available."
            
        # Score sentences based on position and length
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            # Position score (first sentences are more important)
            position_score = 1.0 / (i + 1)
            # Length score (prefer medium-length sentences)
            length_score = 1.0 / (1 + abs(len(str(sentence)) - 100))
            # Combined score
            score = position_score * length_score
            scored_sentences.append((score, str(sentence)))
        
        # Sort by score and take top sentences
        scored_sentences.sort(reverse=True)
        summary_sentences = [s[1] for s in scored_sentences[:2]]
        
        # Join sentences and truncate if needed
        summary = ' '.join(summary_sentences)
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'
            
        return summary

    def analyze_company(self, company_name: str):
        """Analyze a company and print insights for all metrics."""
        print(f"\n{'='*80}")
        print(f"📊 Analysis for {company_name}")
        print(f"{'='*80}\n")
        
        # Get articles mentioning the company
        articles = self.db.get_articles_by_startup(company_name)
        if not articles:
            print(f"❌ No articles found for {company_name}.")
            return

        # Sort articles by date (newest first)
        articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        # Print article summaries
        print("📰 Recent Articles:")
        print("-" * 50)
        for i, article in enumerate(articles[:5], 1):  # Show top 5 articles
            date = article.get('published_at', 'Unknown date')
            source = article.get('source', 'Unknown source')
            summary = self._summarize_article(article)
            print(f"\n{i}. Date: {date}")
            print(f"   Source: {source}")
            print(f"   Summary: {summary}")
        print("-" * 50)
        
        # Detect company industry
        industry = self._detect_industry(company_name, articles)
        print(f"\nDetected Industry: {industry.upper()}")
        print("Analyzing all financial metrics...\n")
        
        # Calculate time-based weights
        now = datetime.now()
        time_weights = []
        for article in articles:
            pub_date = article.get('published_at')
            if pub_date:
                days_old = (now - pub_date).days
                # Exponential decay: newer articles have higher weights
                weight = np.exp(-days_old / 30)  # 30-day half-life
            else:
                weight = 0.5  # Default weight for articles without date
            time_weights.append(weight)
        
        # Normalize time weights
        if time_weights:
            time_weights = [w/sum(time_weights) for w in time_weights]
        
        # Analyze each metric
        for metric in self.financial_metrics:
            print(f"\n📈 {metric.name}")
            print(f"Description: {metric.description}")
            print("-" * 50)
            
            # Get metric-specific data
            metric_data = metric.metric_data
            industry_factor = metric_data["industry_factors"].get(industry, 1.0)
            
            # Analyze articles for the current metric
            impact_scores = []
            sentiments = []
            keyword_scores = []
            confidence_scores = []
            relevant_articles = []
            
            for i, article in enumerate(articles):
                text = f"{article.get('title', '')} {article.get('content', '')}"
                text_lower = text.lower()
                
                # Calculate keyword-based score with context
                positive_matches = sum(1 for kw in metric_data["positive"] if kw.lower() in text_lower)
                negative_matches = sum(1 for kw in metric_data["negative"] if kw.lower() in text_lower)
                total_matches = positive_matches + negative_matches
                
                # Calculate confidence based on keyword matches
                confidence = min(1.0, total_matches / 5)  # Cap at 1.0
                confidence_scores.append(confidence)
                
                # Calculate keyword score with confidence
                keyword_score = (positive_matches - negative_matches) / max(1, total_matches)
                keyword_scores.append(keyword_score * confidence)
                
                # Get impact prediction
                event = Event(
                    event_type=EventType.INDUSTRY_NEWS,
                    title=article.get('title', ''),
                    description=article.get('content', ''),
                    source=article.get('source', ''),
                    date=article.get('published_at', None),
                    location=article.get('category', ''),
                    severity=0.5,
                    confidence=confidence,
                    raw_text=text
                )
                
                result = self.predictor.predict_impact(event, metric)
                if hasattr(result, 'impact_score'):
                    impact_scores.append(result.impact_score * confidence)
                elif isinstance(result, dict) and 'impact_score' in result:
                    impact_scores.append(result['impact_score'] * confidence)
                
                # Calculate sentiment with subjectivity
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity
                
                # Adjust sentiment based on subjectivity
                adjusted_sentiment = sentiment * (1 - subjectivity)
                sentiments.append(adjusted_sentiment)
                
                # Store relevant articles (those with significant impact)
                if abs(keyword_score) > 0.3 or abs(adjusted_sentiment) > 0.3:
                    relevant_articles.append(article)
                    
            if not impact_scores:
                print("❌ No impact could be determined from the articles.")
                continue
                
            # Calculate weighted scores using time weights
            avg_impact = sum(s * w for s, w in zip(impact_scores, time_weights))
            avg_sentiment = sum(s * w for s, w in zip(sentiments, time_weights))
            avg_keyword = sum(s * w for s, w in zip(keyword_scores, time_weights))
            avg_confidence = sum(s * w for s, w in zip(confidence_scores, time_weights))
            
            # Apply industry factor
            avg_impact *= industry_factor
            
            # Calculate trend
            recent_impact = sum(s * w for s, w in zip(impact_scores[:3], time_weights[:3]))
            older_impact = sum(s * w for s, w in zip(impact_scores[3:], time_weights[3:]))
            trend_factor = recent_impact - older_impact if len(impact_scores) > 3 else 0
            
            # Combine scores with metric-specific weighting and confidence
            final_score = (
                avg_impact * 0.4 +  # Base impact
                avg_sentiment * 0.2 +  # General sentiment
                avg_keyword * metric_data["weight"]  # Metric-specific keywords
            ) * avg_confidence  # Apply confidence factor
            
            # Add trend influence
            final_score += trend_factor * 0.1
            
            # Normalize final score to [-1, 1] range
            final_score = max(min(final_score, 1.0), -1.0)
            
            # Determine result and trend
            if final_score > 0.2:
                result = "PROFIT"
                trend = "↑" if trend_factor > 0 else "→"
            elif final_score < -0.2:
                result = "LOSS"
                trend = "↓" if trend_factor < 0 else "→"
            else:
                result = "NEUTRAL"
                trend = "→"
                
            print(f"Result: {result} {trend}")
            print(f"Impact Score: {avg_impact:.2f}")
            print(f"Sentiment Score: {avg_sentiment:.2f}")
            print(f"Keyword Score: {avg_keyword:.2f}")
            print(f"Confidence Score: {avg_confidence:.2f}")
            print(f"Industry Factor: {industry_factor:.2f}")
            print(f"Trend Factor: {trend_factor:.2f}")
            print(f"Final Score: {final_score:.2f}")
            print(f"Articles Analyzed: {len(impact_scores)}")
            print(f"Time Period: {articles[-1].get('published_at', 'Unknown')} to {articles[0].get('published_at', 'Unknown')}")
            
            # Print relevant article summaries for this metric
            if relevant_articles:
                print("\n📰 Relevant Articles for this Metric:")
                for i, article in enumerate(relevant_articles[:3], 1):  # Show top 3 relevant articles
                    date = article.get('published_at', 'Unknown date')
                    summary = self._summarize_article(article)
                    print(f"\n{i}. Date: {date}")
                    print(f"   Summary: {summary}")
            
            print("-" * 50)
            
        print(f"\n{'='*80}")
        print("Analysis Complete!")
        print(f"{'='*80}\n")

def main():
    analyzer = CompanyAnalyzer()
    
    while True:
        # Print companies and get user selection
        analyzer.print_companies()
        user_input = input("\nEnter company serial number (or 0 to exit): ").strip()
        
        if user_input == '0':
            print("\nExiting analysis...")
            break
            
        # Try to interpret as serial number
        company_name = None
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(analyzer.companies):
                company_name = analyzer.companies[idx]
            else:
                print(f"❌ Invalid serial number. Please enter a number between 1 and {len(analyzer.companies)}.")
                continue
        else:
            # Try to match company name (case-insensitive)
            matches = [c for c in analyzer.companies if c.lower() == user_input.lower()]
            if matches:
                company_name = matches[0]
            else:
                print(f"❌ Company '{user_input}' not found in the list. Please enter a valid company name or serial number.")
                continue
                
        print(f"\nSelected company: {company_name}")
        analyzer.analyze_company(company_name)
        
        # Ask if user wants to continue
        print("\nWould you like to analyze another company?")
        print("1. Yes - Show company list again")
        print("0. No - Exit")
        choice = input("Enter your choice (0 or 1): ").strip()
        
        if choice == '0':
            print("\nExiting analysis...")
            break

if __name__ == "__main__":
    main() 