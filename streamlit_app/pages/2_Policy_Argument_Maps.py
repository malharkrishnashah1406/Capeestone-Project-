"""
Policy Argument Maps Page.

This page provides visualization and analysis of policy arguments and debate structures.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
try:
    import networkx as nx
except ModuleNotFoundError:
    nx = None
    import streamlit as st
    st.error('Module networkx is not installed. Please install it to use this page.')
from pathlib import Path
import sys
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from policy_argument_mining import (
    PolicyIngestion, PolicyPreprocessor, PolicySegmenter,
    ClaimDetector, StanceDetector, ArgumentRoleLabeler,
    FrameMiner, EntityLinker, ArgumentGraph, ArgumentScorer
)


def create_argument_analysis():
    """Create argument analysis section."""
    st.header("🔍 Argument Analysis")
    
    # Text input for analysis
    st.subheader("Analyze Policy Text")
    
    # Sample text or user input
    sample_texts = {
        "Sample 1": """
        The proposed regulation will increase compliance costs for small businesses by 15-20%. 
        Industry analysis shows that this burden will disproportionately affect startups and 
        could stifle innovation in the fintech sector. However, consumer advocacy groups 
        argue that the regulation is necessary to protect consumers from predatory practices.
        """,
        "Sample 2": """
        Climate change regulations must be implemented immediately to prevent catastrophic 
        environmental damage. The scientific consensus is clear that immediate action is 
        required. However, some industry representatives claim that rapid implementation 
        will cause economic disruption and job losses.
        """,
        "Custom": ""
    }
    
    selected_sample = st.selectbox("Choose sample text or enter custom:", list(sample_texts.keys()))
    
    if selected_sample == "Custom":
        text_input = st.text_area("Enter policy text for analysis:", height=200)
    else:
        text_input = st.text_area("Policy text:", value=sample_texts[selected_sample], height=200)
    
    if st.button("Analyze Arguments", type="primary") and text_input.strip():
        with st.spinner("Analyzing arguments..."):
            try:
                # Initialize analysis pipeline
                preprocessor = PolicyPreprocessor()
                segmenter = PolicySegmenter()
                claim_detector = ClaimDetector()
                stance_detector = StanceDetector()
                role_labeler = ArgumentRoleLabeler()
                frame_miner = FrameMiner()
                entity_linker = EntityLinker()
                scorer = ArgumentScorer()
                
                # Preprocess text
                preprocessed_text = preprocessor.preprocess_segment(text_input)
                
                # Segment text
                segments = segmenter.segment_text(preprocessed_text)
                
                # Detect claims
                claims = claim_detector.detect_claims(segments)
                
                # Detect stances
                stances = stance_detector.detect_stances_from_claims(claims)
                
                # Label argument roles
                roles = role_labeler.label_claim_roles(claims)
                
                # Detect frames
                frames = frame_miner.detect_frames_from_claims(claims)
                
                # Extract entities
                entities = entity_linker.extract_entities_from_claims(claims)
                
                # Score arguments
                scored_claims = []
                for claim in claims:
                    score = scorer.score_claim(claim)
                    scored_claims.append({
                        "claim": claim.claim_text,
                        "evidence": claim.evidence_text,
                        "claim_type": claim.claim_type,
                        "salience": score.salience,
                        "credibility": score.credibility,
                        "uncertainty": score.uncertainty
                    })
                
                # Display results
                st.subheader("Analysis Results")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Claims Detected", len(claims))
                with col2:
                    st.metric("Stances Identified", len(stances))
                with col3:
                    st.metric("Frames Found", len(frames))
                with col4:
                    st.metric("Entities Extracted", len(entities))
                
                # Claims table
                if scored_claims:
                    st.subheader("Detected Claims")
                    claims_df = pd.DataFrame(scored_claims)
                    st.dataframe(claims_df, width='stretch')
                    
                    # Claims visualization
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Claim types distribution
                        claim_types = [c['claim_type'] for c in scored_claims]
                        type_counts = pd.Series(claim_types).value_counts()
                        fig_types = px.pie(
                            values=type_counts.values,
                            names=type_counts.index,
                            title="Claim Types Distribution"
                        )
                        st.plotly_chart(fig_types, width='stretch')
                    
                    with col2:
                        # Salience vs Credibility scatter
                        fig_scatter = px.scatter(
                            claims_df,
                            x='salience',
                            y='credibility',
                            size='uncertainty',
                            hover_data=['claim'],
                            title="Claims: Salience vs Credibility"
                        )
                        st.plotly_chart(fig_scatter, width='stretch')
                
                # Stances analysis
                if stances:
                    st.subheader("Stance Analysis")
                    stances_data = []
                    for stance in stances:
                        stances_data.append({
                            'Target': stance.stance_target,
                            'Label': stance.stance_label,
                            'Confidence': stance.confidence,
                            'Evidence': stance.evidence_text
                        })
                    
                    stances_df = pd.DataFrame(stances_data)
                    st.dataframe(stances_df, width='stretch')
                    
                    # Stance distribution
                    stance_counts = stances_df['Label'].value_counts()
                    fig_stances = px.bar(
                        x=stance_counts.index,
                        y=stance_counts.values,
                        title="Stance Distribution"
                    )
                    st.plotly_chart(fig_stances, width='stretch')
                
                # Frames analysis
                if frames:
                    st.subheader("Narrative Frames")
                    frames_data = []
                    for frame in frames:
                        frames_data.append({
                            'Frame': frame.frame_label,
                            'Type': frame.frame_type,
                            'Salience': frame.salience,
                            'Description': frame.description
                        })
                    
                    frames_df = pd.DataFrame(frames_data)
                    st.dataframe(frames_df, width='stretch')
                    
                    # Frame salience
                    fig_frames = px.bar(
                        frames_df,
                        x='Frame',
                        y='Salience',
                        title="Frame Salience"
                    )
                    st.plotly_chart(fig_frames, width='stretch')
                
                # Entities analysis
                if entities:
                    st.subheader("Extracted Entities")
                    entities_data = []
                    for entity in entities:
                        entities_data.append({
                            'Entity': entity.entity_name,
                            'Type': entity.entity_type,
                            'Confidence': entity.confidence,
                            'Jurisdiction': entity.jurisdiction
                        })
                    
                    entities_df = pd.DataFrame(entities_data)
                    st.dataframe(entities_df, width='stretch')
                    
                    # Entity types
                    entity_types = entities_df['Type'].value_counts()
                    fig_entities = px.pie(
                        values=entity_types.values,
                        names=entity_types.index,
                        title="Entity Types Distribution"
                    )
                    st.plotly_chart(fig_entities, width='stretch')
            
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")


def create_argument_graph():
    """Create argument graph visualization."""
    st.header("🕸️ Argument Graph")
    
    st.subheader("Argument Relationship Visualization")
    
    # Sample argument graph data
    sample_graph_data = {
        "nodes": [
            {"id": "claim_1", "label": "Regulation increases costs", "type": "claim", "score": 0.85},
            {"id": "claim_2", "label": "Costs affect small businesses", "type": "claim", "score": 0.78},
            {"id": "claim_3", "label": "Consumer protection needed", "type": "claim", "score": 0.92},
            {"id": "stance_1", "label": "Oppose regulation", "type": "stance", "score": 0.8},
            {"id": "stance_2", "label": "Support regulation", "type": "stance", "score": 0.75},
            {"id": "entity_1", "label": "Small Businesses", "type": "entity", "score": 0.9},
            {"id": "entity_2", "label": "Consumers", "type": "entity", "score": 0.88}
        ],
        "edges": [
            {"from": "claim_1", "to": "claim_2", "relation": "supports", "weight": 0.8},
            {"from": "claim_1", "to": "stance_1", "relation": "supports", "weight": 0.9},
            {"from": "claim_3", "to": "stance_2", "relation": "supports", "weight": 0.85},
            {"from": "claim_2", "to": "entity_1", "relation": "mentions", "weight": 0.7},
            {"from": "claim_3", "to": "entity_2", "relation": "mentions", "weight": 0.8}
        ]
    }
    
    # Create network graph
    if nx is not None:
        G = nx.DiGraph()
        
        # Add nodes
        for node in sample_graph_data["nodes"]:
            G.add_node(node["id"], **node)
        
        # Add edges
        for edge in sample_graph_data["edges"]:
            G.add_edge(edge["from"], edge["to"], **edge)
        
        # Calculate layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Create plotly network graph
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])

        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title=dict(text='Node Score'),
                    xanchor='left'
                ),
                line_width=2))

        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([f"{G.nodes[node]['label']}<br>Score: {G.nodes[node]['score']:.2f}"])
            node_trace['marker']['color'] += tuple([G.nodes[node]['score']])

        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Argument Graph',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002 ) ],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                       )
        
        st.plotly_chart(fig, width='stretch')
        
        # Graph statistics
        st.subheader("Graph Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Nodes", len(G.nodes()))
        with col2:
            st.metric("Edges", len(G.edges()))
        with col3:
            st.metric("Density", f"{nx.density(G):.3f}")
        with col4:
            st.metric("Components", nx.number_strongly_connected_components(G))
    else:
        st.error("Networkx is not installed. Please install it to use this page.")


def create_policy_timeline():
    """Create policy timeline visualization."""
    st.header("📅 Policy Timeline")
    
    st.subheader("Policy Development Timeline")
    
    # Sample timeline data
    timeline_data = [
        {
            "date": "2024-01-15",
            "event": "Initial Policy Proposal",
            "type": "proposal",
            "description": "Regulatory body proposes new fintech regulations",
            "impact": "high"
        },
        {
            "date": "2024-02-01",
            "event": "Public Consultation",
            "type": "consultation",
            "description": "Public comment period opens",
            "impact": "medium"
        },
        {
            "date": "2024-03-15",
            "event": "Industry Response",
            "type": "response",
            "description": "Industry groups submit feedback",
            "impact": "high"
        },
        {
            "date": "2024-04-01",
            "event": "Revised Proposal",
            "type": "revision",
            "description": "Regulatory body releases revised proposal",
            "impact": "high"
        },
        {
            "date": "2024-05-01",
            "event": "Final Rule",
            "type": "final",
            "description": "Final regulation published",
            "impact": "very_high"
        }
    ]
    
    # Create timeline visualization
    fig = go.Figure()
    
    # Color mapping for event types
    color_map = {
        "proposal": "blue",
        "consultation": "green",
        "response": "orange",
        "revision": "purple",
        "final": "red"
    }
    
    # Size mapping for impact
    size_map = {
        "low": 10,
        "medium": 15,
        "high": 20,
        "very_high": 25
    }
    
    for event in timeline_data:
        fig.add_trace(go.Scatter(
            x=[event["date"]],
            y=[event["event"]],
            mode='markers+text',
            marker=dict(
                size=size_map[event["impact"]],
                color=color_map[event["type"]],
                symbol='circle'
            ),
            text=event["description"],
            textposition="top center",
            name=event["type"].title(),
            showlegend=False
        ))
    
    fig.update_layout(
        title="Policy Development Timeline",
        xaxis_title="Date",
        yaxis_title="Event",
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Timeline table
    st.subheader("Timeline Details")
    timeline_df = pd.DataFrame(timeline_data)
    st.dataframe(timeline_df)


def create_sentiment_analysis():
    """Create sentiment analysis section."""
    st.header("😊 Sentiment Analysis")
    
    st.subheader("Policy Sentiment Over Time")
    
    # Sample sentiment data
    sentiment_data = {
        "date": ["2024-01-01", "2024-01-15", "2024-02-01", "2024-02-15", "2024-03-01", "2024-03-15"],
        "positive": [0.3, 0.25, 0.2, 0.15, 0.1, 0.05],
        "negative": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
        "neutral": [0.5, 0.45, 0.4, 0.35, 0.3, 0.25]
    }
    
    df = pd.DataFrame(sentiment_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Create sentiment trend chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['positive'],
        mode='lines+markers',
        name='Positive',
        line=dict(color='green')
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['negative'],
        mode='lines+markers',
        name='Negative',
        line=dict(color='red')
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['neutral'],
        mode='lines+markers',
        name='Neutral',
        line=dict(color='gray')
    ))
    
    fig.update_layout(
        title="Sentiment Trends Over Time",
        xaxis_title="Date",
        yaxis_title="Sentiment Score",
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Sentiment summary
    st.subheader("Current Sentiment Summary")
    col1, col2, col3 = st.columns(3)
    
    latest = df.iloc[-1]
    with col1:
        st.metric("Positive", f"{latest['positive']:.1%}")
    with col2:
        st.metric("Negative", f"{latest['negative']:.1%}")
    with col3:
        st.metric("Neutral", f"{latest['neutral']:.1%}")


def main():
    """Main function for the Policy Argument Maps page."""
    st.set_page_config(
        page_title="Policy Argument Maps",
        page_icon="🕸️",
        layout="wide"
    )
    
    st.title("🕸️ Policy Argument Maps")
    st.markdown("""
    This page provides visualization and analysis of policy arguments, debate structures, 
    and sentiment trends. Explore argument relationships, policy timelines, and sentiment analysis.
    """)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Argument Analysis", "Argument Graph", "Policy Timeline", "Sentiment Analysis"
    ])
    
    with tab1:
        create_argument_analysis()
    
    with tab2:
        create_argument_graph()
    
    with tab3:
        create_policy_timeline()
    
    with tab4:
        create_sentiment_analysis()


if __name__ == "__main__":
    main()
