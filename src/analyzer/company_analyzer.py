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

class CompanyAnalyzer:
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

    def get_all_companies(self) -> List[str]:
        """Get list of all companies mentioned in articles"""
        try:
            # First get all text content
            self.db.cur.execute("""
                SELECT title, content FROM articles
            """)
            
            companies = set()
            print("\nScanning articles for company names...")
            
            # Comprehensive list of known companies
            known_companies = {
                # Tech Companies
                'Apple', 'Google', 'Microsoft', 'Amazon', 'Meta', 'Tesla', 'Netflix',
                'Uber', 'Airbnb', 'Twitter', 'IBM', 'Intel', 'Nvidia', 'Oracle', 'Samsung',
                'SpaceX', 'OpenAI', 'Stripe', 'Palantir', 'Coinbase', 'Robinhood', 'Zoom',
                'Slack', 'Dropbox', 'Salesforce', 'Adobe', 'Cisco', 'Qualcomm', 'AMD', 'PayPal',
                'TikTok', 'ByteDance', 'Tencent', 'Alibaba', 'Baidu', 'Huawei', 'Xiaomi',
                'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Sony', 'Panasonic', 'LG',
                'Spotify', 'Pinterest', 'Snapchat', 'Tumblr', 'Reddit', 'LinkedIn',
                
                # Financial Companies
                'JPMorgan', 'Goldman Sachs', 'Morgan Stanley', 'Bank of America', 'Wells Fargo',
                'Citigroup', 'BlackRock', 'Vanguard', 'Fidelity', 'Charles Schwab',
                'American Express', 'Visa', 'Mastercard', 'Square', 'Stripe',
                
                # Automotive Companies
                'Ford', 'General Motors', 'Toyota', 'Honda', 'BMW', 'Mercedes-Benz',
                'Volkswagen', 'Audi', 'Porsche', 'Ferrari', 'Lamborghini', 'Hyundai',
                'Kia', 'Nissan', 'Mazda', 'Subaru', 'Volvo', 'Jaguar', 'Land Rover',
                
                # Retail Companies
                'Walmart', 'Target', 'Costco', 'Home Depot', 'Lowe\'s', 'Best Buy',
                'Macy\'s', 'Nordstrom', 'Kohl\'s', 'IKEA', 'Starbucks', 'McDonald\'s',
                'Coca-Cola', 'PepsiCo', 'Nike', 'Adidas', 'Under Armour', 'Zara',
                'H&M', 'Uniqlo', 'Gap', 'Lululemon',
                
                # Media & Entertainment
                'Disney', 'Warner Bros', 'Universal', 'Sony Pictures', 'Paramount',
                'Netflix', 'Hulu', 'Disney+', 'HBO', 'Showtime', 'ESPN', 'CNN',
                'Fox', 'NBC', 'CBS', 'ABC', 'BBC', 'Reuters', 'Bloomberg',
                
                # Healthcare & Pharma
                'Pfizer', 'Johnson & Johnson', 'Merck', 'Novartis', 'Roche',
                'AstraZeneca', 'GlaxoSmithKline', 'Bayer', 'Sanofi', 'AbbVie',
                'Amgen', 'Bristol-Myers Squibb', 'Eli Lilly', 'Gilead',
                
                # Industrial & Manufacturing
                'Boeing', 'Lockheed Martin', 'General Electric', 'Siemens',
                'Honeywell', '3M', 'Caterpillar', 'Deere', 'United Technologies',
                'Raytheon', 'Northrop Grumman', 'BAE Systems',
                
                # Energy & Utilities
                'ExxonMobil', 'Chevron', 'Shell', 'BP', 'Total', 'ConocoPhillips',
                'Schlumberger', 'Halliburton', 'Baker Hughes', 'NextEra Energy',
                'Duke Energy', 'Southern Company', 'Dominion Energy',
                
                # Telecommunications
                'AT&T', 'Verizon', 'T-Mobile', 'Sprint', 'Comcast', 'Charter',
                'Vodafone', 'Deutsche Telekom', 'Orange', 'Telefonica',
                
                # Startups & Unicorns
                'Stripe', 'SpaceX', 'OpenAI', 'Palantir', 'Coinbase', 'Robinhood',
                'Zoom', 'Slack', 'Dropbox', 'Airbnb', 'Uber', 'Lyft', 'DoorDash',
                'Instacart', 'WeWork', 'Pinterest', 'Snapchat', 'TikTok', 'ByteDance'
            }
            
            # Words to exclude from company names
            exclude_words = {
                'university', 'college', 'school', 'hospital', 'medical',
                'center', 'institute', 'foundation', 'association',
                'council', 'committee', 'department', 'ministry',
                'government', 'federal', 'state', 'city', 'county',
                'district', 'region', 'province', 'territory',
                'national', 'international', 'global', 'world',
                'news', 'media', 'press', 'journal', 'times',
                'sports', 'entertainment', 'music', 'movie',
                'television', 'radio', 'magazine', 'book',
                'research', 'study', 'survey', 'report',
                'project', 'program', 'initiative', 'campaign',
                'team', 'club', 'organization', 'society',
                'group', 'committee', 'board', 'council',
                'department', 'division', 'unit', 'section',
                'office', 'bureau', 'agency', 'authority',
                'commission', 'committee', 'task force', 'working group',
                'the', 'and', 'or', 'but', 'for', 'nor', 'so', 'yet',
                'a', 'an', 'in', 'on', 'at', 'to', 'from', 'by',
                'with', 'about', 'against', 'between', 'into', 'through',
                'during', 'before', 'after', 'above', 'below', 'from',
                'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
                'again', 'further', 'then', 'once', 'here', 'there',
                'when', 'where', 'why', 'how', 'all', 'any', 'both',
                'each', 'few', 'more', 'most', 'other', 'some', 'such',
                'that', 'these', 'this', 'those', 'which', 'who', 'whom',
                'whose', 'what', 'whatever', 'whichever', 'whoever',
                'whomever', 'which', 'whichever', 'whatever', 'whoever',
                'whomever', 'whose', 'that', 'these', 'this', 'those',
                'which', 'who', 'whom', 'whose', 'what', 'whatever',
                'whichever', 'whoever', 'whomever', 'which', 'whichever',
                'whatever', 'whoever', 'whomever', 'whose'
            }
            
            for row in self.db.cur.fetchall():
                text = f"{row['title']} {row['content']}"
                
                # Only look for known companies
                for company in known_companies:
                    # Create a regex pattern that matches the company name as a whole word
                    pattern = r'\b' + re.escape(company) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        companies.add(company)
            
            if not companies:
                print("No companies found in the database. Please make sure you have collected articles first.")
                return []
                
            print(f"\nFound {len(companies)} unique companies:")
            return sorted(list(companies))
            
        except Exception as e:
            print(f"Error getting companies: {e}")
            return []

    def analyze_company_impact(self, company_name: str) -> Dict:
        """Analyze financial impact of news on a specific company"""
        try:
            # Get articles about the company
            articles = self.db.get_articles_by_startup(company_name)
            if not articles:
                return {"error": f"No articles found for {company_name}"}
            
            # Initialize results
            results = {
                "company": company_name,
                "total_articles": len(articles),
                "parameters": {},
                "causes": []
            }
            
            # Analyze each parameter
            for param_name, param in self.parameters.items():
                param_results = {
                    "total_impact": 0.0,
                    "article_count": 0,
                    "evidence": [],
                    "causes": [],
                    "confidence": 0.0,
                    "context": []
                }
                
                for article in articles:
                    # Combine title and content for analysis
                    text = f"{article['title']} {article['content']}".lower()
                    
                    # Skip if article doesn't contain any parameter keywords
                    if not any(keyword in text for keyword in param.keywords):
                        continue
                    
                    # Split into sentences for better context
                    sentences = re.split(r'[.!?]+', text)
                    relevant_sentences = []
                    
                    for sentence in sentences:
                        # Check if sentence contains company name and parameter keywords
                        if (company_name.lower() in sentence.lower() and 
                            any(keyword in sentence for keyword in param.keywords)):
                            relevant_sentences.append(sentence.strip())
                    
                    if not relevant_sentences:
                        continue
                    
                    # Calculate impact score for each relevant sentence
                    for sentence in relevant_sentences:
                        impact_score = 0.0
                        evidence = []
                        
                        # Check for impact indicators
                        for word, score in param.impact_indicators.items():
                            if word in sentence:
                                impact_score += score
                                evidence.append(word)
                        
                        # Skip if no impact indicators found
                        if not evidence:
                            continue
                        
                        # Calculate confidence based on multiple factors
                        confidence = min(1.0, (
                            len(evidence) * 0.3 +  # Number of impact indicators
                            (1 if article['sentiment_score'] is not None else 0) * 0.3 +  # Sentiment score
                            (1 if len(relevant_sentences) > 1 else 0) * 0.2 +  # Multiple relevant sentences
                            (1 if any(num in sentence for num in ['$', '%', 'million', 'billion']) else 0) * 0.2  # Financial numbers
                        ))
                        
                        # Add to results
                        param_results["total_impact"] += impact_score
                        param_results["article_count"] += 1
                        param_results["evidence"].extend(evidence)
                        param_results["causes"].append(sentence)
                        param_results["confidence"] = max(param_results["confidence"], confidence)
                        param_results["context"].append({
                            "sentence": sentence,
                            "impact_score": impact_score,
                            "confidence": confidence,
                            "evidence": list(set(evidence))
                        })
                
                if param_results["article_count"] > 0:
                    param_results["average_impact"] = (
                        param_results["total_impact"] / param_results["article_count"]
                    )
                    results["parameters"][param.name] = param_results
            
            return results
            
        except Exception as e:
            print(f"Error analyzing company impact: {e}")
            return {"error": str(e)}

    def print_analysis(self, analysis: Dict):
        """Print formatted analysis results"""
        if "error" in analysis:
            print(f"\nError: {analysis['error']}")
            return
            
        print(f"\n=== Analysis for {analysis['company']} ===")
        print(f"Total Articles Analyzed: {analysis['total_articles']}")
        
        if not analysis["parameters"]:
            print("\nNo significant financial impacts found in the articles.")
            return
            
        for param_name, data in analysis["parameters"].items():
            print(f"\n{param_name}:")
            
            # Print impact direction and magnitude
            impact = data["average_impact"]
            if impact > 0.5:
                direction = "Positive"
            elif impact < -0.5:
                direction = "Negative"
            else:
                direction = "Neutral"
            
            print(f"  Overall Impact: {direction} ({impact:.2f})")
            print(f"  Confidence: {data['confidence']:.2f}")
            print(f"  Articles Affecting: {data['article_count']}")
            
            # Print top 3 most significant impacts
            if data["context"]:
                print("\n  Key Financial Impacts:")
                # Sort by impact score and confidence
                sorted_context = sorted(
                    data["context"],
                    key=lambda x: (abs(x["impact_score"]), x["confidence"]),
                    reverse=True
                )
                
                for i, ctx in enumerate(sorted_context[:3], 1):
                    print(f"  {i}. {ctx['sentence']}")
                    print(f"     Impact Score: {ctx['impact_score']:.2f}")
                    print(f"     Confidence: {ctx['confidence']:.2f}")
                    if ctx["evidence"]:
                        print(f"     Evidence: {', '.join(ctx['evidence'])}")
                    print()

def main():
    analyzer = CompanyAnalyzer()
    
    # List all companies
    companies = analyzer.get_all_companies()
    if not companies:
        return
        
    print("\nCompanies in database:")
    for i, company in enumerate(companies, 1):
        print(f"{i}. {company}")
    
    # Get company to analyze
    while True:
        company_name = input("\nEnter company name to analyze (or 'quit' to exit): ")
        if company_name.lower() == 'quit':
            break
            
        # Try to find the closest matching company name
        matches = [c for c in companies if company_name.lower() in c.lower()]
        if not matches:
            print("Company not found. Please try again.")
            continue
            
        if len(matches) > 1:
            print("\nMultiple matches found:")
            for i, match in enumerate(matches, 1):
                print(f"{i}. {match}")
            choice = input("Enter the number of the company you want to analyze: ")
            try:
                company_name = matches[int(choice)-1]
            except:
                print("Invalid choice. Please try again.")
                continue
        
        # Analyze company
        analysis = analyzer.analyze_company_impact(company_name)
        analyzer.print_analysis(analysis)

if __name__ == "__main__":
    main() 