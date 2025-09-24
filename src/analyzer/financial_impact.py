import re
from typing import Dict, List, Set
from dataclasses import dataclass
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from src.data_collection.database import Database

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

@dataclass
class FinancialParameter:
    name: str
    keywords: Set[str]
    impact_indicators: Dict[str, float]  # word -> impact score (-1 to 1)
    related_metrics: List[str]  # related parameters that might be affected

class FinancialImpactAnalyzer:
    def __init__(self):
        self.db = Database()
        self.stop_words = set(stopwords.words('english'))
        
        # Define financial parameters and their indicators
        self.parameters = {
            'revenue': FinancialParameter(
                name="Total Revenue",
                keywords={'revenue', 'sales', 'income', 'earnings', 'turnover'},
                impact_indicators={
                    'increase': 1.0, 'growth': 0.8, 'rise': 0.7,
                    'decrease': -1.0, 'decline': -0.8, 'fall': -0.7,
                    'stable': 0.0, 'maintain': 0.0
                },
                related_metrics=['Revenue Growth Rate', 'Gross Profit Margin']
            ),
            'profit': FinancialParameter(
                name="Net Profit/Loss",
                keywords={'profit', 'loss', 'earnings', 'income', 'margin'},
                impact_indicators={
                    'profit': 1.0, 'gain': 0.8, 'surplus': 0.7,
                    'loss': -1.0, 'deficit': -0.8, 'shortfall': -0.7
                },
                related_metrics=['Net Profit Margin', 'EBITDA']
            ),
            'funding': FinancialParameter(
                name="Total Funding Raised",
                keywords={'funding', 'investment', 'raise', 'capital', 'series'},
                impact_indicators={
                    'raise': 1.0, 'invest': 0.8, 'fund': 0.7,
                    'withdraw': -1.0, 'pull': -0.8, 'exit': -0.7
                },
                related_metrics=['Valuation', 'Number of Funding Rounds']
            ),
            'valuation': FinancialParameter(
                name="Valuation",
                keywords={'valuation', 'worth', 'value', 'market cap', 'price'},
                impact_indicators={
                    'increase': 1.0, 'rise': 0.8, 'grow': 0.7,
                    'decrease': -1.0, 'fall': -0.8, 'drop': -0.7
                },
                related_metrics=['Stock Price Growth', 'Market Share']
            ),
            'market_share': FinancialParameter(
                name="Market Share",
                keywords={'market share', 'dominance', 'position', 'competition', 'leadership'},
                impact_indicators={
                    'gain': 1.0, 'increase': 0.8, 'lead': 0.7,
                    'lose': -1.0, 'decline': -0.8, 'fall': -0.7
                },
                related_metrics=['Revenue Growth Rate', 'Customer Acquisition Cost']
            ),
            'customer_metrics': FinancialParameter(
                name="Customer Metrics",
                keywords={'customer', 'user', 'subscriber', 'client', 'acquisition'},
                impact_indicators={
                    'grow': 1.0, 'increase': 0.8, 'expand': 0.7,
                    'lose': -1.0, 'decline': -0.8, 'churn': -0.7
                },
                related_metrics=['LTV/CAC Ratio', 'Churn Rate', 'ARPU']
            ),
            'operational_metrics': FinancialParameter(
                name="Operational Metrics",
                keywords={'operation', 'efficiency', 'cost', 'expense', 'margin'},
                impact_indicators={
                    'improve': 1.0, 'optimize': 0.8, 'reduce': 0.7,
                    'worsen': -1.0, 'increase': -0.8, 'rise': -0.7
                },
                related_metrics=['Operating Profit Margin', 'Burn Rate']
            ),
            'risk_metrics': FinancialParameter(
                name="Risk Metrics",
                keywords={'risk', 'uncertainty', 'volatility', 'stability', 'security'},
                impact_indicators={
                    'reduce': 1.0, 'mitigate': 0.8, 'manage': 0.7,
                    'increase': -1.0, 'worsen': -0.8, 'threat': -0.7
                },
                related_metrics=['Investor Concentration Risk', 'Regulatory & Compliance Risks']
            )
        }

    def analyze_article(self, content: str, title: str) -> Dict[str, Dict]:
        """Analyze article content for financial impact"""
        # Combine title and content for analysis
        text = f"{title} {content}".lower()
        tokens = word_tokenize(text)
        
        # Initialize results
        results = defaultdict(lambda: {
            'impact_score': 0.0,
            'confidence': 0.0,
            'evidence': [],
            'related_metrics': set()
        })
        
        # Analyze each parameter
        for param_name, param in self.parameters.items():
            # Check for parameter keywords
            keyword_matches = sum(1 for word in tokens if word in param.keywords)
            
            if keyword_matches > 0:
                # Calculate impact score
                impact_score = 0.0
                evidence = []
                
                for word, score in param.impact_indicators.items():
                    if word in text:
                        impact_score += score
                        evidence.append(word)
                
                # Calculate confidence based on keyword matches and impact indicators
                confidence = min(1.0, (keyword_matches + len(evidence)) / 5)
                
                # Store results
                results[param_name].update({
                    'impact_score': impact_score,
                    'confidence': confidence,
                    'evidence': evidence,
                    'related_metrics': set(param.related_metrics)
                })
        
        return dict(results)

    def analyze_startup_news(self, startup_name: str):
        """Analyze all news articles about a specific startup"""
        try:
            # Get articles about the startup
            articles = self.db.get_articles_by_startup(startup_name)
            print(f"\nAnalyzing {len(articles)} articles about {startup_name}")
            
            # Aggregate results
            aggregated_impact = defaultdict(lambda: {
                'total_impact': 0.0,
                'article_count': 0,
                'average_impact': 0.0,
                'evidence': set(),
                'related_metrics': set()
            })
            
            # Analyze each article
            for article in articles:
                results = self.analyze_article(article['content'], article['title'])
                
                for param_name, result in results.items():
                    if result['confidence'] > 0.3:  # Only consider confident results
                        agg = aggregated_impact[param_name]
                        agg['total_impact'] += result['impact_score']
                        agg['article_count'] += 1
                        agg['evidence'].update(result['evidence'])
                        agg['related_metrics'].update(result['related_metrics'])
            
            # Calculate averages and prepare output
            output = {}
            for param_name, agg in aggregated_impact.items():
                if agg['article_count'] > 0:
                    param = self.parameters[param_name]
                    avg_impact = agg['total_impact'] / agg['article_count']
                    
                    output[param.name] = {
                        'Average Impact': avg_impact,
                        'Impact Direction': 'Positive' if avg_impact > 0 else 'Negative',
                        'Article Count': agg['article_count'],
                        'Key Evidence': list(agg['evidence'])[:5],
                        'Related Metrics': list(agg['related_metrics'])
                    }
            
            return output
            
        except Exception as e:
            print(f"Error analyzing startup news: {e}")
            return {}

    def print_analysis(self, analysis: Dict):
        """Print formatted analysis results"""
        print("\n=== Financial Impact Analysis ===")
        
        for param_name, data in analysis.items():
            print(f"\n{param_name}:")
            print(f"  Impact Direction: {data['Impact Direction']}")
            print(f"  Average Impact: {data['Average Impact']:.2f}")
            print(f"  Articles Analyzed: {data['Article Count']}")
            print("  Key Evidence:")
            for evidence in data['Key Evidence']:
                print(f"    - {evidence}")
            print("  Related Metrics:")
            for metric in data['Related Metrics']:
                print(f"    - {metric}")

def main():
    analyzer = FinancialImpactAnalyzer()
    startup_name = input("Enter startup name to analyze: ")
    analysis = analyzer.analyze_startup_news(startup_name)
    analyzer.print_analysis(analysis)

if __name__ == "__main__":
    main() 