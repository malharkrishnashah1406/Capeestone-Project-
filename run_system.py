#!/usr/bin/env python3
"""
Main System Startup Script.

This script launches the complete startup performance prediction system
with all functionalities working together.
"""

import sys
import os
import subprocess
import time
import threading
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemLauncher:
    """Launches all components of the startup performance prediction system."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = []
        
    def check_dependencies(self):
        """Check if all required dependencies are installed."""
        logger.info("🔍 Checking system dependencies...")
        
        required_packages = [
            'numpy', 'pandas', 'plotly', 'streamlit', 'fastapi', 
            'uvicorn', 'python-dotenv', 'pyyaml', 'networkx',
            'scikit-learn', 'xgboost', 'lightgbm', 'lifelines',
            'matplotlib', 'seaborn', 'scipy'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"  ✓ {package}")
            except ImportError:
                missing_packages.append(package)
                logger.error(f"  ✗ {package} - MISSING")
        
        if missing_packages:
            logger.error(f"\n❌ Missing packages: {', '.join(missing_packages)}")
            logger.info("Please install missing packages using:")
            logger.info(f"pip install {' '.join(missing_packages)}")
            return False
        
        logger.info("✅ All dependencies are installed!")
        return True
    
    def run_tests(self):
        """Run system tests to ensure everything works."""
        logger.info("🧪 Running system tests...")
        
        try:
            result = subprocess.run(
                [sys.executable, "simple_test.py"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("✅ All tests passed!")
                return True
            else:
                logger.error("❌ Some tests failed!")
                logger.error(result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running tests: {e}")
            return False
    
    def start_fastapi_server(self):
        """Start the FastAPI backend server."""
        logger.info("🚀 Starting FastAPI backend server...")
        
        try:
            # Start FastAPI server
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "src.api.server:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ], cwd=self.project_root)
            
            self.processes.append(("FastAPI Server", process))
            logger.info("✅ FastAPI server started on http://localhost:8000")
            logger.info("📚 API Documentation: http://localhost:8000/docs")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting FastAPI server: {e}")
            return False
    
    def start_streamlit_app(self):
        """Start the Streamlit frontend application."""
        logger.info("🎨 Starting Streamlit frontend...")
        
        try:
            # Start Streamlit app
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run",
                "streamlit_app/main.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0"
            ], cwd=self.project_root)
            
            self.processes.append(("Streamlit App", process))
            logger.info("✅ Streamlit app started on http://localhost:8501")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting Streamlit app: {e}")
            return False
    
    def start_research_dashboard(self):
        """Start the research dashboard separately."""
        logger.info("🔬 Starting Research Dashboard...")
        
        try:
            # Start Research Dashboard
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run",
                "streamlit_app/pages/5_Research_Dashboard.py",
                "--server.port", "8502",
                "--server.address", "0.0.0.0"
            ], cwd=self.project_root)
            
            self.processes.append(("Research Dashboard", process))
            logger.info("✅ Research Dashboard started on http://localhost:8502")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting Research Dashboard: {e}")
            return False
    
    def show_system_info(self):
        """Display system information and access URLs."""
        logger.info("\n" + "="*60)
        logger.info("🎉 STARTUP PERFORMANCE PREDICTION SYSTEM")
        logger.info("="*60)
        logger.info("")
        logger.info("📱 ACCESS POINTS:")
        logger.info("  • Main Application:     http://localhost:8501")
        logger.info("  • Research Dashboard:   http://localhost:8502")
        logger.info("  • API Documentation:    http://localhost:8000/docs")
        logger.info("  • API Health Check:     http://localhost:8000/health")
        logger.info("")
        logger.info("🔧 AVAILABLE FUNCTIONALITIES:")
        logger.info("  • Multi-Domain Analysis (10 specialized domains)")
        logger.info("  • Policy Argument Mining & Analysis")
        logger.info("  • Scenario Generation & Simulation")
        logger.info("  • Portfolio Risk Monitoring")
        logger.info("  • Research-Grade Analytics:")
        logger.info("    - Hybrid Modeling (Survival Analysis + ML)")
        logger.info("    - Causal Inference Engine")
        logger.info("    - Graph-Based Risk Networks")
        logger.info("    - Multimodal Data Fusion")
        logger.info("")
        logger.info("📊 STREAMLIT PAGES:")
        logger.info("  1. Dashboard Overview")
        logger.info("  2. Domain Analysis")
        logger.info("  3. Scenario Simulation")
        logger.info("  4. Portfolio Risk Monitor")
        logger.info("  5. Research Dashboard")
        logger.info("")
        logger.info("🛑 To stop the system, press Ctrl+C")
        logger.info("="*60)
    
    def cleanup(self):
        """Clean up all running processes."""
        logger.info("\n🛑 Shutting down system...")
        
        for name, process in self.processes:
            try:
                logger.info(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        logger.info("✅ System shutdown complete")
    
    def run(self):
        """Run the complete system."""
        try:
            # Check dependencies
            if not self.check_dependencies():
                return False
            
            # Run tests
            if not self.run_tests():
                logger.warning("⚠️  Tests failed, but continuing...")
            
            # Start all components
            success = True
            success &= self.start_fastapi_server()
            success &= self.start_streamlit_app()
            success &= self.start_research_dashboard()
            
            if not success:
                logger.error("❌ Failed to start some components")
                return False
            
            # Wait a moment for services to start
            time.sleep(3)
            
            # Show system information
            self.show_system_info()
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
        except Exception as e:
            logger.error(f"❌ System error: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

def main():
    """Main entry point."""
    launcher = SystemLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()








