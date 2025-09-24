from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from typing import Dict, List, Optional

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()
        
    def generate_pdf_report(self, company: str, analysis_data: Dict) -> str:
        """Generate a comprehensive PDF report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"{company}_analysis_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(
            str(filename),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create content
        content = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        content.append(Paragraph(f"Analysis Report: {company}", title_style))
        content.append(Spacer(1, 12))
        
        # Executive Summary
        content.append(Paragraph("Executive Summary", self.styles['Heading2']))
        content.append(Paragraph(analysis_data.get('summary', ''), self.styles['Normal']))
        content.append(Spacer(1, 12))
        
        # Market Analysis
        content.append(Paragraph("Market Analysis", self.styles['Heading2']))
        market_data = analysis_data.get('market_analysis', {})
        if market_data:
            # Create market analysis table
            market_table_data = [
                ['Metric', 'Value'],
                ['Current Price', f"${market_data.get('current_price', 0):.2f}"],
                ['Market Cap', f"${market_data.get('market_cap', 0):,.2f}"],
                ['P/E Ratio', f"{market_data.get('pe_ratio', 0):.2f}"],
                ['Dividend Yield', f"{market_data.get('dividend_yield', 0):.2%}"]
            ]
            market_table = Table(market_table_data, colWidths=[2*inch, 2*inch])
            market_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(market_table)
            content.append(Spacer(1, 12))
        
        # Sentiment Analysis
        content.append(Paragraph("Sentiment Analysis", self.styles['Heading2']))
        sentiment_data = analysis_data.get('sentiment_analysis', {})
        if sentiment_data:
            sentiment_text = f"""
            Overall Sentiment: {sentiment_data.get('overall_sentiment', 0):.2f}
            Confidence: {sentiment_data.get('confidence', 0):.2f}
            Article Count: {sentiment_data.get('article_count', 0)}
            """
            content.append(Paragraph(sentiment_text, self.styles['Normal']))
            content.append(Spacer(1, 12))
        
        # Risk Analysis
        content.append(Paragraph("Risk Analysis", self.styles['Heading2']))
        risk_data = analysis_data.get('risk_analysis', {})
        if risk_data:
            risk_table_data = [
                ['Risk Metric', 'Value'],
                ['Volatility', f"{risk_data.get('volatility', 0):.2%}"],
                ['Value at Risk (95%)', f"{risk_data.get('var_95', 0):.2%}"],
                ['Beta', f"{risk_data.get('beta', 0):.2f}"],
                ['Risk Score', f"{risk_data.get('risk_score', 0):.2f}"]
            ]
            risk_table = Table(risk_table_data, colWidths=[2*inch, 2*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(risk_table)
            content.append(Spacer(1, 12))
        
        # Recommendations
        content.append(Paragraph("Recommendations", self.styles['Heading2']))
        recommendations = analysis_data.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                content.append(Paragraph(f"• {rec}", self.styles['Normal']))
            content.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(content)
        return str(filename)
    
    def generate_excel_report(self, company: str, analysis_data: Dict) -> str:
        """Generate an Excel report with multiple sheets."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"{company}_analysis_{timestamp}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(filename) as writer:
            # Market Analysis Sheet
            market_data = analysis_data.get('market_analysis', {})
            if market_data:
                market_df = pd.DataFrame([market_data])
                market_df.to_excel(writer, sheet_name='Market Analysis', index=False)
            
            # Sentiment Analysis Sheet
            sentiment_data = analysis_data.get('sentiment_analysis', {})
            if sentiment_data:
                sentiment_df = pd.DataFrame([sentiment_data])
                sentiment_df.to_excel(writer, sheet_name='Sentiment Analysis', index=False)
            
            # Risk Analysis Sheet
            risk_data = analysis_data.get('risk_analysis', {})
            if risk_data:
                risk_df = pd.DataFrame([risk_data])
                risk_df.to_excel(writer, sheet_name='Risk Analysis', index=False)
            
            # Recommendations Sheet
            recommendations = analysis_data.get('recommendations', [])
            if recommendations:
                rec_df = pd.DataFrame(recommendations, columns=['Recommendation'])
                rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
        
        return str(filename)
    
    def generate_json_report(self, company: str, analysis_data: Dict) -> str:
        """Generate a JSON report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"{company}_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=4)
        
        return str(filename)
    
    def generate_visualizations(self, company: str, analysis_data: Dict) -> Dict[str, str]:
        """Generate various visualizations."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        viz_dir = self.output_dir / "visualizations" / f"{company}_{timestamp}"
        viz_dir.mkdir(parents=True, exist_ok=True)
        
        viz_files = {}
        
        # Price Chart
        if 'market_data' in analysis_data:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              vertical_spacing=0.03, subplot_titles=('Price', 'Volume'),
                              row_width=[0.7, 0.3])
            
            fig.add_trace(go.Candlestick(
                x=analysis_data['market_data'].index,
                open=analysis_data['market_data']['Open'],
                high=analysis_data['market_data']['High'],
                low=analysis_data['market_data']['Low'],
                close=analysis_data['market_data']['Close'],
                name='Price'
            ), row=1, col=1)
            
            fig.add_trace(go.Bar(
                x=analysis_data['market_data'].index,
                y=analysis_data['market_data']['Volume'],
                name='Volume'
            ), row=2, col=1)
            
            fig.update_layout(
                title=f'{company} Stock Price and Volume',
                yaxis_title='Price',
                yaxis2_title='Volume',
                xaxis_rangeslider_visible=False
            )
            
            price_chart_path = viz_dir / "price_chart.html"
            fig.write_html(str(price_chart_path))
            viz_files['price_chart'] = str(price_chart_path)
        
        # Sentiment Chart
        if 'sentiment_analysis' in analysis_data:
            sentiment_data = analysis_data['sentiment_analysis']
            fig = go.Figure()
            
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=sentiment_data.get('overall_sentiment', 0),
                title={'text': "Overall Sentiment"},
                gauge={'axis': {'range': [-1, 1]},
                      'bar': {'color': "darkblue"},
                      'steps': [
                          {'range': [-1, -0.5], 'color': "red"},
                          {'range': [-0.5, 0], 'color': "orange"},
                          {'range': [0, 0.5], 'color': "lightgreen"},
                          {'range': [0.5, 1], 'color': "green"}
                      ]}
            ))
            
            sentiment_chart_path = viz_dir / "sentiment_chart.html"
            fig.write_html(str(sentiment_chart_path))
            viz_files['sentiment_chart'] = str(sentiment_chart_path)
        
        # Risk Chart
        if 'risk_analysis' in analysis_data:
            risk_data = analysis_data['risk_analysis']
            fig = go.Figure()
            
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=risk_data.get('risk_score', 0),
                title={'text': "Risk Score"},
                gauge={'axis': {'range': [0, 10]},
                      'bar': {'color': "darkblue"},
                      'steps': [
                          {'range': [0, 3], 'color': "green"},
                          {'range': [3, 7], 'color': "orange"},
                          {'range': [7, 10], 'color': "red"}
                      ]}
            ))
            
            risk_chart_path = viz_dir / "risk_chart.html"
            fig.write_html(str(risk_chart_path))
            viz_files['risk_chart'] = str(risk_chart_path)
        
        return viz_files 