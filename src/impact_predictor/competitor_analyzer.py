from typing import List, Dict, Set
import pandas as pd
import numpy as np
from dataclasses import dataclass
from .market_analyzer import MarketAnalyzer
from .company_analyzer import CompanyAnalyzer

@dataclass
class CompetitorMetrics:
    company: str
    market_share: float
    growth_rate: float
    sentiment_score: float
    financial_health: float
    competitive_advantage: float

class CompetitorAnalyzer:
    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.company_analyzer = CompanyAnalyzer()
        
        # Define industry sectors and their companies
        self.sector_mapping = {
            "Technology": {
                "microsoft", "apple", "google", "amazon", "meta", "nvidia", "intel", "amd",
                "ibm", "oracle", "salesforce", "adobe", "cisco", "qualcomm"
            },
            "Entertainment": {
                "netflix", "disney", "spotify", "warner bros", "sony", "paramount"
            },
            "E-commerce": {
                "amazon", "shopify", "ebay", "etsy", "walmart", "target"
            },
            "Social Media": {
                "meta", "twitter", "snap", "pinterest", "linkedin", "tiktok"
            },
            "Cloud Computing": {
                "amazon", "microsoft", "google", "oracle", "ibm", "salesforce"
            },
            "Semiconductor": {
                "intel", "amd", "nvidia", "qualcomm", "broadcom", "micron"
            }
        }

    def get_competitors(self, company: str) -> Set[str]:
        """Get direct competitors for a given company."""
        company = company.lower()
        for sector, companies in self.sector_mapping.items():
            if company in companies:
                return companies - {company}
        return set()

    def analyze_competitor_metrics(self, company: str) -> List[CompetitorMetrics]:
        """Analyze metrics for a company and its competitors."""
        competitors = self.get_competitors(company)
        all_companies = [company] + list(competitors)
        metrics_list = []

        for comp in all_companies:
            # Get company insights
            insights = self.company_analyzer.get_company_insights(comp)
            
            # Calculate market share (placeholder - would need real market data)
            market_share = np.random.uniform(0.1, 0.4) if comp == company else np.random.uniform(0.05, 0.2)
            
            # Calculate growth rate from stock data
            ticker = self.company_analyzer._get_company_ticker(comp)
            growth_rate = 0.0
            if ticker:
                stock_data = self.market_analyzer.get_stock_data(ticker)
                if not stock_data.empty:
                    growth_rate = (stock_data['Close'][-1] / stock_data['Close'][0] - 1) * 100

            # Get sentiment score
            sentiment_score = insights.get('sentiment_analysis', {}).get('overall_sentiment', 0)

            # Calculate financial health (placeholder - would need real financial data)
            financial_health = np.random.uniform(0.5, 1.0)

            # Calculate competitive advantage
            competitive_advantage = (market_share * 0.4 + 
                                  (growth_rate / 100) * 0.3 + 
                                  (sentiment_score + 1) * 0.3)

            metrics = CompetitorMetrics(
                company=comp,
                market_share=market_share,
                growth_rate=growth_rate,
                sentiment_score=sentiment_score,
                financial_health=financial_health,
                competitive_advantage=competitive_advantage
            )
            metrics_list.append(metrics)

        return metrics_list

    def generate_competitive_analysis(self, company: str) -> Dict:
        """Generate comprehensive competitive analysis."""
        metrics_list = self.analyze_competitor_metrics(company)
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([vars(m) for m in metrics_list])
        
        # Calculate relative metrics
        df['relative_market_share'] = df['market_share'] / df['market_share'].max()
        df['relative_growth'] = df['growth_rate'] / df['growth_rate'].max()
        df['relative_sentiment'] = df['sentiment_score'] / df['sentiment_score'].max()
        
        # Generate insights
        target_company = df[df['company'] == company].iloc[0]
        competitors = df[df['company'] != company]
        
        insights = {
            "company": company,
            "market_position": {
                "market_share_rank": int(df[df['company'] == company]['market_share'].rank(ascending=False).iloc[0]),
                "total_competitors": len(competitors),
                "market_share": target_company['market_share'],
                "relative_market_share": target_company['relative_market_share']
            },
            "competitive_advantages": {
                "strengths": self._identify_strengths(target_company, competitors),
                "weaknesses": self._identify_weaknesses(target_company, competitors)
            },
            "market_trends": {
                "growth_comparison": self._analyze_growth_trends(target_company, competitors),
                "sentiment_comparison": self._analyze_sentiment_trends(target_company, competitors)
            },
            "recommendations": self._generate_competitive_recommendations(target_company, competitors)
        }
        
        return insights

    def _identify_strengths(self, target: pd.Series, competitors: pd.DataFrame) -> List[str]:
        """Identify company strengths relative to competitors."""
        strengths = []
        if target['market_share'] > competitors['market_share'].mean():
            strengths.append("Strong market position")
        if target['growth_rate'] > competitors['growth_rate'].mean():
            strengths.append("Above-average growth rate")
        if target['sentiment_score'] > competitors['sentiment_score'].mean():
            strengths.append("Positive market sentiment")
        if target['financial_health'] > competitors['financial_health'].mean():
            strengths.append("Strong financial health")
        return strengths

    def _identify_weaknesses(self, target: pd.Series, competitors: pd.DataFrame) -> List[str]:
        """Identify company weaknesses relative to competitors."""
        weaknesses = []
        if target['market_share'] < competitors['market_share'].mean():
            weaknesses.append("Below-average market share")
        if target['growth_rate'] < competitors['growth_rate'].mean():
            weaknesses.append("Slower growth rate")
        if target['sentiment_score'] < competitors['sentiment_score'].mean():
            weaknesses.append("Negative market sentiment")
        if target['financial_health'] < competitors['financial_health'].mean():
            weaknesses.append("Weaker financial health")
        return weaknesses

    def _analyze_growth_trends(self, target: pd.Series, competitors: pd.DataFrame) -> Dict:
        """Analyze growth trends relative to competitors."""
        return {
            "company_growth": target['growth_rate'],
            "industry_average": competitors['growth_rate'].mean(),
            "growth_rank": int(competitors['growth_rate'].rank(ascending=False).iloc[0]),
            "trend": "above" if target['growth_rate'] > competitors['growth_rate'].mean() else "below"
        }

    def _analyze_sentiment_trends(self, target: pd.Series, competitors: pd.DataFrame) -> Dict:
        """Analyze sentiment trends relative to competitors."""
        return {
            "company_sentiment": target['sentiment_score'],
            "industry_average": competitors['sentiment_score'].mean(),
            "sentiment_rank": int(competitors['sentiment_score'].rank(ascending=False).iloc[0]),
            "trend": "positive" if target['sentiment_score'] > competitors['sentiment_score'].mean() else "negative"
        }

    def _generate_competitive_recommendations(self, target: pd.Series, competitors: pd.DataFrame) -> List[str]:
        """Generate recommendations based on competitive analysis."""
        recommendations = []
        
        # Market share recommendations
        if target['market_share'] < competitors['market_share'].mean():
            recommendations.append("Consider strategies to increase market share")
        
        # Growth recommendations
        if target['growth_rate'] < competitors['growth_rate'].mean():
            recommendations.append("Focus on accelerating growth through innovation or market expansion")
        
        # Sentiment recommendations
        if target['sentiment_score'] < competitors['sentiment_score'].mean():
            recommendations.append("Improve market perception through better communication and PR")
        
        # Financial health recommendations
        if target['financial_health'] < competitors['financial_health'].mean():
            recommendations.append("Strengthen financial position through cost optimization and revenue growth")
        
        return recommendations 