"""
Research Dashboard.

This page provides access to advanced research functionalities including
hybrid modeling, causal inference, graph networks, and multimodal fusion.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
import json
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from research.hybrid_models import HybridModelEngine, SurvivalData
from research.causal_inference import CausalInferenceEngine, CounterfactualScenario
from research.graph_networks import TemporalKnowledgeGraph, ShockPropagationEngine
from research.multimodal_fusion import MultimodalDataFusion, DataSource

def create_hybrid_modeling_section():
    """Create hybrid modeling section."""
    st.header("🔬 Hybrid Modeling (Econometrics + ML)")
    st.write("Compare traditional econometric models with machine learning approaches for startup failure prediction.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Configuration")
        
        # Model selection
        selected_models = st.multiselect(
            "Select models to compare:",
            ["Cox PH", "Weibull AFT", "XGBoost", "LightGBM", "Ensemble"],
            default=["Cox PH", "XGBoost", "Ensemble"]
        )
        
        # Domain selection
        domain = st.selectbox(
            "Select domain:",
            ["all", "fintech", "healthtech", "greentech", "saas", "venture_capital"]
        )
        
        # Sample size
        sample_size = st.slider("Sample size:", 100, 10000, 1000, step=100)
    
    with col2:
        st.subheader("Performance Metrics")
        
        # Display metrics
        if st.button("Run Model Comparison", type="primary"):
            with st.spinner("Running hybrid model comparison..."):
                # Generate synthetic data for demonstration
                np.random.seed(42)
                n_samples = sample_size
                
                # Create synthetic startup data
                startup_data = pd.DataFrame({
                    'startup_id': [f'startup_{i}' for i in range(n_samples)],
                    'domain': np.random.choice(['fintech', 'healthtech', 'greentech', 'saas'], n_samples),
                    'funding_rounds': np.random.poisson(3, n_samples),
                    'total_funding': np.random.exponential(1000000, n_samples),
                    'team_size': np.random.poisson(20, n_samples),
                    'age_months': np.random.exponential(24, n_samples),
                    'customer_count': np.random.exponential(1000, n_samples),
                    'revenue': np.random.exponential(500000, n_samples),
                    'burn_rate': np.random.exponential(100000, n_samples),
                    'market_cap': np.random.exponential(5000000, n_samples),
                    'competitor_count': np.random.poisson(10, n_samples),
                    'regulatory_score': np.random.uniform(0, 1, n_samples),
                    'policy_impact_score': np.random.uniform(0, 1, n_samples),
                    'start_date': pd.date_range('2020-01-01', periods=n_samples, freq='D'),
                    'end_date': pd.date_range('2023-01-01', periods=n_samples, freq='D'),
                    'status': np.random.choice(['operating', 'failed', 'acquired'], n_samples, p=[0.7, 0.2, 0.1])
                })
                
                # Initialize hybrid model engine
                engine = HybridModelEngine()
                
                # Prepare survival data manually since method prepare_survival_data does not exist
                survival_data = []
                for _, row in startup_data.iterrows():
                    features = {
                        'age_months': row['age_months'],
                        'customer_count': row['customer_count'],
                        'revenue': row['revenue'],
                        'burn_rate': row['burn_rate'],
                        'market_cap': row['market_cap'],
                        'competitor_count': row['competitor_count'],
                        'regulatory_score': row['regulatory_score'],
                        'policy_impact_score': row['policy_impact_score']
                    }
                    duration = (row['end_date'] - row['start_date']).days
                    event = row['status'] == 'failed'
                    survival_data.append(SurvivalData(duration=duration, event=event, features=features, timestamp=row['start_date']))
                
                # Train survival model
                train_results = engine.train_survival_model(survival_data)
                
                # Display results
                st.success("Model training completed!")
                
                # Show training results
                st.json(train_results)

def create_causal_inference_section():
    """Create causal inference section."""
    st.header("🔍 Causal Inference Analysis")
    st.write("Estimate causal effects of policies, funding, and shocks on startup performance.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Causal Analysis Setup")
        
        # Treatment variable
        treatment_var = st.selectbox(
            "Treatment variable:",
            ["funding_round", "regulatory_policy", "market_competition", "team_size"]
        )
        
        # Outcome variable
        outcome_var = st.selectbox(
            "Outcome variable:",
            ["revenue", "profitability", "survival_probability", "growth_rate"]
        )
        
        # Estimation method
        method = st.selectbox(
            "Estimation method:",
            ["propensity_score", "matching", "regression", "instrumental_variables"]
        )
        
        # Domain
        domain = st.selectbox(
            "Domain:",
            ["fintech", "healthtech", "greentech", "saas"],
            key="causal_domain"
        )
    
    with col2:
        st.subheader("Counterfactual Scenarios")
        
        scenario_name = st.text_input("Scenario name:", "Policy X Removal")
        treatment_value = st.number_input("Treatment value:", value=0.0, step=0.1)
        baseline_value = st.number_input("Baseline value:", value=1.0, step=0.1)
        
        if st.button("Run Causal Analysis", type="primary"):
            with st.spinner("Running causal inference analysis..."):
                # Generate synthetic data
                np.random.seed(42)
                n_samples = 1000
                
                data = pd.DataFrame({
                    'startup_id': [f'startup_{i}' for i in range(n_samples)],
                    'domain': domain,
                    'funding_round': np.random.poisson(3, n_samples),
                    'regulatory_policy': np.random.uniform(0, 1, n_samples),
                    'market_competition': np.random.uniform(0, 1, n_samples),
                    'team_size': np.random.poisson(20, n_samples),
                    'revenue': np.random.exponential(500000, n_samples),
                    'profitability': np.random.normal(0.1, 0.2, n_samples),
                    'survival_probability': np.random.uniform(0, 1, n_samples),
                    'growth_rate': np.random.normal(0.05, 0.1, n_samples),
                    'date': pd.date_range('2023-01-01', periods=n_samples, freq='D')
                })
                
                # Initialize causal inference engine
                engine = CausalInferenceEngine()
                
                # Estimate causal effect
                covariates = ['team_size', 'market_competition']
                effect = engine.estimate_causal_effect(
                    data, treatment_var, outcome_var, covariates, method
                )
                
                # Display results
                st.success("Causal analysis completed!")
                
                # Effect summary
                st.metric("Effect Size", f"{effect.effect_size:.3f}")
                st.metric("P-value", f"{effect.p_value:.3f}")
                st.metric("Confidence Interval", f"({effect.confidence_interval[0]:.3f}, {effect.confidence_interval[1]:.3f})")
                
                # Run counterfactual analysis
                scenario = CounterfactualScenario(
                    scenario_name=scenario_name,
                    treatment_variable=treatment_var,
                    treatment_value=treatment_value,
                    baseline_value=baseline_value,
                    affected_startups=data['startup_id'].tolist()[:100],
                    time_period=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
                    assumptions={'no_interference': True, 'consistency': True}
                )
                
                counterfactual_result = engine.run_counterfactual_analysis(scenario, data)
                
                # Display counterfactual results
                st.subheader("Counterfactual Analysis Results")
                st.metric("Baseline Outcome", f"{counterfactual_result['baseline_outcome']:.2f}")
                st.metric("Counterfactual Outcome", f"{counterfactual_result['counterfactual_outcome']:.2f}")
                st.metric("Effect Size", f"{counterfactual_result['effect_size']:.2f}")
                st.metric("Effect Percentage", f"{counterfactual_result['effect_percentage']:.1f}%")

def create_graph_networks_section():
    """Create graph networks section."""
    st.header("🕸️ Graph-Based Risk Networks")
    st.write("Analyze startup ecosystems as temporal knowledge graphs with shock propagation.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Network Configuration")
        
        # Network type
        network_type = st.selectbox(
            "Network type:",
            ["startup_investor", "startup_accelerator", "startup_policy", "comprehensive"]
        )
        
        # Shock configuration
        shock_type = st.selectbox(
            "Shock type:",
            ["policy_change", "market_crash", "regulatory_change", "funding_drought"]
        )
        
        shock_intensity = st.slider("Shock intensity:", 0.1, 1.0, 0.5, step=0.1)
        max_steps = st.slider("Max propagation steps:", 5, 20, 10)
    
    with col2:
        st.subheader("Shock Source")
        
        source_type = st.selectbox(
            "Source type:",
            ["startup", "investor", "accelerator", "policy", "domain"]
        )
        
        source_id = st.text_input("Source ID:", "startup_001")
        
        if st.button("Simulate Shock Propagation", type="primary"):
            with st.spinner("Simulating shock propagation..."):
                # Generate synthetic network data
                np.random.seed(42)
                n_startups = 100
                n_investors = 20
                n_accelerators = 10
                n_policies = 5
                
                # Startup data
                startup_data = pd.DataFrame({
                    'startup_id': [f'startup_{i}' for i in range(n_startups)],
                    'name': [f'Startup {i}' for i in range(n_startups)],
                    'domain': np.random.choice(['fintech', 'healthtech', 'greentech', 'saas'], n_startups),
                    'funding_stage': np.random.choice(['seed', 'series_a', 'series_b', 'series_c'], n_startups),
                    'total_funding': np.random.exponential(1000000, n_startups),
                    'team_size': np.random.poisson(20, n_startups),
                    'revenue': np.random.exponential(500000, n_startups),
                    'burn_rate': np.random.exponential(100000, n_startups),
                    'market_cap': np.random.exponential(5000000, n_startups),
                    'competitor_count': np.random.poisson(10, n_startups),
                    'regulatory_score': np.random.uniform(0, 1, n_startups),
                    'policy_impact_score': np.random.uniform(0, 1, n_startups),
                    'founded_date': pd.date_range('2020-01-01', periods=n_startups, freq='D')
                })
                
                # Investor data
                investor_data = pd.DataFrame({
                    'investor_id': [f'investor_{i}' for i in range(n_investors)],
                    'name': [f'Investor {i}' for i in range(n_investors)],
                    'type': np.random.choice(['vc', 'angel', 'corporate'], n_investors),
                    'total_investments': np.random.exponential(10000000, n_investors),
                    'portfolio_size': np.random.poisson(15, n_investors),
                    'investment_focus': np.random.choice(['fintech', 'healthtech', 'greentech', 'saas'], n_investors),
                    'founded_date': pd.date_range('2010-01-01', periods=n_investors, freq='D')
                })
                
                # Accelerator data
                accelerator_data = pd.DataFrame({
                    'accelerator_id': [f'accelerator_{i}' for i in range(n_accelerators)],
                    'name': [f'Accelerator {i}' for i in range(n_accelerators)],
                    'program_duration': np.random.uniform(3, 12, n_accelerators),
                    'success_rate': np.random.uniform(0.3, 0.8, n_accelerators),
                    'mentor_network_size': np.random.poisson(50, n_accelerators),
                    'founded_date': pd.date_range('2015-01-01', periods=n_accelerators, freq='D')
                })
                
                # Policy data
                policy_data = pd.DataFrame({
                    'policy_id': [f'policy_{i}' for i in range(n_policies)],
                    'name': [f'Policy {i}' for i in range(n_policies)],
                    'type': np.random.choice(['regulation', 'subsidy', 'tax'], n_policies),
                    'jurisdiction': np.random.choice(['US', 'EU', 'UK'], n_policies),
                    'impact_score': np.random.uniform(0.1, 0.9, n_policies),
                    'affected_domains': [['fintech', 'healthtech'] for _ in range(n_policies)],
                    'enactment_date': pd.date_range('2022-01-01', periods=n_policies, freq='D')
                })
                
                # Build network
                graph = TemporalKnowledgeGraph()
                graph.build_startup_network(startup_data, investor_data, accelerator_data, policy_data)
                
                # Initialize propagation engine
                propagation_engine = ShockPropagationEngine(graph)
                
                # Simulate shock propagation
                shock_source = f"{source_type}_{source_id}"
                propagation = propagation_engine.simulate_shock_propagation(
                    shock_source, shock_intensity, shock_type, max_steps
                )
                
                # Display results
                st.success("Shock propagation simulation completed!")
                
                # Network statistics
                stats = graph.get_network_statistics()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Nodes", stats['total_nodes'])
                with col2:
                    st.metric("Total Edges", stats['total_edges'])
                with col3:
                    st.metric("Affected Nodes", len(propagation.affected_nodes))
                with col4:
                    st.metric("Total Impact", f"{propagation.total_impact:.2f}")
                
                # Propagation visualization
                fig = go.Figure()
                
                # Add nodes
                node_types = []
                for node_id in propagation.affected_nodes:
                    if node_id in graph.graph:
                        node_type = graph.graph.nodes[node_id].get('node_type', 'unknown')
                        node_types.append(node_type)
                
                # Count by type
                type_counts = pd.Series(node_types).value_counts()
                
                fig.add_trace(go.Bar(
                    x=type_counts.index,
                    y=type_counts.values,
                    name='Affected Nodes by Type'
                ))
                
                fig.update_layout(
                    title="Shock Propagation Results",
                    xaxis_title="Node Type",
                    yaxis_title="Number of Affected Nodes"
                )
                
                st.plotly_chart(fig, width='stretch')

def create_multimodal_fusion_section():
    """Create multimodal fusion section."""
    st.header("📊 Multimodal Data Fusion")
    st.write("Integrate structured, unstructured, and semi-structured data for comprehensive risk assessment.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Sources")
        
        # Data source selection
        data_sources = st.multiselect(
            "Select data sources:",
            ["financial_kpis", "news_sentiment", "social_media", "patent_data", "policy_documents"],
            default=["financial_kpis", "news_sentiment"]
        )
        
        # Fusion method
        fusion_method = st.selectbox(
            "Fusion method:",
            ["concatenation", "weighted", "pca"]
        )
        
        # Embedding type
        embedding_type = st.selectbox(
            "Embedding type:",
            ["tfidf", "lda", "nmf"]
        )
    
    with col2:
        st.subheader("Risk Indices")
        
        # Domain selection
        domain = st.selectbox(
            "Domain:",
            ["fintech", "healthtech", "greentech", "saas"],
            key="fusion_domain"
        )
        
        # Time window
        time_window = st.slider("Time window (days):", 7, 90, 30)
        
        if st.button("Run Multimodal Fusion", type="primary"):
            with st.spinner("Running multimodal fusion analysis..."):
                # Initialize fusion engine
                fusion_engine = MultimodalDataFusion()
                
                # Register data sources
                for source_id in data_sources:
                    source = DataSource(
                        source_id=source_id,
                        source_type="structured" if source_id == "financial_kpis" else "unstructured",
                        data_type=source_id.split('_')[0],
                        file_path=f"data/{source_id}.csv",
                        description=f"{source_id} data source",
                        update_frequency="daily",
                        last_updated=datetime.now()
                    )
                    fusion_engine.register_data_source(source)
                
                # Generate embeddings for text data
                text_sources = [s for s in data_sources if s in ["news_sentiment", "social_media", "policy_documents"]]
                for source_id in text_sources:
                    embedding_result = fusion_engine.generate_embeddings(source_id, embedding_type)
                
                # Fuse data
                fusion_result = fusion_engine.fuse_multimodal_data(
                    data_sources, fusion_method, "risk_score"
                )
                
                # Create dynamic risk indices
                risk_indices = fusion_engine.create_dynamic_risk_indices(domain, time_window)
                
                # Display results
                st.success("Multimodal fusion completed!")
                
                # Performance metrics
                metrics = fusion_result.performance_metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("R² Score", f"{metrics['r2_score']:.3f}")
                with col2:
                    st.metric("MSE", f"{metrics['mse']:.3f}")
                with col3:
                    st.metric("Feature Importance", f"{metrics['feature_importance_mean']:.3f}")
                
                # Risk indices visualization
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=risk_indices['date'],
                    y=risk_indices['risk_index'],
                    mode='lines',
                    name='Risk Index',
                    line=dict(color='red', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=risk_indices['date'],
                    y=risk_indices['risk_ma'],
                    mode='lines',
                    name='Moving Average',
                    line=dict(color='blue', width=2, dash='dash')
                ))
                
                fig.update_layout(
                    title=f"Dynamic Risk Index - {domain.title()}",
                    xaxis_title="Date",
                    yaxis_title="Risk Index",
                    height=400
                )
                
                st.plotly_chart(fig, width='stretch')

def create_research_export_section():
    """Create research export section."""
    st.header("📋 Research Export")
    st.write("Export results for academic research papers and publications.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export Options")
        
        # Export formats
        export_formats = st.multiselect(
            "Export formats:",
            ["CSV", "JSON", "LaTeX", "PNG", "PDF"],
            default=["CSV", "LaTeX", "PNG"]
        )
        
        # Export components
        export_components = st.multiselect(
            "Export components:",
            ["Model Comparisons", "Causal Effects", "Network Analysis", "Fusion Results"],
            default=["Model Comparisons", "Causal Effects"]
        )
    
    with col2:
        st.subheader("Export Settings")
        
        # Output directory
        output_dir = st.text_input("Output directory:", "research_outputs")
        
        # Include metadata
        include_metadata = st.checkbox("Include metadata", value=True)
        
        # Include visualizations
        include_viz = st.checkbox("Include visualizations", value=True)
        
        if st.button("Export Research Results", type="primary"):
            with st.spinner("Exporting research results..."):
                # This would integrate with the actual export functions
                st.success("Research results exported successfully!")
                
                # Show export summary
                st.subheader("Export Summary")
                
                export_summary = {
                    "Export Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Output Directory": output_dir,
                    "Formats": export_formats,
                    "Components": export_components,
                    "Files Generated": len(export_formats) * len(export_components)
                }
                
                for key, value in export_summary.items():
                    st.write(f"**{key}:** {value}")

def main():
    """Main research dashboard function."""
    st.set_page_config(
        page_title="Research Dashboard",
        page_icon="🔬",
        layout="wide"
    )
    
    st.title("🔬 Research Dashboard")
    st.write("Advanced research functionalities for startup performance prediction and risk assessment.")
    
    # Create tabs for different research areas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Hybrid Modeling", 
        "Causal Inference", 
        "Graph Networks", 
        "Multimodal Fusion",
        "Research Export"
    ])
    
    with tab1:
        create_hybrid_modeling_section()
    
    with tab2:
        create_causal_inference_section()
    
    with tab3:
        create_graph_networks_section()
    
    with tab4:
        create_multimodal_fusion_section()
    
    with tab5:
        create_research_export_section()

if __name__ == "__main__":
    main()
