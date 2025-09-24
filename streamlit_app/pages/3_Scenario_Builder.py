"""
Scenario Builder Page.

This page provides tools for building and running scenario simulations.
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

from simulation.scenario_engine import ScenarioEngine, ScenarioParameters
from simulation.shocks import ShockGenerator
from utils.registry import get_domain, list_domain_keys


def create_scenario_builder():
    """Create scenario builder section."""
    st.header("🏗️ Scenario Builder")
    
    # Scenario configuration
    st.subheader("Scenario Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scenario_name = st.text_input("Scenario Name", "Custom Scenario")
        scenario_description = st.text_area("Scenario Description", "A custom scenario simulation")
        
        # Domain selection
        domain_keys = list_domain_keys()
        selected_domain = st.selectbox("Select Domain", domain_keys)
    
    with col2:
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
        
        seed = st.number_input("Random Seed", value=42, min_value=1, max_value=10000)
    
    # Shock configuration
    st.subheader("Shock Configuration")
    
    shock_generator = ShockGenerator()
    available_shock_types = list(shock_generator.shock_types.keys())
    
    col1, col2 = st.columns(2)
    
    with col1:
        shock_types = st.multiselect(
            "Shock Types",
            available_shock_types,
            default=available_shock_types[:3]
        )
        
        jurisdictions = st.multiselect(
            "Jurisdictions",
            ["US", "EU", "UK", "JP", "CA", "CN"],
            default=["US", "EU"]
        )
    
    with col2:
        correlation_prob = st.slider(
            "Correlation Probability",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1
        )
        
        num_shocks = st.slider(
            "Number of Shocks",
            min_value=1,
            max_value=10,
            value=3,
            step=1
        )
    
    # Custom shocks
    st.subheader("Custom Shocks (Optional)")
    
    use_custom_shocks = st.checkbox("Use custom shocks instead of generated ones")
    
    if use_custom_shocks:
        num_custom_shocks = st.number_input("Number of custom shocks", min_value=1, max_value=10, value=3)
        
        custom_shocks = []
        for i in range(num_custom_shocks):
            with st.expander(f"Custom Shock {i+1}"):
                shock_type = st.selectbox(f"Shock Type {i+1}", available_shock_types, key=f"custom_shock_{i}")
                jurisdiction = st.selectbox(f"Jurisdiction {i+1}", ["US", "EU", "UK", "JP", "CA", "CN"], key=f"custom_jurisdiction_{i}")
                intensity = st.slider(f"Intensity {i+1}", 0.0, 1.0, 0.5, key=f"custom_intensity_{i}")
                duration = st.slider(f"Duration (days) {i+1}", 1, 365, 90, key=f"custom_duration_{i}")
                confidence = st.slider(f"Confidence {i+1}", 0.0, 1.0, 0.8, key=f"custom_confidence_{i}")
                
                custom_shocks.append({
                    "type": shock_type,
                    "jurisdiction": jurisdiction,
                    "intensity": intensity,
                    "duration_days": duration,
                    "confidence": confidence
                })
    
    # Run scenario
    if st.button("Run Scenario", type="primary"):
        with st.spinner("Running scenario simulation..."):
            try:
                # Create scenario parameters
                params = ScenarioParameters(
                    name=scenario_name,
                    description=scenario_description,
                    domain_key=selected_domain,
                    num_iterations=num_iterations,
                    time_horizon_days=time_horizon,
                    seed=seed,
                    shock_types=shock_types if not use_custom_shocks else None,
                    jurisdictions=jurisdictions if not use_custom_shocks else None,
                    correlation_probability=correlation_prob
                )
                
                # Run scenario
                scenario_engine = ScenarioEngine()
                result = scenario_engine.run_scenario(params)
                
                # Store result in session state
                st.session_state['scenario_result'] = result
                st.session_state['scenario_params'] = params
                
                st.success("Scenario completed successfully!")
                
            except Exception as e:
                st.error(f"Scenario failed: {str(e)}")


def create_predefined_scenarios():
    """Create predefined scenarios section."""
    st.header("📋 Predefined Scenarios")
    
    # Available predefined scenarios
    predefined_scenarios = {
        "recession": "Economic recession scenario with market crash and policy rate changes",
        "tech_regulation": "Technology regulation scenario with regulatory changes and cybersecurity breaches",
        "trade_conflict": "Trade conflict scenario with trade wars and political instability",
        "climate_crisis": "Climate crisis scenario with extreme weather and regulatory changes",
        "pandemic_response": "Pandemic response scenario with public health emergency and policy changes"
    }
    
    selected_scenario = st.selectbox(
        "Select Predefined Scenario",
        list(predefined_scenarios.keys()),
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    if selected_scenario:
        st.write(f"**Description:** {predefined_scenarios[selected_scenario]}")
        
        # Scenario parameters
        col1, col2 = st.columns(2)
        
        with col1:
            domain_keys = list_domain_keys()
            scenario_domain = st.selectbox("Domain", domain_keys, key="predefined_domain")
            
            scenario_iterations = st.slider(
                "Iterations",
                min_value=100,
                max_value=10000,
                value=1000,
                step=100,
                key="predefined_iterations"
            )
        
        with col2:
            scenario_horizon = st.slider(
                "Time Horizon (days)",
                min_value=30,
                max_value=730,
                value=365,
                step=30,
                key="predefined_horizon"
            )
            
            scenario_seed = st.number_input(
                "Seed",
                value=42,
                min_value=1,
                max_value=10000,
                key="predefined_seed"
            )
        
        if st.button("Run Predefined Scenario", type="primary"):
            with st.spinner(f"Running {selected_scenario} scenario..."):
                try:
                    shock_generator = ShockGenerator()
                    shocks = shock_generator.generate_scenario_shocks(selected_scenario)
                    
                    params = ScenarioParameters(
                        name=f"Predefined: {selected_scenario}",
                        description=predefined_scenarios[selected_scenario],
                        domain_key=scenario_domain,
                        num_iterations=scenario_iterations,
                        time_horizon_days=scenario_horizon,
                        seed=scenario_seed,
                        custom_shocks=shocks
                    )
                    
                    scenario_engine = ScenarioEngine()
                    result = scenario_engine.run_scenario(params)
                    
                    st.session_state['scenario_result'] = result
                    st.session_state['scenario_params'] = params
                    
                    st.success("Predefined scenario completed successfully!")
                    
                except Exception as e:
                    st.error(f"Predefined scenario failed: {str(e)}")


def create_scenario_results():
    """Create scenario results section."""
    st.header("📊 Scenario Results")
    
    if 'scenario_result' not in st.session_state:
        st.info("Run a scenario first to see results.")
        return
    
    result = st.session_state['scenario_result']
    params = st.session_state['scenario_params']
    
    # Scenario summary
    st.subheader("Scenario Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Scenario Name", result.scenario_name)
    with col2:
        st.metric("Domain", result.domain_key)
    with col3:
        st.metric("Iterations", result.num_iterations)
    with col4:
        st.metric("Time Horizon", f"{result.time_horizon_days} days")
    
    # Summary statistics
    if result.summary_stats:
        st.subheader("Summary Statistics")
        
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
    
    # Shocks analysis
    if result.results:
        st.subheader("Shocks Analysis")
        
        # Aggregate shocks from all iterations
        all_shocks = []
        for res in result.results:
            all_shocks.extend(res.shocks)
        
        if all_shocks:
            # Shock types distribution
            shock_types = [s.type for s in all_shocks]
            type_counts = pd.Series(shock_types).value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_types = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Shock Types Distribution"
                )
                st.plotly_chart(fig_types, width='stretch')
            
            with col2:
                # Shock intensity distribution
                intensities = [s.intensity for s in all_shocks]
                fig_intensity = px.histogram(
                    x=intensities,
                    title="Shock Intensity Distribution",
                    nbins=20
                )
                st.plotly_chart(fig_intensity, width='stretch')
            
            # Shock statistics
            shock_stats = {
                'Total Shocks': len(all_shocks),
                'Avg Intensity': f"{sum(s.intensity for s in all_shocks) / len(all_shocks):.3f}",
                'Avg Duration': f"{sum(s.duration_days for s in all_shocks) / len(all_shocks):.1f} days",
                'Avg Confidence': f"{sum(s.confidence for s in all_shocks) / len(all_shocks):.3f}"
            }
            
            col1, col2, col3, col4 = st.columns(4)
            for i, (key, value) in enumerate(shock_stats.items()):
                with [col1, col2, col3, col4][i]:
                    st.metric(key, value)


def create_what_if_analysis():
    """Create what-if analysis section."""
    st.header("🤔 What-If Analysis")
    
    if 'scenario_result' not in st.session_state:
        st.info("Run a base scenario first to perform what-if analysis.")
        return
    
    base_result = st.session_state['scenario_result']
    
    st.subheader("What-If Modifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        intensity_multiplier = st.slider(
            "Intensity Multiplier",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        duration_multiplier = st.slider(
            "Duration Multiplier",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
    
    with col2:
        correlation_multiplier = st.slider(
            "Correlation Multiplier",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        additional_shocks = st.number_input(
            "Additional Shocks",
            min_value=0,
            max_value=5,
            value=0,
            step=1
        )
    
    if st.button("Run What-If Analysis", type="primary"):
        with st.spinner("Running what-if analysis..."):
            try:
                what_if_params = {
                    'intensity_multiplier': intensity_multiplier,
                    'duration_multiplier': duration_multiplier,
                    'correlation_multiplier': correlation_multiplier,
                    'additional_shocks': additional_shocks
                }
                
                scenario_engine = ScenarioEngine()
                what_if_result = scenario_engine.run_what_if_analysis(base_result, what_if_params)
                
                st.session_state['what_if_result'] = what_if_result
                
                st.success("What-if analysis completed successfully!")
                
            except Exception as e:
                st.error(f"What-if analysis failed: {str(e)}")
    
    # What-if results comparison
    if 'what_if_result' in st.session_state:
        st.subheader("What-If Results Comparison")
        
        what_if_result = st.session_state['what_if_result']
        
        # Compare key metrics
        comparison_data = []
        
        for metric in base_result.summary_stats.keys():
            if metric in what_if_result.summary_stats:
                base_mean = base_result.summary_stats[metric]['mean']
                what_if_mean = what_if_result.summary_stats[metric]['mean']
                
                comparison_data.append({
                    'Metric': metric.replace('_', ' ').title(),
                    'Base Scenario': f"{base_mean:.4f}",
                    'What-If Scenario': f"{what_if_mean:.4f}",
                    'Difference': f"{what_if_mean - base_mean:.4f}",
                    'Change %': f"{((what_if_mean - base_mean) / base_mean * 100):.1f}%" if base_mean != 0 else "N/A"
                })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, width='stretch')
            
            # Create comparison chart
            fig = go.Figure()
            
            metrics = [row['Metric'] for row in comparison_data]
            base_values = [float(row['Base Scenario']) for row in comparison_data]
            what_if_values = [float(row['What-If Scenario']) for row in comparison_data]
            
            fig.add_trace(go.Bar(
                name='Base Scenario',
                x=metrics,
                y=base_values,
                marker_color='blue'
            ))
            
            fig.add_trace(go.Bar(
                name='What-If Scenario',
                x=metrics,
                y=what_if_values,
                marker_color='red'
            ))
            
            fig.update_layout(
                title="Scenario Comparison",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, width='stretch')


def main():
    """Main function for the Scenario Builder page."""
    st.set_page_config(
        page_title="Scenario Builder",
        page_icon="🏗️",
        layout="wide"
    )
    
    st.title("🏗️ Scenario Builder")
    st.markdown("""
    This page provides tools for building and running scenario simulations.
    Create custom scenarios, run predefined scenarios, and perform what-if analysis.
    """)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Custom Scenarios", "Predefined Scenarios", "Results", "What-If Analysis"
    ])
    
    with tab1:
        create_scenario_builder()
    
    with tab2:
        create_predefined_scenarios()
    
    with tab3:
        create_scenario_results()
    
    with tab4:
        create_what_if_analysis()


if __name__ == "__main__":
    main()








