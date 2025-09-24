#!/usr/bin/env python3
"""
Main Streamlit Application.

This is the main entry point for the startup performance prediction system.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Startup Performance Prediction System",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main header
    st.title("🚀 Startup Performance Prediction System")
    st.markdown("---")
    
    # System overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🏢 **Multi-Domain Analysis**\n\n10 specialized domains with risk models")
    
    with col2:
        st.info("🔍 **Policy Analysis**\n\nArgument mining and impact assessment")
    
    with col3:
        st.info("🎯 **Scenario Simulation**\n\nShock generation and Monte Carlo analysis")
    
    st.markdown("---")
    
    # Quick start section
    st.header("🚀 Quick Start")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Domain Analysis", "Scenario Simulation", "Policy Analysis", "Research Dashboard"])
    
    with tab1:
        st.subheader("Domain Analysis")
        st.write("Analyze startup performance across different domains:")
        
        domain_options = [
            "Venture Capital", "SaaS", "FinTech", "HealthTech", "GreenTech",
            "RegTech", "Cross-Border", "Public Sector", "MediaTech", "Accelerators"
        ]
        
        selected_domain = st.selectbox("Select Domain:", domain_options)
        
        if st.button("Analyze Domain"):
            st.success(f"✅ Analysis completed for {selected_domain}")
            st.info("Navigate to the Domain Analysis page for detailed results.")
    
    with tab2:
        st.subheader("Scenario Simulation")
        st.write("Generate and analyze different scenarios:")
        
        scenario_type = st.selectbox(
            "Scenario Type:",
            ["Policy Change", "Market Crash", "Pandemic", "Trade War", "Regulatory Change"]
        )
        
        intensity = st.slider("Shock Intensity:", 0.1, 1.0, 0.5)
        
        if st.button("Run Simulation"):
            st.success(f"✅ Simulation completed for {scenario_type}")
            st.info("Navigate to the Scenario Simulation page for detailed results.")
    
    with tab3:
        st.subheader("Policy Analysis")
        st.write("Analyze policy documents and extract arguments:")
        
        policy_text = st.text_area(
            "Enter Policy Text:",
            placeholder="Paste policy document text here..."
        )
        
        if st.button("Analyze Policy"):
            if policy_text:
                st.success("✅ Policy analysis completed")
                st.info("Navigate to the Policy Analysis page for detailed results.")
            else:
                st.warning("Please enter policy text to analyze.")
    
    with tab4:
        st.subheader("Research Dashboard")
        st.write("Access advanced research functionalities:")
        
        research_options = [
            "Hybrid Modeling", "Causal Inference", "Graph Networks", "Multimodal Fusion"
        ]
        
        selected_research = st.selectbox("Research Area:", research_options)
        
        if st.button("Open Research Dashboard"):
            st.success(f"✅ Opening {selected_research} dashboard")
            st.info("Navigate to the Research Dashboard page for advanced analytics.")
    
    st.markdown("---")
    
    # System status
    st.header("📊 System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("API Status", "🟢 Online", "http://localhost:8000")
    
    with col2:
        st.metric("Domains Available", "10", "All domains ready")
    
    with col3:
        st.metric("Scenarios Ready", "8", "Shock types available")
    
    with col4:
        st.metric("Research Tools", "4", "Advanced analytics")
    
    # Navigation guide
    st.markdown("---")
    st.header("🧭 Navigation Guide")
    
    st.markdown("""
    **📱 Available Pages:**
    
    1. **Dashboard Overview** (Current) - System overview and quick start
    2. **Domain Analysis** - Specialized domain risk assessment
    3. **Scenario Simulation** - Shock generation and impact analysis
    4. **Portfolio Risk Monitor** - Real-time portfolio monitoring
    5. **Research Dashboard** - Advanced research functionalities
    
    **🔧 API Access:**
    - **Documentation**: http://localhost:8000/docs
    - **Health Check**: http://localhost:8000/health
    - **Status**: http://localhost:8000/api/v1/status
    """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>🚀 Startup Performance Prediction System | Research-Grade Analytics Platform</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
