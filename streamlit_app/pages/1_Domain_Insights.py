"""
Domain Insights Page.

This page provides insights into different startup domains and their characteristics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
try:
    import yaml
except ModuleNotFoundError:
    import streamlit as st
    st.error('Module yaml is not installed. Please install it to use this page.')
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from utils.registry import get_all_domain_info, get_domain
from utils.helpers import format_percentage, format_currency
from simulation.scenario_engine import ScenarioEngine, ScenarioParameters
from simulation.domain_response import DomainResponseSimulator


def load_domain_config():
    """Load domain configuration from YAML file."""
    config_path = Path(__file__).parent.parent.parent / "config" / "domains.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_domain_overview():
    """Create domain overview section."""
    st.header("🏢 Domain Overview")
    
    # Load domain configuration
    config = load_domain_config()
    
    # Create domain summary
    domains_data = []
    for domain_key, domain_info in config['domains'].items():
        domains_data.append({
            'Domain': domain_info['name'],
            'Category': domain_info['category'],
            'Risk Profile': domain_info['risk_profile'],
            'Weight': domain_info['weight'],
            'Features': len(domain_info['features'])
        })
    
    df = pd.DataFrame(domains_data)
    
    # Display domain table
    st.subheader("Available Domains")
    st.dataframe(df)
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk profile distribution
        risk_counts = df['Risk Profile'].value_counts()
        fig_risk = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Risk Profile Distribution"
        )
        st.plotly_chart(fig_risk, width='stretch')
    
    with col2:
        # Category distribution
        category_counts = df['Category'].value_counts()
        fig_category = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            title="Domains by Category"
        )
        st.plotly_chart(fig_category, width='stretch')


def create_domain_details():
    """Create domain details section."""
    st.header("📊 Domain Details")
    
    # Load domain configuration
    config = load_domain_config()
    
    # Domain selector
    domain_keys = list(config['domains'].keys())
    selected_domain = st.selectbox(
        "Select Domain",
        domain_keys,
        format_func=lambda x: config['domains'][x]['name']
    )
    
    if selected_domain:
        domain_info = config['domains'][selected_domain]
        
        # Domain information
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Category", domain_info['category'].title())
        with col2:
            st.metric("Risk Profile", domain_info['risk_profile'].title())
        with col3:
            st.metric("Weight", f"{domain_info['weight']:.2f}")
        with col4:
            st.metric("Features", len(domain_info['features']))
        
        st.write(f"**Description:** {domain_info['description']}")
        
        # Features table
        st.subheader("Domain Features")
        features_data = []
        for feature_name, feature_info in domain_info['features'].items():
            features_data.append({
                'Feature': feature_name.replace('_', ' ').title(),
                'Description': feature_info['description'],
                'Type': feature_info['type'],
                'Default': str(feature_info['default'])
            })
        
        features_df = pd.DataFrame(features_data)
        st.dataframe(features_df)
        
        # Feature validation rules
        st.subheader("Feature Validation Rules")
        for feature_name, feature_info in domain_info['features'].items():
            if 'validation' in feature_info:
                with st.expander(f"Validation for {feature_name.replace('_', ' ').title()}"):
                    validation = feature_info['validation']
                    if 'min' in validation:
                        st.write(f"**Minimum:** {validation['min']}")
                    if 'max' in validation:
                        st.write(f"**Maximum:** {validation['max']}")


def create_domain_simulation():
    """Create domain simulation section."""
    st.header("🎯 Domain Simulation")
    
    # Load domain configuration
    config = load_domain_config()
    
    # Domain selector
    domain_keys = list(config['domains'].keys())
    selected_domain = st.selectbox(
        "Select Domain for Simulation",
        domain_keys,
        key="simulation_domain",
        format_func=lambda x: config['domains'][x]['name']
    )
    
    if selected_domain:
        domain_info = config['domains'][selected_domain]
        
        # Simulation parameters
        st.subheader("Simulation Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_iterations = st.slider(
                "Number of Iterations",
                min_value=100,
                max_value=10000,
                value=1000,
                step=100
            )
            
            time_horizon = st.slider(
                "Time Horizon (days)",
                min_value=30,
                max_value=730,
                value=365,
                step=30
            )
        
        with col2:
            seed = st.number_input(
                "Random Seed",
                min_value=1,
                max_value=10000,
                value=42
            )
            
            correlation_prob = st.slider(
                "Correlation Probability",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1
            )
        
        # Feature inputs
        st.subheader("Domain Features")
        features = {}
        
        for feature_name, feature_info in domain_info['features'].items():
            feature_type = feature_info['type']
            default_value = feature_info['default']
            
            if feature_type == 'float':
                if 'validation' in feature_info:
                    min_val = feature_info['validation']['min']
                    max_val = feature_info['validation']['max']
                    features[feature_name] = st.slider(
                        feature_name.replace('_', ' ').title(),
                        min_value=float(min_val),
                        max_value=float(max_val),
                        value=float(default_value),
                        help=feature_info['description']
                    )
                else:
                    features[feature_name] = st.number_input(
                        feature_name.replace('_', ' ').title(),
                        value=float(default_value),
                        help=feature_info['description']
                    )
            
            elif feature_type == 'int':
                if 'validation' in feature_info:
                    min_val = feature_info['validation']['min']
                    max_val = feature_info['validation']['max']
                    features[feature_name] = st.slider(
                        feature_name.replace('_', ' ').title(),
                        min_value=int(min_val),
                        max_value=int(max_val),
                        value=int(default_value),
                        help=feature_info['description']
                    )
                else:
                    features[feature_name] = st.number_input(
                        feature_name.replace('_', ' ').title(),
                        value=int(default_value),
                        step=1,
                        help=feature_info['description']
                    )
            
            elif feature_type == 'dict':
                st.write(f"**{feature_name.replace('_', ' ').title()}:** {default_value}")
                features[feature_name] = default_value
        
        # Run simulation
        if st.button("Run Simulation", type="primary"):
            with st.spinner("Running simulation..."):
                try:
                    # Create scenario parameters
                    params = ScenarioParameters(
                        name=f"Domain simulation for {selected_domain}",
                        description=f"Simulation for domain {selected_domain}",
                        domain_key=selected_domain,
                        num_iterations=num_iterations,
                        time_horizon_days=time_horizon,
                        seed=seed,
                        correlation_probability=correlation_prob
                    )
                    
                    # Run simulation
                    scenario_engine = ScenarioEngine()
                    result = scenario_engine.run_scenario(params)
                    
                    # Display results
                    st.subheader("Simulation Results")
                    
                    # Summary statistics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Iterations", result.num_iterations)
                    with col2:
                        st.metric("Time Horizon", f"{result.time_horizon_days} days")
                    with col3:
                        st.metric("Seed", result.seed)
                    
                    # Outcome metrics
                    if result.summary_stats:
                        st.subheader("Outcome Metrics")
                        
                        # Create metrics table
                        metrics_data = []
                        for metric, stats in result.summary_stats.items():
                            metrics_data.append({
                                'Metric': metric.replace('_', ' ').title(),
                                'Mean': f"{stats['mean']:.4f}",
                                'Std Dev': f"{stats['std']:.4f}",
                                'Min': f"{stats['min']:.4f}",
                                'Max': f"{stats['max']:.4f}",
                                'Median': f"{stats['median']:.4f}"
                            })
                        
                        metrics_df = pd.DataFrame(metrics_data)
                        st.dataframe(metrics_df, width='stretch')
                        
                        # Create distribution plots
                        st.subheader("Outcome Distributions")
                        
                        # Get sample results for plotting
                        sample_results = result.results[:100]  # Limit for performance
                        
                        if sample_results:
                            # Create subplots for each metric
                            metrics = list(result.summary_stats.keys())
                            num_metrics = len(metrics)
                            
                            if num_metrics > 0:
                                fig = make_subplots(
                                    rows=num_metrics,
                                    cols=1,
                                    subplot_titles=[m.replace('_', ' ').title() for m in metrics]
                                )
                                
                                for i, metric in enumerate(metrics, 1):
                                    values = [r.outcomes.get(metric, 0) for r in sample_results]
                                    
                                    fig.add_trace(
                                        go.Histogram(
                                            x=values,
                                            name=metric.replace('_', ' ').title(),
                                            showlegend=False
                                        ),
                                        row=i, col=1
                                    )
                                
                                fig.update_layout(height=200 * num_metrics)
                                st.plotly_chart(fig, width='stretch')
                    
                    # Percentiles
                    if result.percentiles:
                        st.subheader("Percentiles")
                        
                        percentiles_data = []
                        for metric, percs in result.percentiles.items():
                            percentiles_data.append({
                                'Metric': metric.replace('_', ' ').title(),
                                '5th': f"{percs[0]:.4f}",
                                '10th': f"{percs[1]:.4f}",
                                '25th': f"{percs[2]:.4f}",
                                '50th': f"{percs[3]:.4f}",
                                '75th': f"{percs[4]:.4f}",
                                '90th': f"{percs[5]:.4f}",
                                '95th': f"{percs[6]:.4f}"
                            })
                        
                        percentiles_df = pd.DataFrame(percentiles_data)
                        st.dataframe(percentiles_df, width='stretch')
                
                except Exception as e:
                    st.error(f"Simulation failed: {str(e)}")


def create_domain_comparison():
    """Create domain comparison section."""
    st.header("⚖️ Domain Comparison")
    
    # Load domain configuration
    config = load_domain_config()
    
    # Domain selector
    domain_keys = list(config['domains'].keys())
    selected_domains = st.multiselect(
        "Select Domains to Compare",
        domain_keys,
        default=domain_keys[:3],
        format_func=lambda x: config['domains'][x]['name']
    )
    
    if len(selected_domains) >= 2:
        # Comparison metrics
        comparison_data = []
        
        for domain_key in selected_domains:
            domain_info = config['domains'][domain_key]
            comparison_data.append({
                'Domain': domain_info['name'],
                'Category': domain_info['category'],
                'Risk Profile': domain_info['risk_profile'],
                'Weight': domain_info['weight'],
                'Features': len(domain_info['features'])
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Display comparison table
        st.subheader("Domain Comparison")
        st.dataframe(comparison_df)
        
        # Create comparison visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk profile comparison
            fig_risk = px.bar(
                comparison_df,
                x='Domain',
                y='Weight',
                color='Risk Profile',
                title="Domain Weights by Risk Profile"
            )
            st.plotly_chart(fig_risk, width='stretch')
        
        with col2:
            # Feature count comparison
            fig_features = px.bar(
                comparison_df,
                x='Domain',
                y='Features',
                title="Number of Features by Domain"
            )
            st.plotly_chart(fig_features, width='stretch')
        
        # Category analysis
        st.subheader("Category Analysis")
        category_counts = comparison_df['Category'].value_counts()
        fig_category = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Domains by Category"
        )
        st.plotly_chart(fig_category, width='stretch')


def main():
    """Main function for the Domain Insights page."""
    st.set_page_config(
        page_title="Domain Insights",
        page_icon="🏢",
        layout="wide"
    )
    
    st.title("🏢 Domain Insights")
    st.markdown("""
    This page provides comprehensive insights into different startup domains and their characteristics.
    Explore domain features, run simulations, and compare different domains.
    """)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview", "Details", "Simulation", "Comparison"
    ])
    
    with tab1:
        create_domain_overview()
    
    with tab2:
        create_domain_details()
    
    with tab3:
        create_domain_simulation()
    
    with tab4:
        create_domain_comparison()


if __name__ == "__main__":
    main()
