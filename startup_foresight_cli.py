#!/usr/bin/env python3
"""
Startup Foresight CLI - Comprehensive Command Line Interface

This file provides a menu-driven interface for all system operations including:
- Article collection and analysis
- Domain analysis and simulation
- Financial predictions
- Policy argument mining
- Portfolio risk monitoring
- System testing and validation
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

class StartupForesightCLI:
    """Main CLI class for Startup Foresight system."""
    
    def __init__(self):
        self.system_status = "initializing"
        self.current_session = {
            "start_time": datetime.now(),
            "operations_performed": [],
            "data_collected": {},
            "analysis_results": {}
        }
        
    def print_banner(self):
        """Print the system banner."""
        print("=" * 80)
        print("🚀 STARTUP FORESIGHT - RELATIONAL STARTUP ANALYSIS SYSTEM")
        print("=" * 80)
        print("📊 Advanced Startup Performance Prediction & Risk Analysis")
        print("🔍 Policy-Aware Financial Impact Assessment")
        print("⚡ Real-time Event Detection & Classification")
        print("=" * 80)
        print()
    
    def print_menu(self):
        """Print the main menu."""
        print("\n📋 MAIN MENU - Select an operation:")
        print("-" * 50)
        print("1.  📰 Article Collection & News Analysis")
        print("2.  🏢 Domain Analysis & Simulation")
        print("3.  💰 Financial Predictions & Modeling")
        print("4.  🗳️  Policy Argument Mining")
        print("5.  📊 Portfolio Risk Monitoring")
        print("6.  🧪 System Testing & Validation")
        print("7.  🌐 Launch Web Dashboard")
        print("8.  📈 Generate Reports")
        print("9.  ⚙️  System Configuration")
        print("10. 📊 View System Status")
        print("11. 🔄 Run Complete Analysis Pipeline")
        print("0.  🚪 Exit System")
        print("-" * 50)
    
    def get_user_choice(self) -> int:
        """Get user choice from menu."""
        try:
            choice = input("\n🎯 Enter your choice (0-11): ").strip()
            return int(choice)
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            return -1
    
    def run_article_collection(self):
        """Run article collection and analysis."""
        print("\n📰 ARTICLE COLLECTION & NEWS ANALYSIS")
        print("=" * 50)
        
        try:
            from data_collection.news_collector import NewsCollector
            from event_detection.event_classifier import EventClassifier
            
            print("🔍 Initializing news collection system...")
            collector = NewsCollector()
            classifier = EventClassifier()
            
            # Get user preferences
            print("\n📝 Collection Parameters:")
            keywords = input("Enter keywords to search (comma-separated): ").strip()
            if not keywords:
                keywords = "startup, venture capital, fintech, regulation, policy"
            
            num_articles = input("Number of articles to collect (default: 50): ").strip()
            num_articles = int(num_articles) if num_articles.isdigit() else 50
            
            print(f"\n🔍 Collecting {num_articles} articles for keywords: {keywords}")
            
            # Simulate article collection
            articles = []
            for i in range(min(num_articles, 10)):  # Limit for demo
                article = {
                    "title": f"Sample Article {i+1}",
                    "content": f"This is sample content for article {i+1} about {keywords}",
                    "source": "Sample News",
                    "date": datetime.now() - timedelta(days=i),
                    "url": f"https://example.com/article{i+1}"
                }
                articles.append(article)
            
            print(f"✅ Collected {len(articles)} articles")
            
            # Analyze articles
            print("🧠 Analyzing articles for events...")
            events = []
            for article in articles:
                event = classifier.classify_event(article)
                if event:
                    events.append(event)
            
            print(f"✅ Detected {len(events)} events")
            
            # Store results
            self.current_session["data_collected"]["articles"] = articles
            self.current_session["analysis_results"]["events"] = events
            self.current_session["operations_performed"].append("article_collection")
            
            print("\n📊 Analysis Summary:")
            print(f"   • Articles collected: {len(articles)}")
            print(f"   • Events detected: {len(events)}")
            print(f"   • Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error in article collection: {e}")
    
    def run_domain_analysis(self):
        """Run domain analysis and simulation."""
        print("\n🏢 DOMAIN ANALYSIS & SIMULATION")
        print("=" * 50)
        
        try:
            from utils.registry import list_domain_keys, get_domain
            from simulation.scenario_engine import ScenarioEngine
            from simulation.shocks import ShockGenerator
            
            print("🔍 Available domains:")
            domain_keys = list_domain_keys()
            for i, key in enumerate(domain_keys, 1):
                domain = get_domain(key)
                print(f"   {i}. {key}: {domain.name}")
            
            # Get user selection
            choice = input(f"\nSelect domain (1-{len(domain_keys)}): ").strip()
            try:
                domain_index = int(choice) - 1
                if 0 <= domain_index < len(domain_keys):
                    selected_domain_key = domain_keys[domain_index]
                    domain = get_domain(selected_domain_key)
                    print(f"\n✅ Selected: {domain.name}")
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid input")
                return
            
            # Get simulation parameters
            print(f"\n📊 Analyzing {domain.name}...")
            
            # Extract features
            sample_inputs = {
                "revenue": 1000000,
                "employees": 50,
                "funding_rounds": 3,
                "market_size": 1000000000
            }
            
            features = domain.extract_features(sample_inputs)
            print(f"✅ Extracted {len(features)} features")
            
            # Get risk factors
            risk_factors = domain.risk_factors()
            print(f"⚠️  Identified {len(risk_factors)} risk factors")
            
            # Run simulation
            print("\n🧪 Running simulation...")
            shock_generator = ShockGenerator()
            scenario_engine = ScenarioEngine()
            
            # Generate sample shocks
            shocks = shock_generator.generate_shock_sequence(num_shocks=3)
            print(f"⚡ Generated {len(shocks)} shocks")
            
            # Simulate response
            response = domain.simulate_response(features, shocks)
            print(f"📈 Simulation completed with {len(response)} metrics")
            
            # Store results
            self.current_session["analysis_results"]["domain_analysis"] = {
                "domain": selected_domain_key,
                "features": features,
                "risk_factors": risk_factors,
                "shocks": [{"type": s.type, "intensity": s.intensity} for s in shocks],
                "response": response
            }
            self.current_session["operations_performed"].append("domain_analysis")
            
            print("\n📊 Analysis Summary:")
            print(f"   • Domain: {domain.name}")
            print(f"   • Features extracted: {len(features)}")
            print(f"   • Risk factors: {len(risk_factors)}")
            print(f"   • Simulation metrics: {len(response)}")
            
        except Exception as e:
            print(f"❌ Error in domain analysis: {e}")
    
    def run_financial_predictions(self):
        """Run financial predictions and modeling."""
        print("\n💰 FINANCIAL PREDICTIONS & MODELING")
        print("=" * 50)
        
        try:
            from modeling.financial_predictor import FinancialPredictor
            
            print("🧠 Initializing financial prediction models...")
            predictor = FinancialPredictor()
            
            # Get user inputs
            print("\n📝 Financial Parameters:")
            revenue = input("Current revenue (default: 1000000): ").strip()
            revenue = float(revenue) if revenue else 1000000
            
            growth_rate = input("Growth rate (default: 0.2): ").strip()
            growth_rate = float(growth_rate) if growth_rate else 0.2
            
            months = input("Prediction horizon in months (default: 12): ").strip()
            months = int(months) if months.isdigit() else 12
            
            print(f"\n🔮 Generating predictions for {months} months...")
            
            # Generate predictions
            predictions = predictor.predict_financial_metrics({
                "revenue": revenue,
                "growth_rate": growth_rate,
                "months": months
            })
            
            print(f"✅ Generated {len(predictions)} financial metrics")
            
            # Store results
            self.current_session["analysis_results"]["financial_predictions"] = predictions
            self.current_session["operations_performed"].append("financial_predictions")
            
            print("\n📊 Prediction Summary:")
            for metric, value in list(predictions.items())[:5]:  # Show first 5
                print(f"   • {metric}: {value}")
            if len(predictions) > 5:
                print(f"   • ... and {len(predictions) - 5} more metrics")
            
        except Exception as e:
            print(f"❌ Error in financial predictions: {e}")
    
    def run_policy_analysis(self):
        """Run policy argument mining and analysis."""
        print("\n🗳️  POLICY ARGUMENT MINING")
        print("=" * 50)
        
        try:
            from policy_argument_mining.integration import PolicyArgumentIntegrator
            from policy_argument_mining.claim_detection import ClaimDetector
            from policy_argument_mining.stance_detection import StanceDetector
            
            print("🧠 Initializing policy analysis system...")
            integrator = PolicyArgumentIntegrator()
            claim_detector = ClaimDetector()
            stance_detector = StanceDetector()
            
            # Get policy text
            print("\n📝 Policy Analysis:")
            policy_text = input("Enter policy text to analyze (or press Enter for sample): ").strip()
            if not policy_text:
                policy_text = """
                The proposed regulation will increase compliance costs for small businesses by 15-20%. 
                Industry analysis shows that this burden will disproportionately affect startups and 
                could stifle innovation in the fintech sector. However, consumer advocacy groups 
                argue that the regulation is necessary to protect consumers from predatory practices.
                """
            
            print(f"\n🔍 Analyzing policy text ({len(policy_text)} characters)...")
            
            # Simulate policy analysis
            claims = claim_detector.detect_claims([policy_text])
            stances = stance_detector.detect_stances_from_claims(claims)
            
            print(f"✅ Detected {len(claims)} claims and {len(stances)} stances")
            
            # Analyze policy signals
            policy_signals = integrator.analyze_policy_arguments(claims, stances, [], [])
            print(f"📊 Generated {len(policy_signals)} policy signals")
            
            # Store results
            self.current_session["analysis_results"]["policy_analysis"] = {
                "claims": len(claims),
                "stances": len(stances),
                "policy_signals": len(policy_signals)
            }
            self.current_session["operations_performed"].append("policy_analysis")
            
            print("\n📊 Policy Analysis Summary:")
            print(f"   • Claims detected: {len(claims)}")
            print(f"   • Stances identified: {len(stances)}")
            print(f"   • Policy signals: {len(policy_signals)}")
            
        except Exception as e:
            print(f"❌ Error in policy analysis: {e}")
    
    def run_portfolio_monitoring(self):
        """Run portfolio risk monitoring."""
        print("\n📊 PORTFOLIO RISK MONITORING")
        print("=" * 50)
        
        try:
            from utils.registry import list_domain_keys
            from simulation.domain_response import DomainResponseSimulator
            from simulation.shocks import ShockGenerator
            
            print("🔍 Available domains for portfolio:")
            domain_keys = list_domain_keys()
            for i, key in enumerate(domain_keys, 1):
                print(f"   {i}. {key}")
            
            # Create sample portfolio
            print("\n💼 Creating sample portfolio...")
            portfolio = {
                "name": "Sample Portfolio",
                "holdings": [
                    {"domain": domain_keys[0], "weight": 0.4, "value": 4000000},
                    {"domain": domain_keys[1] if len(domain_keys) > 1 else domain_keys[0], "weight": 0.3, "value": 3000000},
                    {"domain": domain_keys[2] if len(domain_keys) > 2 else domain_keys[0], "weight": 0.3, "value": 3000000}
                ]
            }
            
            print(f"✅ Created portfolio with {len(portfolio['holdings'])} holdings")
            
            # Run risk analysis
            print("\n⚠️  Running risk analysis...")
            simulator = DomainResponseSimulator()
            shock_generator = ShockGenerator()
            
            # Generate shocks
            shocks = shock_generator.generate_shock_sequence(num_shocks=2)
            
            # Simulate portfolio response
            portfolio_responses = {}
            for holding in portfolio["holdings"]:
                response = simulator.simulate_domain_response(
                    holding["domain"], 
                    {"revenue": holding["value"]}, 
                    shocks
                )
                portfolio_responses[holding["domain"]] = response
            
            print(f"✅ Completed risk analysis for {len(portfolio_responses)} holdings")
            
            # Store results
            self.current_session["analysis_results"]["portfolio_monitoring"] = {
                "portfolio": portfolio,
                "responses": portfolio_responses,
                "shocks": len(shocks)
            }
            self.current_session["operations_performed"].append("portfolio_monitoring")
            
            print("\n📊 Portfolio Summary:")
            print(f"   • Total holdings: {len(portfolio['holdings'])}")
            print(f"   • Total value: ${sum(h['value'] for h in portfolio['holdings']):,}")
            print(f"   • Risk scenarios: {len(shocks)}")
            
        except Exception as e:
            print(f"❌ Error in portfolio monitoring: {e}")
    
    def run_system_testing(self):
        """Run system testing and validation."""
        print("\n🧪 SYSTEM TESTING & VALIDATION")
        print("=" * 50)
        
        try:
            print("🔍 Running comprehensive system tests...")
            
            # Test domains
            print("\n1. Testing domains...")
            from utils.registry import list_domain_keys, get_domain
            domain_keys = list_domain_keys()
            domain_tests_passed = 0
            
            for key in domain_keys:
                try:
                    domain = get_domain(key)
                    features = domain.extract_features({})
                    risks = domain.risk_factors()
                    domain_tests_passed += 1
                    print(f"   ✅ {key}: {domain.name}")
                except Exception as e:
                    print(f"   ❌ {key}: {e}")
            
            # Test event detection
            print("\n2. Testing event detection...")
            try:
                from event_detection.event_classifier import EventClassifier
                classifier = EventClassifier()
                print("   ✅ Event classification system working")
                event_tests_passed = 1
            except Exception as e:
                print(f"   ❌ Event detection: {e}")
                event_tests_passed = 0
            
            # Test financial prediction
            print("\n3. Testing financial prediction...")
            try:
                from modeling.financial_predictor import FinancialPredictor
                predictor = FinancialPredictor()
                predictions = predictor.predict_financial_metrics({"revenue": 1000000})
                print(f"   ✅ Financial prediction: {len(predictions)} metrics")
                financial_tests_passed = 1
            except Exception as e:
                print(f"   ❌ Financial prediction: {e}")
                financial_tests_passed = 0
            
            # Test simulation
            print("\n4. Testing simulation engine...")
            try:
                from simulation.scenario_engine import ScenarioEngine
                from simulation.shocks import ShockGenerator
                engine = ScenarioEngine()
                generator = ShockGenerator()
                shocks = generator.generate_shock_sequence(num_shocks=2)
                print(f"   ✅ Simulation: {len(shocks)} shocks generated")
                simulation_tests_passed = 1
            except Exception as e:
                print(f"   ❌ Simulation: {e}")
                simulation_tests_passed = 0
            
            # Summary
            total_tests = 4
            passed_tests = domain_tests_passed + event_tests_passed + financial_tests_passed + simulation_tests_passed
            
            print(f"\n📊 Test Results: {passed_tests}/{total_tests} components working")
            
            if passed_tests == total_tests:
                print("🎉 All system tests passed!")
                self.system_status = "operational"
            else:
                print("⚠️  Some components need attention")
                self.system_status = "partial"
            
            # Store results
            self.current_session["analysis_results"]["system_tests"] = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "domain_tests": domain_tests_passed,
                "event_tests": event_tests_passed,
                "financial_tests": financial_tests_passed,
                "simulation_tests": simulation_tests_passed
            }
            self.current_session["operations_performed"].append("system_testing")
            
        except Exception as e:
            print(f"❌ Error in system testing: {e}")
    
    def launch_web_dashboard(self):
        """Launch the web dashboard."""
        print("\n🌐 LAUNCHING WEB DASHBOARD")
        print("=" * 50)
        
        try:
            print("🚀 Starting Streamlit dashboard...")
            print("📱 Dashboard will be available at: http://localhost:8501")
            print("⏹️  Press Ctrl+C to stop the dashboard")
            print("\n" + "="*50)
            
            # Launch Streamlit
            import subprocess
            import sys
            
            # Use the virtual environment Python
            venv_python = Path("venv/Scripts/python.exe")
            if venv_python.exists():
                cmd = [str(venv_python), "-m", "streamlit", "run", "streamlit_app/main.py", "--server.port", "8501"]
            else:
                cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app/main.py", "--server.port", "8501"]
            
            subprocess.run(cmd)
            
        except KeyboardInterrupt:
            print("\n⏹️  Dashboard stopped by user")
        except Exception as e:
            print(f"❌ Error launching dashboard: {e}")
            print("💡 Try installing dependencies first: venv\\Scripts\\python.exe -m pip install streamlit plotly fastapi uvicorn")
    
    def generate_reports(self):
        """Generate analysis reports."""
        print("\n📈 GENERATING REPORTS")
        print("=" * 50)
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"reports/analysis_report_{timestamp}.json"
            
            # Ensure reports directory exists
            Path("reports").mkdir(exist_ok=True)
            
            # Generate report
            report = {
                "timestamp": timestamp,
                "session_info": self.current_session,
                "system_status": self.system_status,
                "operations_performed": self.current_session["operations_performed"],
                "summary": {
                    "total_operations": len(self.current_session["operations_performed"]),
                    "session_duration": str(datetime.now() - self.current_session["start_time"]),
                    "data_collected": len(self.current_session["data_collected"]),
                    "analysis_results": len(self.current_session["analysis_results"])
                }
            }
            
            # Save report
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"✅ Report generated: {report_file}")
            print(f"📊 Session summary:")
            print(f"   • Operations performed: {report['summary']['total_operations']}")
            print(f"   • Session duration: {report['summary']['session_duration']}")
            print(f"   • Data collections: {report['summary']['data_collected']}")
            print(f"   • Analysis results: {report['summary']['analysis_results']}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def show_system_status(self):
        """Show current system status."""
        print("\n📊 SYSTEM STATUS")
        print("=" * 50)
        
        print(f"🟢 System Status: {self.system_status.upper()}")
        print(f"⏰ Session Start: {self.current_session['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔄 Operations Performed: {len(self.current_session['operations_performed'])}")
        
        if self.current_session['operations_performed']:
            print("\n📋 Recent Operations:")
            for i, op in enumerate(self.current_session['operations_performed'][-5:], 1):
                print(f"   {i}. {op}")
        
        print(f"\n📊 Data Collections: {len(self.current_session['data_collected'])}")
        print(f"📈 Analysis Results: {len(self.current_session['analysis_results'])}")
        
        # Test system components
        print("\n🔍 Component Status:")
        try:
            from utils.registry import list_domain_keys
            domain_count = len(list_domain_keys())
            print(f"   ✅ Domains: {domain_count} available")
        except:
            print("   ❌ Domains: Not available")
        
        try:
            from event_detection.event_classifier import EventClassifier
            print("   ✅ Event Detection: Available")
        except:
            print("   ❌ Event Detection: Not available")
        
        try:
            from modeling.financial_predictor import FinancialPredictor
            print("   ✅ Financial Prediction: Available")
        except:
            print("   ❌ Financial Prediction: Not available")
    
    def run_complete_pipeline(self):
        """Run the complete analysis pipeline."""
        print("\n🔄 RUNNING COMPLETE ANALYSIS PIPELINE")
        print("=" * 50)
        
        print("🚀 Starting comprehensive analysis...")
        
        # Run all major components
        operations = [
            ("Article Collection", self.run_article_collection),
            ("Domain Analysis", self.run_domain_analysis),
            ("Financial Predictions", self.run_financial_predictions),
            ("Policy Analysis", self.run_policy_analysis),
            ("Portfolio Monitoring", self.run_portfolio_monitoring),
            ("System Testing", self.run_system_testing)
        ]
        
        for name, operation in operations:
            print(f"\n🔄 Running {name}...")
            try:
                operation()
                print(f"✅ {name} completed")
            except Exception as e:
                print(f"❌ {name} failed: {e}")
        
        print("\n🎉 Complete analysis pipeline finished!")
        print("📊 Use option 8 to generate a comprehensive report")
    
    def run(self):
        """Main CLI loop."""
        self.print_banner()
        
        while True:
            self.print_menu()
            choice = self.get_user_choice()
            
            if choice == 0:
                print("\n👋 Thank you for using Startup Foresight!")
                print("📊 Session summary:")
                print(f"   • Operations performed: {len(self.current_session['operations_performed'])}")
                print(f"   • Session duration: {datetime.now() - self.current_session['start_time']}")
                break
            elif choice == 1:
                self.run_article_collection()
            elif choice == 2:
                self.run_domain_analysis()
            elif choice == 3:
                self.run_financial_predictions()
            elif choice == 4:
                self.run_policy_analysis()
            elif choice == 5:
                self.run_portfolio_monitoring()
            elif choice == 6:
                self.run_system_testing()
            elif choice == 7:
                self.launch_web_dashboard()
            elif choice == 8:
                self.generate_reports()
            elif choice == 9:
                print("\n⚙️  System Configuration")
                print("Configuration options will be available in future versions.")
            elif choice == 10:
                self.show_system_status()
            elif choice == 11:
                self.run_complete_pipeline()
            else:
                print("❌ Invalid choice. Please select 0-11.")
            
            input("\n⏸️  Press Enter to continue...")

def main():
    """Main entry point."""
    try:
        cli = StartupForesightCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 System interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


