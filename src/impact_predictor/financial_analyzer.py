from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from src.impact_predictor.data_sources import DataSources
from src.impact_predictor.ml_models import MLModels
import emoji
from textblob import TextBlob

@dataclass
class FinancialMetrics:
    # Revenue Metrics
    total_revenue: float
    revenue_growth_rate: float
    net_profit: float
    ebitda: float
    gross_profit_margin: float
    operating_profit_margin: float
    net_profit_margin: float
    free_cash_flow: float
    burn_rate: float
    break_even_point: float
    
    # Funding Metrics
    total_funding_raised: float
    funding_rounds: int
    valuation: float
    investor_concentration_risk: float
    vc_dependency: float
    equity_dilution: float
    convertible_debt: float
    ipo_status: bool
    stock_price_growth: float
    ma_activity: int
    
    # Market Metrics
    market_share: float
    customer_acquisition_cost: float
    ltv_per_customer: float
    ltv_cac_ratio: float
    churn_rate: float
    revenue_per_user: float
    active_user_growth: float
    brand_sentiment_score: float
    competitor_funding_trends: float
    subscription_renewal_rate: float
    
    # Innovation Metrics
    rd_expenditure: float
    tech_adoption_rate: float
    talent_migration_rate: float
    geo_expansion_rate: float
    esg_compliance_score: float
    infrastructure_investment: float
    patents_ip_owned: int
    supply_chain_efficiency: float
    customer_satisfaction_index: float
    regulatory_compliance_score: float
    
    # External Impact Metrics
    inflation_impact: float
    interest_rate_impact: float
    global_trade_impact: float
    pandemic_impact: float
    vc_market_impact: float
    stock_market_impact: float
    gov_policy_impact: float
    tech_disruption_impact: float
    competitor_ipo_impact: float
    geopolitical_impact: float

class FinancialAnalyzer:
    def __init__(self):
        self.data_sources = DataSources()
        self.ml_models = MLModels()
        
    def analyze_company_financials(self, company: str, ticker: Optional[str] = None) -> FinancialMetrics:
        """Analyze comprehensive financial metrics for a company."""
        try:
            # Get company info and market data
            company_info = self.data_sources.get_company_info(ticker or company)
            market_data = self.data_sources.get_market_data(ticker or company)
            news_articles = self.data_sources.get_news_articles(company)
            
            # Calculate revenue metrics
            revenue_metrics = self._calculate_revenue_metrics(company_info, market_data)
            
            # Calculate funding metrics
            funding_metrics = self._calculate_funding_metrics(company_info, market_data)
            
            # Calculate market metrics
            market_metrics = self._calculate_market_metrics(company_info, market_data, news_articles)
            
            # Calculate innovation metrics
            innovation_metrics = self._calculate_innovation_metrics(company_info, news_articles)
            
            # Calculate external impact metrics
            external_metrics = self._calculate_external_impact_metrics(company_info, market_data, news_articles)
            
            # Combine all metrics
            return FinancialMetrics(
                # Revenue Metrics
                total_revenue=revenue_metrics['total_revenue'],
                revenue_growth_rate=revenue_metrics['revenue_growth_rate'],
                net_profit=revenue_metrics['net_profit'],
                ebitda=revenue_metrics['ebitda'],
                gross_profit_margin=revenue_metrics['gross_profit_margin'],
                operating_profit_margin=revenue_metrics['operating_profit_margin'],
                net_profit_margin=revenue_metrics['net_profit_margin'],
                free_cash_flow=revenue_metrics['free_cash_flow'],
                burn_rate=revenue_metrics['burn_rate'],
                break_even_point=revenue_metrics['break_even_point'],
                
                # Funding Metrics
                total_funding_raised=funding_metrics['total_funding_raised'],
                funding_rounds=funding_metrics['funding_rounds'],
                valuation=funding_metrics['valuation'],
                investor_concentration_risk=funding_metrics['investor_concentration_risk'],
                vc_dependency=funding_metrics['vc_dependency'],
                equity_dilution=funding_metrics['equity_dilution'],
                convertible_debt=funding_metrics['convertible_debt'],
                ipo_status=funding_metrics['ipo_status'],
                stock_price_growth=funding_metrics['stock_price_growth'],
                ma_activity=funding_metrics['ma_activity'],
                
                # Market Metrics
                market_share=market_metrics['market_share'],
                customer_acquisition_cost=market_metrics['customer_acquisition_cost'],
                ltv_per_customer=market_metrics['ltv_per_customer'],
                ltv_cac_ratio=market_metrics['ltv_cac_ratio'],
                churn_rate=market_metrics['churn_rate'],
                revenue_per_user=market_metrics['revenue_per_user'],
                active_user_growth=market_metrics['active_user_growth'],
                brand_sentiment_score=market_metrics['brand_sentiment_score'],
                competitor_funding_trends=market_metrics['competitor_funding_trends'],
                subscription_renewal_rate=market_metrics['subscription_renewal_rate'],
                
                # Innovation Metrics
                rd_expenditure=innovation_metrics['rd_expenditure'],
                tech_adoption_rate=innovation_metrics['tech_adoption_rate'],
                talent_migration_rate=innovation_metrics['talent_migration_rate'],
                geo_expansion_rate=innovation_metrics['geo_expansion_rate'],
                esg_compliance_score=innovation_metrics['esg_compliance_score'],
                infrastructure_investment=innovation_metrics['infrastructure_investment'],
                patents_ip_owned=innovation_metrics['patents_ip_owned'],
                supply_chain_efficiency=innovation_metrics['supply_chain_efficiency'],
                customer_satisfaction_index=innovation_metrics['customer_satisfaction_index'],
                regulatory_compliance_score=innovation_metrics['regulatory_compliance_score'],
                
                # External Impact Metrics
                inflation_impact=external_metrics['inflation_impact'],
                interest_rate_impact=external_metrics['interest_rate_impact'],
                global_trade_impact=external_metrics['global_trade_impact'],
                pandemic_impact=external_metrics['pandemic_impact'],
                vc_market_impact=external_metrics['vc_market_impact'],
                stock_market_impact=external_metrics['stock_market_impact'],
                gov_policy_impact=external_metrics['gov_policy_impact'],
                tech_disruption_impact=external_metrics['tech_disruption_impact'],
                competitor_ipo_impact=external_metrics['competitor_ipo_impact'],
                geopolitical_impact=external_metrics['geopolitical_impact']
            )
            
        except Exception as e:
            print(f"Error in financial analysis: {str(e)}")
            return None
    
    def _calculate_revenue_metrics(self, company_info: Dict, market_data: pd.DataFrame) -> Dict:
        """Calculate revenue-related metrics."""
        try:
            # Get financial data from company info
            financial_data = company_info.get('financialData', {})
            
            # Calculate metrics
            total_revenue = financial_data.get('totalRevenue', 0)
            net_income = financial_data.get('netIncome', 0)
            ebitda = financial_data.get('ebitda', 0)
            gross_profit = financial_data.get('grossProfits', 0)
            operating_income = financial_data.get('operatingIncome', 0)
            
            # Calculate growth rate
            if market_data is not None and not market_data.empty:
                revenue_growth = ((market_data['Close'].iloc[-1] / market_data['Close'].iloc[0]) - 1) * 100
            else:
                revenue_growth = 0
            
            # Calculate margins
            gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue else 0
            operating_profit_margin = (operating_income / total_revenue * 100) if total_revenue else 0
            net_profit_margin = (net_income / total_revenue * 100) if total_revenue else 0
            
            # Calculate cash flow metrics
            free_cash_flow = financial_data.get('freeCashflow', 0)
            burn_rate = abs(min(0, free_cash_flow)) / 12  # Monthly burn rate
            break_even_point = abs(free_cash_flow) / (total_revenue / 12) if total_revenue else 0
            
            return {
                'total_revenue': total_revenue,
                'revenue_growth_rate': revenue_growth,
                'net_profit': net_income,
                'ebitda': ebitda,
                'gross_profit_margin': gross_profit_margin,
                'operating_profit_margin': operating_profit_margin,
                'net_profit_margin': net_profit_margin,
                'free_cash_flow': free_cash_flow,
                'burn_rate': burn_rate,
                'break_even_point': break_even_point
            }
        except Exception as e:
            print(f"Error calculating revenue metrics: {str(e)}")
            return self._get_default_revenue_metrics()
    
    def _calculate_funding_metrics(self, company_info: Dict, market_data: pd.DataFrame) -> Dict:
        """Calculate funding-related metrics."""
        try:
            # Get funding data
            funding_data = company_info.get('fundingData', {})
            market_cap = company_info.get('marketCap', 0)
            
            # Calculate metrics
            total_funding = funding_data.get('totalFunding', 0)
            funding_rounds = len(funding_data.get('rounds', []))
            valuation = market_cap or funding_data.get('valuation', 0)
            
            # Calculate investor metrics
            investors = funding_data.get('investors', [])
            investor_concentration = len(set(investors)) / len(investors) if investors else 0
            vc_dependency = total_funding / (valuation or 1) * 100
            
            # Calculate equity metrics
            equity_dilution = funding_data.get('equityDilution', 0)
            convertible_debt = funding_data.get('convertibleDebt', 0)
            
            # Calculate IPO status and stock growth
            ipo_status = company_info.get('isPublic', False)
            if market_data is not None and not market_data.empty:
                stock_growth = ((market_data['Close'].iloc[-1] / market_data['Close'].iloc[0]) - 1) * 100
            else:
                stock_growth = 0
            
            # Count M&A activity
            ma_activity = len(company_info.get('acquisitions', []))
            
            return {
                'total_funding_raised': total_funding,
                'funding_rounds': funding_rounds,
                'valuation': valuation,
                'investor_concentration_risk': investor_concentration,
                'vc_dependency': vc_dependency,
                'equity_dilution': equity_dilution,
                'convertible_debt': convertible_debt,
                'ipo_status': ipo_status,
                'stock_price_growth': stock_growth,
                'ma_activity': ma_activity
            }
        except Exception as e:
            print(f"Error calculating funding metrics: {str(e)}")
            return self._get_default_funding_metrics()
    
    def _calculate_market_metrics(self, company_info: Dict, market_data: pd.DataFrame, news_articles: List[Dict]) -> Dict:
        """Calculate market-related metrics."""
        try:
            # Get market data
            market_cap = company_info.get('marketCap', 0)
            industry_market_cap = company_info.get('industryMarketCap', 0)
            
            # Calculate market share
            market_share = (market_cap / industry_market_cap * 100) if industry_market_cap else 0
            
            # Calculate customer metrics
            customer_metrics = company_info.get('customerMetrics', {})
            cac = customer_metrics.get('acquisitionCost', 0)
            ltv = customer_metrics.get('lifetimeValue', 0)
            ltv_cac = ltv / cac if cac else 0
            
            # Calculate user metrics
            active_users = customer_metrics.get('activeUsers', 0)
            previous_users = customer_metrics.get('previousUsers', 0)
            user_growth = ((active_users / previous_users) - 1) * 100 if previous_users else 0
            
            # Calculate revenue per user
            revenue = company_info.get('totalRevenue', 0)
            revenue_per_user = revenue / active_users if active_users else 0
            
            # Calculate sentiment score
            sentiment_score = self._calculate_sentiment_score(news_articles)
            
            # Calculate competitor metrics
            competitor_funding = company_info.get('competitorFunding', 0)
            subscription_rate = customer_metrics.get('subscriptionRenewalRate', 0)
            
            return {
                'market_share': market_share,
                'customer_acquisition_cost': cac,
                'ltv_per_customer': ltv,
                'ltv_cac_ratio': ltv_cac,
                'churn_rate': customer_metrics.get('churnRate', 0),
                'revenue_per_user': revenue_per_user,
                'active_user_growth': user_growth,
                'brand_sentiment_score': sentiment_score,
                'competitor_funding_trends': competitor_funding,
                'subscription_renewal_rate': subscription_rate
            }
        except Exception as e:
            print(f"Error calculating market metrics: {str(e)}")
            return self._get_default_market_metrics()
    
    def _calculate_innovation_metrics(self, company_info: Dict, news_articles: List[Dict]) -> Dict:
        """Calculate innovation-related metrics."""
        try:
            # Get innovation data
            innovation_data = company_info.get('innovationData', {})
            
            # Calculate R&D metrics
            rd_expenditure = innovation_data.get('rdExpenditure', 0)
            tech_adoption = innovation_data.get('techAdoptionRate', 0)
            
            # Calculate talent metrics
            talent_data = innovation_data.get('talentData', {})
            talent_migration = talent_data.get('migrationRate', 0)
            geo_expansion = talent_data.get('geoExpansionRate', 0)
            
            # Calculate ESG and compliance
            esg_score = innovation_data.get('esgScore', 0)
            infrastructure = innovation_data.get('infrastructureInvestment', 0)
            
            # Calculate IP metrics
            patents = innovation_data.get('patents', [])
            supply_chain = innovation_data.get('supplyChainEfficiency', 0)
            
            # Calculate customer satisfaction
            satisfaction = innovation_data.get('customerSatisfaction', 0)
            compliance = innovation_data.get('regulatoryCompliance', 0)
            
            return {
                'rd_expenditure': rd_expenditure,
                'tech_adoption_rate': tech_adoption,
                'talent_migration_rate': talent_migration,
                'geo_expansion_rate': geo_expansion,
                'esg_compliance_score': esg_score,
                'infrastructure_investment': infrastructure,
                'patents_ip_owned': len(patents),
                'supply_chain_efficiency': supply_chain,
                'customer_satisfaction_index': satisfaction,
                'regulatory_compliance_score': compliance
            }
        except Exception as e:
            print(f"Error calculating innovation metrics: {str(e)}")
            return self._get_default_innovation_metrics()
    
    def _calculate_external_impact_metrics(self, company_info: Dict, market_data: pd.DataFrame, news_articles: List[Dict]) -> Dict:
        """Calculate external impact metrics."""
        try:
            # Get external impact data
            impact_data = company_info.get('externalImpactData', {})
            
            # Calculate economic impacts
            inflation = impact_data.get('inflationImpact', 0)
            interest = impact_data.get('interestRateImpact', 0)
            trade = impact_data.get('globalTradeImpact', 0)
            
            # Calculate market impacts
            pandemic = impact_data.get('pandemicImpact', 0)
            vc_market = impact_data.get('vcMarketImpact', 0)
            stock_market = impact_data.get('stockMarketImpact', 0)
            
            # Calculate policy and disruption impacts
            policy = impact_data.get('governmentPolicyImpact', 0)
            tech_disruption = impact_data.get('techDisruptionImpact', 0)
            competitor_ipo = impact_data.get('competitorIpoImpact', 0)
            geopolitical = impact_data.get('geopoliticalImpact', 0)
            
            return {
                'inflation_impact': inflation,
                'interest_rate_impact': interest,
                'global_trade_impact': trade,
                'pandemic_impact': pandemic,
                'vc_market_impact': vc_market,
                'stock_market_impact': stock_market,
                'gov_policy_impact': policy,
                'tech_disruption_impact': tech_disruption,
                'competitor_ipo_impact': competitor_ipo,
                'geopolitical_impact': geopolitical
            }
        except Exception as e:
            print(f"Error calculating external impact metrics: {str(e)}")
            return self._get_default_external_impact_metrics()
    
    def _calculate_sentiment_score(self, news_articles: List[Dict]) -> float:
        """Calculate sentiment score from news articles using TextBlob and emoji analysis."""
        try:
            if not news_articles:
                return 0.0
            
            sentiments = []
            for article in news_articles:
                text = f"{article.get('title', '')} {article.get('content', '')}"
                
                # Convert emojis to text for better sentiment analysis
                text = emoji.demojize(text)
                
                # Analyze sentiment
                blob = TextBlob(text)
                sentiments.append(blob.sentiment.polarity)
            
            # Calculate average sentiment
            return sum(sentiments) / len(sentiments)
        except Exception as e:
            print(f"Error calculating sentiment score: {str(e)}")
            return 0.0
    
    def _get_default_revenue_metrics(self) -> Dict:
        return {
            'total_revenue': 0,
            'revenue_growth_rate': 0,
            'net_profit': 0,
            'ebitda': 0,
            'gross_profit_margin': 0,
            'operating_profit_margin': 0,
            'net_profit_margin': 0,
            'free_cash_flow': 0,
            'burn_rate': 0,
            'break_even_point': 0
        }
    
    def _get_default_funding_metrics(self) -> Dict:
        return {
            'total_funding_raised': 0,
            'funding_rounds': 0,
            'valuation': 0,
            'investor_concentration_risk': 0,
            'vc_dependency': 0,
            'equity_dilution': 0,
            'convertible_debt': 0,
            'ipo_status': False,
            'stock_price_growth': 0,
            'ma_activity': 0
        }
    
    def _get_default_market_metrics(self) -> Dict:
        return {
            'market_share': 0,
            'customer_acquisition_cost': 0,
            'ltv_per_customer': 0,
            'ltv_cac_ratio': 0,
            'churn_rate': 0,
            'revenue_per_user': 0,
            'active_user_growth': 0,
            'brand_sentiment_score': 0,
            'competitor_funding_trends': 0,
            'subscription_renewal_rate': 0
        }
    
    def _get_default_innovation_metrics(self) -> Dict:
        return {
            'rd_expenditure': 0,
            'tech_adoption_rate': 0,
            'talent_migration_rate': 0,
            'geo_expansion_rate': 0,
            'esg_compliance_score': 0,
            'infrastructure_investment': 0,
            'patents_ip_owned': 0,
            'supply_chain_efficiency': 0,
            'customer_satisfaction_index': 0,
            'regulatory_compliance_score': 0
        }
    
    def _get_default_external_impact_metrics(self) -> Dict:
        return {
            'inflation_impact': 0,
            'interest_rate_impact': 0,
            'global_trade_impact': 0,
            'pandemic_impact': 0,
            'vc_market_impact': 0,
            'stock_market_impact': 0,
            'gov_policy_impact': 0,
            'tech_disruption_impact': 0,
            'competitor_ipo_impact': 0,
            'geopolitical_impact': 0
        } 