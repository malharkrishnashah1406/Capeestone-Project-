"""
Dashboard Module.

This module provides visualization capabilities for the startup performance
prediction system.
"""

from typing import Dict, List, Any, Optional
import logging
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StartupDashboard:
    """Dashboard for startup performance visualization."""
    
    def __init__(self):
        self.chart_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def run(self):
        """Run the main dashboard."""
        if 'startup_data' not in st.session_state:
            st.warning("No startup data available. Please run the analysis first.")
            return
        
        startup_data = st.session_state.get('startup_data', {})
        events = st.session_state.get('events', [])
        predictions = st.session_state.get('predictions', {})
        
        # Display main dashboard
        self._display_overview(startup_data, events, predictions)
        self._display_predictions(predictions)
        self._display_events(events)
        self._display_analysis(startup_data, events, predictions)
    
    def _display_overview(self, startup_data: Dict[str, Any], events: List[Dict[str, Any]], 
                         predictions: Dict[str, Any]):
        """Display overview section."""
        st.header("📊 Startup Performance Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Startup Name",
                startup_data.get('startup_name', 'Unknown'),
                delta=None
            )
        
        with col2:
            st.metric(
                "Events Analyzed",
                len(events),
                delta=f"+{len(events)} new events"
            )
        
        with col3:
            confidence = predictions.get('confidence', 0.0)
            st.metric(
                "Prediction Confidence",
                f"{confidence:.1%}",
                delta=f"{confidence:.1%} confidence"
            )
        
        with col4:
            st.metric(
                "Analysis Date",
                datetime.now().strftime("%Y-%m-%d"),
                delta="Latest analysis"
            )
    
    def _display_predictions(self, predictions: Dict[str, Any]):
        """Display financial predictions."""
        st.header("💰 Financial Predictions")
        
        if not predictions:
            st.warning("No predictions available.")
            return
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            revenue = predictions.get('revenue', 0)
            st.metric(
                "Predicted Revenue",
                f"${revenue:,.0f}",
                delta=f"${revenue:,.0f}"
            )
        
        with col2:
            profit = predictions.get('profit', 0)
            st.metric(
                "Predicted Profit",
                f"${profit:,.0f}",
                delta=f"${profit:,.0f}"
            )
        
        with col3:
            valuation = predictions.get('valuation', 0)
            st.metric(
                "Predicted Valuation",
                f"${valuation:,.0f}",
                delta=f"${valuation:,.0f}"
            )
        
        # Financial metrics chart
        self._create_financial_metrics_chart(predictions)
    
    def _create_financial_metrics_chart(self, predictions: Dict[str, Any]):
        """Create chart for financial metrics."""
        metrics = ['revenue', 'profit', 'valuation', 'market_share', 'funding_availability']
        values = [predictions.get(metric, 0) for metric in metrics]
        
        # Normalize values for better visualization
        normalized_values = []
        for i, value in enumerate(values):
            if i < 3:  # Revenue, profit, valuation
                normalized_values.append(value / 1000000)  # Convert to millions
            else:
                normalized_values.append(value * 100)  # Convert to percentage
        
        fig = go.Figure(data=[
            go.Bar(
                x=metrics,
                y=normalized_values,
                marker_color=self.chart_colors[:len(metrics)]
            )
        ])
        
        fig.update_layout(
            title="Financial Metrics Overview",
            xaxis_title="Metrics",
            yaxis_title="Values (Normalized)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_events(self, events: List[Dict[str, Any]]):
        """Display events analysis."""
        st.header("📰 Events Analysis")
        
        if not events:
            st.info("No events to display.")
            return
        
        # Event categories
        categories = [event.get('event_category', 'unknown') for event in events]
        category_counts = pd.Series(categories).value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Event categories pie chart
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Event Categories Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Event sentiment
            sentiments = [event.get('sentiment', 0) for event in events]
            confidences = [event.get('confidence', 0) for event in events]
            
            fig = go.Figure(data=[
                go.Scatter(
                    x=sentiments,
                    y=confidences,
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=sentiments,
                        colorscale='RdYlGn',
                        showscale=True
                    ),
                    text=[f"Event {i+1}" for i in range(len(events))],
                    hovertemplate="Sentiment: %{x:.2f}<br>Confidence: %{y:.2f}<br>%{text}<extra></extra>"
                )
            ])
            
            fig.update_layout(
                title="Event Sentiment vs Confidence",
                xaxis_title="Sentiment (-1 to 1)",
                yaxis_title="Confidence (0 to 1)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Events table
        st.subheader("Recent Events")
        events_df = pd.DataFrame(events)
        if not events_df.empty:
            display_columns = ['title', 'event_category', 'sentiment', 'confidence', 'published_at']
            available_columns = [col for col in display_columns if col in events_df.columns]
            st.dataframe(events_df[available_columns], use_container_width=True)
    
    def _display_analysis(self, startup_data: Dict[str, Any], events: List[Dict[str, Any]], 
                         predictions: Dict[str, Any]):
        """Display analysis insights."""
        st.header("🔍 Analysis Insights")
        
        # Generate insights
        insights = self._generate_insights(startup_data, events, predictions)
        
        for insight in insights:
            st.info(insight)
    
    def _generate_insights(self, startup_data: Dict[str, Any], events: List[Dict[str, Any]], 
                          predictions: Dict[str, Any]) -> List[str]:
        """Generate analysis insights."""
        insights = []
        
        # Event insights
        if events:
            num_events = len(events)
            avg_sentiment = np.mean([e.get('sentiment', 0) for e in events])
            avg_confidence = np.mean([e.get('confidence', 0) for e in events])
            
            insights.append(f"Analyzed {num_events} events with average sentiment of {avg_sentiment:.2f}")
            insights.append(f"Event classification confidence: {avg_confidence:.1%}")
        
        # Prediction insights
        if predictions:
            confidence = predictions.get('confidence', 0)
            revenue = predictions.get('revenue', 0)
            profit = predictions.get('profit', 0)
            
            insights.append(f"Financial predictions have {confidence:.1%} confidence")
            insights.append(f"Predicted revenue: ${revenue:,.0f}")
            insights.append(f"Predicted profit: ${profit:,.0f}")
        
        # Risk insights
        if events:
            high_impact_events = [e for e in events if e.get('impact_score', 0) > 0.7]
            if high_impact_events:
                insights.append(f"⚠️ {len(high_impact_events)} high-impact events detected")
        
        return insights
    
    def create_time_series_chart(self, data: Dict[str, List[float]], 
                                title: str = "Time Series Analysis") -> go.Figure:
        """Create time series chart."""
        fig = go.Figure()
        
        for i, (metric, values) in enumerate(data.items()):
            fig.add_trace(go.Scatter(
                y=values,
                mode='lines+markers',
                name=metric,
                line=dict(color=self.chart_colors[i % len(self.chart_colors)])
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Time Period",
            yaxis_title="Value",
            hovermode='x unified'
        )
        
        return fig
    
    def create_correlation_heatmap(self, data: pd.DataFrame, 
                                  title: str = "Correlation Matrix") -> go.Figure:
        """Create correlation heatmap."""
        corr_matrix = data.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Metrics",
            yaxis_title="Metrics"
        )
        
        return fig