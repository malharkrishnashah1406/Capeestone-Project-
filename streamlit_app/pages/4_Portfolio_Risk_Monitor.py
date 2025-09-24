"""
Portfolio Risk Monitor Page.

This page provides portfolio risk monitoring and analysis tools.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from simulation.domain_response import DomainResponseSimulator
from simulation.shocks import ShockGenerator
from utils.registry import get_domain, list_domain_keys


def create_portfolio_builder():
    """Create portfolio builder section."""
    st.header("💼 Portfolio Builder")
    
    # Portfolio configuration
    st.subheader("Portfolio Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        portfolio_name = st.text_input("Portfolio Name", "Sample Portfolio")
        portfolio_description = st.text_area("Portfolio Description", "A sample portfolio for demonstration")
        base_currency = st.selectbox("Base Currency", ["USD", "EUR", "GBP", "JPY"])
    
    with col2:
        risk_profile = st.selectbox("Risk Profile", ["conservative", "moderate", "aggressive"])
        total_value = st.number_input("Total Portfolio Value (USD)", min_value=1000000, value=10000000, step=1000000)
    
    # Holdings configuration
    st.subheader("Portfolio Holdings")
    
    domain_keys = list_domain_keys()
    
    # Sample holdings - use available domain keys
    available_domains = list_domain_keys()
    sample_holdings = [
        {
            "name": "VC Fund Alpha",
            "domain": "venture_capital" if "venture_capital" in available_domains else available_domains[0],
            "weight": 0.4,
            "value": 4000000,
            "features": {"dry_powder": 0.6, "fund_age_years": 3, "dpi": 1.2}
        },
        {
            "name": "SaaS Startup Beta",
            "domain": "saas" if "saas" in available_domains else available_domains[1] if len(available_domains) > 1 else available_domains[0],
            "weight": 0.3,
            "value": 3000000,
            "features": {"arr": 1000000, "gross_churn": 0.05, "ltv_cac_ratio": 3.0}
        },
        {
            "name": "FinTech Company Gamma",
            "domain": "fintech" if "fintech" in available_domains else available_domains[2] if len(available_domains) > 2 else available_domains[0],
            "weight": 0.3,
            "value": 3000000,
            "features": {"tpv": 10000000, "fraud_rate": 0.02, "regulatory_compliance_score": 0.8}
        }
    ]
    
    # Holdings table
    holdings_data = []
    for i, holding in enumerate(sample_holdings):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            name = st.text_input(f"Holding {i+1} Name", holding["name"], key=f"name_{i}")
        
        with col2:
            # Find the index of the domain, or use 0 if not found
            domain_index = 0
            if holding["domain"] in domain_keys:
                domain_index = domain_keys.index(holding["domain"])
            domain = st.selectbox(f"Domain {i+1}", domain_keys, index=domain_index, key=f"domain_{i}")
        
        with col3:
            weight = st.slider(f"Weight {i+1}", 0.0, 1.0, holding["weight"], step=0.05, key=f"weight_{i}")
        
        with col4:
            value = st.number_input(f"Value {i+1} (USD)", min_value=0, value=holding["value"], step=100000, key=f"value_{i}")
        
        with col5:
            features = st.text_area(f"Features {i+1} (JSON)", json.dumps(holding["features"], indent=2), key=f"features_{i}")
        
        holdings_data.append({
            "name": name,
            "domain": domain,
            "weight": weight,
            "value": value,
            "features": json.loads(features) if features.strip() else {}
        })
    
    # Portfolio summary
    st.subheader("Portfolio Summary")
    
    total_weight = sum(h["weight"] for h in holdings_data)
    total_portfolio_value = sum(h["value"] for h in holdings_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Weight", f"{total_weight:.2f}")
    with col2:
        st.metric("Total Value", f"${total_portfolio_value:,.0f}")
    with col3:
        st.metric("Number of Holdings", len(holdings_data))
    with col4:
        st.metric("Average Weight", f"{total_weight/len(holdings_data):.2f}" if holdings_data else "0.00")
    
    # Weight validation
    if abs(total_weight - 1.0) > 0.01:
        st.warning(f"Portfolio weights sum to {total_weight:.2f}, should be 1.0")
    else:
        st.success("Portfolio weights are valid")
    
    # Store portfolio in session state
    st.session_state['portfolio'] = {
        "name": portfolio_name,
        "description": portfolio_description,
        "base_currency": base_currency,
        "risk_profile": risk_profile,
        "total_value": total_value,
        "holdings": holdings_data
    }


def create_risk_analysis():
    """Create risk analysis section."""
    st.header("⚠️ Risk Analysis")
    
    if 'portfolio' not in st.session_state:
        st.info("Build a portfolio first to perform risk analysis.")
        return
    
    portfolio = st.session_state['portfolio']
    
    # Risk metrics
    st.subheader("Portfolio Risk Metrics")
    
    # Calculate domain exposure
    domain_exposure = {}
    for holding in portfolio['holdings']:
        domain = holding['domain']
        if domain not in domain_exposure:
            domain_exposure[domain] = 0.0
        domain_exposure[domain] += holding['weight']
    
    # Display domain exposure
    col1, col2 = st.columns(2)
    
    with col1:
        # Domain exposure chart
        exposure_df = pd.DataFrame([
            {"Domain": domain, "Exposure": exposure}
            for domain, exposure in domain_exposure.items()
        ])
        
        fig_exposure = px.pie(
            exposure_df,
            values='Exposure',
            names='Domain',
            title="Domain Exposure"
        )
        st.plotly_chart(fig_exposure, width='stretch')
    
    with col2:
        # Risk profile by domain - use available domains
        available_domains = list_domain_keys()
        risk_profiles = {}
        for domain in available_domains:
            if "venture_capital" in domain or "fintech" in domain or "cross_border" in domain or "mediatech" in domain:
                risk_profiles[domain] = "high"
            elif "saas" in domain or "greentech" in domain or "accelerators" in domain or "public_sector" in domain:
                risk_profiles[domain] = "medium"
            else:
                risk_profiles[domain] = "medium"  # Default to medium
        
        risk_data = []
        for domain, exposure in domain_exposure.items():
            risk_data.append({
                "Domain": domain,
                "Exposure": exposure,
                "Risk Profile": risk_profiles.get(domain, "medium")
            })
        
        risk_df = pd.DataFrame(risk_data)
        
        fig_risk = px.bar(
            risk_df,
            x='Domain',
            y='Exposure',
            color='Risk Profile',
            title="Domain Exposure by Risk Profile"
        )
        st.plotly_chart(fig_risk, width='stretch')
    
    # Risk metrics summary
    st.subheader("Risk Metrics Summary")
    
    # Calculate weighted risk metrics
    total_high_risk = sum(exposure for domain, exposure in domain_exposure.items() 
                         if risk_profiles.get(domain, "medium") == "high")
    total_medium_risk = sum(exposure for domain, exposure in domain_exposure.items() 
                           if risk_profiles.get(domain, "medium") == "medium")
    total_low_risk = sum(exposure for domain, exposure in domain_exposure.items() 
                        if risk_profiles.get(domain, "medium") == "low")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("High Risk Exposure", f"{total_high_risk:.1%}")
    with col2:
        st.metric("Medium Risk Exposure", f"{total_medium_risk:.1%}")
    with col3:
        st.metric("Low Risk Exposure", f"{total_low_risk:.1%}")
    with col4:
        st.metric("Risk Score", f"{total_high_risk * 0.8 + total_medium_risk * 0.5 + total_low_risk * 0.2:.2f}")


def create_stress_testing():
    """Create stress testing section."""
    st.header("🧪 Stress Testing")
    
    if 'portfolio' not in st.session_state:
        st.info("Build a portfolio first to perform stress testing.")
        return
    
    portfolio = st.session_state['portfolio']
    
    # Stress test scenarios
    st.subheader("Stress Test Scenarios")
    
    stress_scenarios = {
        "severe_recession": "Economic recession with market crash and policy rate changes",
        "tech_regulation": "Technology regulation with regulatory changes and cybersecurity breaches",
        "trade_conflict": "Trade conflict with trade wars and political instability",
        "climate_crisis": "Climate crisis with extreme weather and regulatory changes",
        "pandemic_response": "Pandemic response with public health emergency and policy changes",
        "liquidity_crisis": "Liquidity crisis with policy rate changes and market crash",
        "black_swan": "Black swan event with multiple simultaneous shocks"
    }
    
    selected_scenarios = st.multiselect(
        "Select Stress Test Scenarios",
        list(stress_scenarios.keys()),
        default=["severe_recession", "tech_regulation"]
    )
    
    if st.button("Run Stress Tests", type="primary") and selected_scenarios:
        with st.spinner("Running stress tests..."):
            try:
                simulator = DomainResponseSimulator()
                shock_generator = ShockGenerator()
                
                stress_results = {}
                
                for scenario in selected_scenarios:
                    # Generate shocks for scenario
                    if scenario == "black_swan":
                        shocks = shock_generator.generate_shock_sequence(
                            num_shocks=5,
                            shock_types=['pandemic', 'market_crash', 'cybersecurity_breach', 'climate_event', 'political_instability']
                        )
                    elif scenario == "liquidity_crisis":
                        shocks = shock_generator.generate_shock_sequence(
                            num_shocks=2,
                            shock_types=['policy_rate_change', 'market_crash']
                        )
                    else:
                        shocks = shock_generator.generate_scenario_shocks(scenario)
                    
                    # Simulate portfolio response
                    portfolio_responses = {}
                    domain_weights = {}
                    
                    for holding in portfolio['holdings']:
                        domain_key = holding['domain']
                        features = holding['features']
                        weight = holding['weight']
                        
                        # Simulate domain response
                        response = simulator.simulate_domain_response(domain_key, features, shocks)
                        portfolio_responses[domain_key] = response
                        
                        if domain_key not in domain_weights:
                            domain_weights[domain_key] = 0.0
                        domain_weights[domain_key] += weight
                    
                    # Calculate portfolio risk metrics
                    portfolio_metrics = simulator.calculate_portfolio_risk(portfolio_responses, domain_weights)
                    
                    stress_results[scenario] = {
                        "shocks": shocks,
                        "responses": portfolio_responses,
                        "metrics": portfolio_metrics
                    }
                
                st.session_state['stress_results'] = stress_results
                st.success("Stress tests completed successfully!")
                
            except Exception as e:
                st.error(f"Stress testing failed: {str(e)}")
    
    # Display stress test results
    if 'stress_results' in st.session_state:
        st.subheader("Stress Test Results")
        
        stress_results = st.session_state['stress_results']
        
        # Create results comparison
        comparison_data = []
        
        for scenario, results in stress_results.items():
            metrics = results['metrics']
            for metric, value in metrics.items():
                comparison_data.append({
                    'Scenario': scenario.replace('_', ' ').title(),
                    'Metric': metric.replace('_', ' ').title(),
                    'Value': value
                })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Pivot for better visualization
            pivot_df = comparison_df.pivot(index='Scenario', columns='Metric', values='Value')
            
            st.dataframe(pivot_df, width='stretch')
            
            # Create heatmap
            fig_heatmap = px.imshow(
                pivot_df,
                title="Stress Test Results Heatmap",
                aspect="auto"
            )
            st.plotly_chart(fig_heatmap, width='stretch')
            
            # Create bar chart for key metrics
            key_metrics = ['portfolio_var_95', 'portfolio_var_99', 'portfolio_max_loss']
            available_metrics = [m for m in key_metrics if m in pivot_df.columns]
            
            if available_metrics:
                fig_bars = px.bar(
                    pivot_df[available_metrics],
                    title="Key Risk Metrics by Scenario"
                )
                st.plotly_chart(fig_bars, width='stretch')


def create_portfolio_monitoring():
    """Create portfolio monitoring section."""
    st.header("📊 Portfolio Monitoring")
    
    if 'portfolio' not in st.session_state:
        st.info("Build a portfolio first to monitor performance.")
        return
    
    portfolio = st.session_state['portfolio']
    
    # Performance tracking
    st.subheader("Performance Tracking")
    
    # Sample performance data
    performance_data = {
        "date": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", "2024-05-01"],
        "portfolio_value": [10000000, 10200000, 9800000, 10500000, 10800000],
        "benchmark_value": [10000000, 10100000, 9900000, 10300000, 10600000],
        "var_95": [0.05, 0.06, 0.08, 0.07, 0.06],
        "sharpe_ratio": [1.2, 1.1, 0.8, 1.3, 1.4]
    }
    
    df = pd.DataFrame(performance_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Performance chart
    fig_performance = go.Figure()
    
    fig_performance.add_trace(go.Scatter(
        x=df['date'],
        y=df['portfolio_value'],
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='blue')
    ))
    
    fig_performance.add_trace(go.Scatter(
        x=df['date'],
        y=df['benchmark_value'],
        mode='lines+markers',
        name='Benchmark Value',
        line=dict(color='gray', dash='dash')
    ))
    
    fig_performance.update_layout(
        title="Portfolio Performance Over Time",
        xaxis_title="Date",
        yaxis_title="Value (USD)",
        height=400
    )
    
    st.plotly_chart(fig_performance, width='stretch')
    
    # Risk metrics over time
    col1, col2 = st.columns(2)
    
    with col1:
        fig_var = px.line(
            df,
            x='date',
            y='var_95',
            title="VaR (95%) Over Time"
        )
        st.plotly_chart(fig_var, width='stretch')
    
    with col2:
        fig_sharpe = px.line(
            df,
            x='date',
            y='sharpe_ratio',
            title="Sharpe Ratio Over Time"
        )
        st.plotly_chart(fig_sharpe, width='stretch')
    
    # Current metrics
    st.subheader("Current Metrics")
    
    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Value", f"${latest['portfolio_value']:,.0f}")
    with col2:
        st.metric("Total Return", f"{((latest['portfolio_value'] - 10000000) / 10000000 * 100):.1f}%")
    with col3:
        st.metric("VaR (95%)", f"{latest['var_95']:.1%}")
    with col4:
        st.metric("Sharpe Ratio", f"{latest['sharpe_ratio']:.2f}")
    
    # Alerts and notifications
    st.subheader("Risk Alerts")
    
    alerts = []
    
    if latest['var_95'] > 0.07:
        alerts.append("⚠️ VaR (95%) is above threshold (7%)")
    
    if latest['sharpe_ratio'] < 1.0:
        alerts.append("⚠️ Sharpe ratio is below target (1.0)")
    
    if len(alerts) == 0:
        st.success("✅ No risk alerts - portfolio is within acceptable risk parameters")
    else:
        for alert in alerts:
            st.warning(alert)


def main():
    """Main function for the Portfolio Risk Monitor page."""
    st.set_page_config(
        page_title="Portfolio Risk Monitor",
        page_icon="💼",
        layout="wide"
    )
    
    st.title("💼 Portfolio Risk Monitor")
    st.markdown("""
    This page provides portfolio risk monitoring and analysis tools.
    Build portfolios, analyze risk metrics, perform stress testing, and monitor performance.
    """)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Portfolio Builder", "Risk Analysis", "Stress Testing", "Monitoring"
    ])
    
    with tab1:
        create_portfolio_builder()
    
    with tab2:
        create_risk_analysis()
    
    with tab3:
        create_stress_testing()
    
    with tab4:
        create_portfolio_monitoring()


if __name__ == "__main__":
    main()








