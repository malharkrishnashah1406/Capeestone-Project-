from src.impact_predictor.financial_analyzer import FinancialAnalyzer
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
from pathlib import Path

def format_currency(value: float) -> str:
    """Format number as currency."""
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format number as percentage."""
    return f"{value:.2f}%"

def create_metrics_dashboard(metrics, company_name: str):
    """Create an interactive dashboard of key metrics."""
    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "Revenue Metrics", "Funding Metrics",
            "Market Metrics", "Innovation Metrics",
            "External Impact Metrics", "Risk Metrics"
        )
    )

    # Revenue Metrics
    revenue_metrics = {
        "Total Revenue": metrics.total_revenue,
        "Revenue Growth": metrics.revenue_growth_rate,
        "Net Profit": metrics.net_profit_loss,
        "EBITDA": metrics.ebitda,
        "Gross Margin": metrics.gross_profit_margin,
        "Operating Margin": metrics.operating_profit_margin,
        "Net Margin": metrics.net_profit_margin
    }
    
    fig.add_trace(
        go.Bar(
            x=list(revenue_metrics.keys()),
            y=list(revenue_metrics.values()),
            name="Revenue Metrics"
        ),
        row=1, col=1
    )

    # Funding Metrics
    funding_metrics = {
        "Total Funding": metrics.total_funding_raised,
        "Valuation": metrics.valuation,
        "VC Dependency": metrics.vc_dependency,
        "Equity Dilution": metrics.equity_dilution,
        "Convertible Debt": metrics.convertible_debt,
        "Stock Growth": metrics.stock_price_growth
    }
    
    fig.add_trace(
        go.Bar(
            x=list(funding_metrics.keys()),
            y=list(funding_metrics.values()),
            name="Funding Metrics"
        ),
        row=1, col=2
    )

    # Market Metrics
    market_metrics = {
        "Market Share": metrics.market_share,
        "CAC": metrics.customer_acquisition_cost,
        "LTV": metrics.lifetime_value_per_customer,
        "LTV/CAC": metrics.ltv_cac_ratio,
        "Churn Rate": metrics.churn_rate,
        "ARPU": metrics.revenue_per_user
    }
    
    fig.add_trace(
        go.Bar(
            x=list(market_metrics.keys()),
            y=list(market_metrics.values()),
            name="Market Metrics"
        ),
        row=2, col=1
    )

    # Innovation Metrics
    innovation_metrics = {
        "R&D Expenditure": metrics.rd_expenditure,
        "Tech Adoption": metrics.technology_adoption_rate,
        "Talent Migration": metrics.talent_migration_rate,
        "Geo Expansion": metrics.geographical_expansion_rate,
        "ESG Score": metrics.esg_compliance_score,
        "Supply Chain": metrics.supply_chain_efficiency
    }
    
    fig.add_trace(
        go.Bar(
            x=list(innovation_metrics.keys()),
            y=list(innovation_metrics.values()),
            name="Innovation Metrics"
        ),
        row=2, col=2
    )

    # External Impact Metrics
    external_metrics = {
        "Inflation Impact": metrics.inflation_impact,
        "Interest Rate": metrics.interest_rate_impact,
        "Global Trade": metrics.global_trade_impact,
        "Pandemic Impact": metrics.pandemic_impact,
        "VC Market": metrics.vc_market_impact,
        "Stock Market": metrics.stock_market_impact
    }
    
    fig.add_trace(
        go.Bar(
            x=list(external_metrics.keys()),
            y=list(external_metrics.values()),
            name="External Impact"
        ),
        row=3, col=1
    )

    # Risk Metrics
    risk_metrics = {
        "Investor Risk": metrics.investor_concentration_risk,
        "Regulatory Risk": metrics.regulatory_risk_score,
        "Policy Impact": metrics.government_policy_impact,
        "Tech Disruption": metrics.tech_disruption_impact,
        "Competitor IPO": metrics.competitor_ipo_impact,
        "Geopolitical": metrics.geopolitical_impact
    }
    
    fig.add_trace(
        go.Bar(
            x=list(risk_metrics.keys()),
            y=list(risk_metrics.values()),
            name="Risk Metrics"
        ),
        row=3, col=2
    )

    # Update layout
    fig.update_layout(
        height=1200,
        width=1600,
        title_text=f"Financial Analysis Dashboard - {company_name}",
        showlegend=False
    )

    # Save the dashboard
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    fig.write_html(output_dir / f"{company_name}_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

def generate_report(metrics, company_name: str):
    """Generate a comprehensive report of all metrics."""
    report = {
        "company": company_name,
        "timestamp": datetime.now().isoformat(),
        "revenue_metrics": {
            "Total Revenue": format_currency(metrics.total_revenue),
            "Revenue Growth Rate": format_percentage(metrics.revenue_growth_rate),
            "Net Profit/Loss": format_currency(metrics.net_profit_loss),
            "EBITDA": format_currency(metrics.ebitda),
            "Gross Profit Margin": format_percentage(metrics.gross_profit_margin),
            "Operating Profit Margin": format_percentage(metrics.operating_profit_margin),
            "Net Profit Margin": format_percentage(metrics.net_profit_margin),
            "Free Cash Flow": format_currency(metrics.free_cash_flow),
            "Burn Rate": format_currency(metrics.burn_rate),
            "Break-even Point": f"{metrics.break_even_point:.1f} months"
        },
        "funding_metrics": {
            "Total Funding Raised": format_currency(metrics.total_funding_raised),
            "Funding Rounds": metrics.funding_rounds_count,
            "Valuation": format_currency(metrics.valuation),
            "Investor Concentration Risk": format_percentage(metrics.investor_concentration_risk),
            "VC Dependency": format_percentage(metrics.vc_dependency),
            "Equity Dilution": format_percentage(metrics.equity_dilution),
            "Convertible Debt": format_currency(metrics.convertible_debt),
            "IPO Status": "Yes" if metrics.ipo_status else "No",
            "Stock Price Growth": format_percentage(metrics.stock_price_growth),
            "M&A Activity": metrics.m_and_a_activity
        },
        "market_metrics": {
            "Market Share": format_percentage(metrics.market_share),
            "Customer Acquisition Cost": format_currency(metrics.customer_acquisition_cost),
            "Lifetime Value per Customer": format_currency(metrics.lifetime_value_per_customer),
            "LTV/CAC Ratio": f"{metrics.ltv_cac_ratio:.2f}",
            "Churn Rate": format_percentage(metrics.churn_rate),
            "Revenue per User": format_currency(metrics.revenue_per_user),
            "Active User Growth": format_percentage(metrics.active_user_growth),
            "Brand Sentiment Score": f"{metrics.brand_sentiment_score:.2f}",
            "Competitor Funding Trends": format_percentage(metrics.competitor_funding_trends),
            "Subscription Renewal Rate": format_percentage(metrics.subscription_renewal_rate)
        },
        "innovation_metrics": {
            "R&D Expenditure": format_currency(metrics.rd_expenditure),
            "Technology Adoption Rate": format_percentage(metrics.technology_adoption_rate),
            "Talent Migration Rate": format_percentage(metrics.talent_migration_rate),
            "Geographical Expansion Rate": format_percentage(metrics.geographical_expansion_rate),
            "ESG Compliance Score": f"{metrics.esg_compliance_score:.2f}",
            "Infrastructure Investment": format_currency(metrics.infrastructure_investment),
            "Patents Count": metrics.patents_count,
            "Supply Chain Efficiency": f"{metrics.supply_chain_efficiency:.2f}",
            "Customer Satisfaction Index": f"{metrics.customer_satisfaction_index:.2f}",
            "Regulatory Risk Score": f"{metrics.regulatory_risk_score:.2f}"
        },
        "external_impact_metrics": {
            "Inflation Impact": format_percentage(metrics.inflation_impact),
            "Interest Rate Impact": format_percentage(metrics.interest_rate_impact),
            "Global Trade Impact": format_percentage(metrics.global_trade_impact),
            "Pandemic Impact": format_percentage(metrics.pandemic_impact),
            "VC Market Impact": format_percentage(metrics.vc_market_impact),
            "Stock Market Impact": format_percentage(metrics.stock_market_impact),
            "Government Policy Impact": format_percentage(metrics.government_policy_impact),
            "Tech Disruption Impact": format_percentage(metrics.tech_disruption_impact),
            "Competitor IPO Impact": format_percentage(metrics.competitor_ipo_impact),
            "Geopolitical Impact": format_percentage(metrics.geopolitical_impact)
        }
    }

    # Save the report
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    report_path = output_dir / f"{company_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=4)
    
    return report_path

def main():
    # Initialize the analyzer
    analyzer = FinancialAnalyzer()
    
    # Get company name from user
    company_name = input("Enter company name or ticker symbol: ")
    
    try:
        # Analyze company financials
        print(f"\nAnalyzing {company_name}...")
        metrics = analyzer.analyze_company_financials(company_name)
        
        if metrics is None:
            print(f"Error: Could not analyze {company_name}")
            return
        
        # Create dashboard
        print("Creating interactive dashboard...")
        create_metrics_dashboard(metrics, company_name)
        
        # Generate report
        print("Generating comprehensive report...")
        report_path = generate_report(metrics, company_name)
        
        print(f"\nAnalysis complete!")
        print(f"Dashboard saved to: reports/{company_name}_dashboard_*.html")
        print(f"Report saved to: {report_path}")
        
        # Print key metrics
        print("\nKey Metrics Summary:")
        print(f"Total Revenue: {format_currency(metrics.total_revenue)}")
        print(f"Revenue Growth Rate: {format_percentage(metrics.revenue_growth_rate)}")
        print(f"Market Share: {format_percentage(metrics.market_share)}")
        print(f"Valuation: {format_currency(metrics.valuation)}")
        print(f"Brand Sentiment Score: {metrics.brand_sentiment_score:.2f}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 