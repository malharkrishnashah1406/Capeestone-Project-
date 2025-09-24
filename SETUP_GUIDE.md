# 🚀 Startup Performance Prediction System - Setup Guide

## 📋 Prerequisites

- **Python 3.8+** (3.11 recommended)
- **Git** (for cloning the repository)
- **8GB+ RAM** (recommended for research features)
- **Windows 10/11, macOS, or Linux**

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd startup-performance-prediction-system
```

### 2. Install Dependencies

#### Option A: Using requirements.txt (Recommended)
```bash
pip install -r requirements.txt
```

#### Option B: Install Core Dependencies Only
```bash
pip install numpy pandas plotly streamlit fastapi uvicorn python-dotenv pyyaml networkx scikit-learn xgboost lightgbm lifelines matplotlib seaborn scipy
```

### 3. Verify Installation
```bash
python simple_test.py
```
You should see: `🎉 All simple tests passed!`

## 🚀 Running the Complete System

### Method 1: Automated Startup (Recommended)
```bash
python run_system.py
```

### Method 2: Windows Batch File
Double-click `start_system.bat` or run:
```cmd
start_system.bat
```

### Method 3: Manual Startup (Advanced)

#### Start FastAPI Backend:
```bash
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
```

#### Start Streamlit Main App:
```bash
streamlit run streamlit_app/main.py --server.port 8501
```

#### Start Research Dashboard:
```bash
streamlit run streamlit_app/pages/5_Research_Dashboard.py --server.port 8502
```

## 🌐 Access Points

Once the system is running, you can access:

| Component | URL | Description |
|-----------|-----|-------------|
| **Main Application** | http://localhost:8501 | Complete system interface |
| **Research Dashboard** | http://localhost:8502 | Advanced research features |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **API Health Check** | http://localhost:8000/health | System status |

## 📊 Available Functionalities

### 🏢 Multi-Domain Analysis
- **10 Specialized Domains**: VC, SaaS, FinTech, HealthTech, GreenTech, RegTech, Cross-Border, Public Sector, MediaTech, Accelerators
- **Domain-Specific Risk Models**
- **Cross-Domain Interactions**

### 🔍 Policy Argument Mining
- **Claim Detection**: Extract policy arguments and evidence
- **Stance Detection**: Identify support/opposition
- **Argument Role Labeling**: Classify argument components
- **Frame Mining**: Extract policy narratives
- **Entity Linking**: Connect arguments to real-world entities

### 🎯 Scenario Simulation
- **8 Shock Types**: Policy changes, market crashes, pandemics, trade wars, etc.
- **Multi-jurisdictional Coverage**: US, EU, UK, JP, CA, CN
- **Monte Carlo Simulations**: Probabilistic scenario generation
- **What-if Analysis**: Policy impact assessment

### 📈 Portfolio Risk Monitoring
- **Real-time Risk Assessment**
- **Portfolio Optimization**
- **Risk-Adjusted Returns**
- **Stress Testing**

### 🔬 Research-Grade Analytics
- **Hybrid Modeling**: Survival Analysis + Machine Learning
- **Causal Inference**: Policy effect estimation
- **Graph-Based Risk Networks**: Ecosystem modeling
- **Multimodal Data Fusion**: Comprehensive data integration

## 📱 Streamlit Pages

1. **Dashboard Overview**: System-wide metrics and insights
2. **Domain Analysis**: Specialized domain risk assessment
3. **Scenario Simulation**: Shock generation and impact analysis
4. **Portfolio Risk Monitor**: Real-time portfolio monitoring
5. **Research Dashboard**: Advanced research functionalities

## 🔧 API Endpoints

### Core Endpoints
- `GET /` - System status
- `GET /health` - Health check
- `GET /api/v1/status` - API status

### Domain Management
- `GET /api/v1/domains/` - List domains
- `GET /api/v1/domains/{domain_id}` - Get domain details
- `POST /api/v1/domains/` - Create domain

### Scenario Management
- `GET /api/v1/scenarios/` - List scenarios
- `POST /api/v1/scenarios/` - Create scenario
- `GET /api/v1/scenarios/{scenario_id}` - Get scenario details

### Policy Analysis
- `GET /api/v1/policies/` - List policies
- `POST /api/v1/policies/` - Create policy
- `POST /api/v1/policies/{policy_id}/analyze` - Analyze policy

### Argument Mining
- `POST /api/v1/arguments/analyze` - Analyze arguments
- `GET /api/v1/arguments/graph` - Get argument graph
- `GET /api/v1/arguments/claims` - Get claims

## 🧪 Testing

### Run All Tests
```bash
python simple_test.py
```

### Run Individual Components
```bash
# Test domains
python -c "from src.domains.venture_capital import VentureCapitalDomain; print('Domains OK')"

# Test simulation
python -c "from src.simulation.shocks import ShockGenerator; print('Simulation OK')"

# Test API
python -c "from src.api.server import app; print('API OK')"
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure you're in the project root directory
cd /path/to/startup-performance-prediction-system

# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### 2. Port Already in Use
```bash
# Kill processes using the ports
lsof -ti:8000 | xargs kill -9  # FastAPI
lsof -ti:8501 | xargs kill -9  # Streamlit main
lsof -ti:8502 | xargs kill -9  # Research dashboard
```

#### 3. Missing Dependencies
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### 4. Memory Issues
- Close other applications
- Reduce the number of concurrent simulations
- Use smaller datasets for testing

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 4GB | 8GB+ |
| **CPU** | 2 cores | 4+ cores |
| **Storage** | 2GB | 5GB+ |
| **Python** | 3.8 | 3.11 |

## 📚 Usage Examples

### 1. Basic Domain Analysis
```python
from src.domains.venture_capital import VentureCapitalDomain

domain = VentureCapitalDomain()
risk_score = domain.calculate_risk_score({
    'funding_round': 'Series A',
    'team_size': 15,
    'market_cap': 1000000
})
print(f"Risk Score: {risk_score}")
```

### 2. Scenario Generation
```python
from src.simulation.shocks import ShockGenerator

generator = ShockGenerator()
shock = generator.generate_random_shock()
print(f"Generated shock: {shock.type}")
```

### 3. Policy Analysis
```python
from src.policy_argument_mining import PolicyIngestion

ingestion = PolicyIngestion()
document = ingestion.create_document(
    title="Sample Policy",
    content="This policy regulates financial services...",
    source="government"
)
```

## 🔄 Development

### Project Structure
```
startup-performance-prediction-system/
├── src/                          # Source code
│   ├── api/                      # FastAPI backend
│   ├── domains/                  # Domain-specific modules
│   ├── simulation/               # Scenario simulation
│   ├── policy_argument_mining/   # Policy analysis
│   ├── research/                 # Research features
│   └── utils/                    # Utilities
├── streamlit_app/                # Streamlit frontend
├── tests/                        # Test files
├── run_system.py                 # Main startup script
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

### Adding New Features
1. Create your module in the appropriate `src/` directory
2. Add tests in `tests/`
3. Update API routes if needed
4. Add Streamlit interface if applicable
5. Update documentation

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Run `python simple_test.py` to verify system health
3. Check the API documentation at http://localhost:8000/docs
4. Review the logs for error messages

## 🎯 Next Steps

1. **Explore the Main Application**: Start with http://localhost:8501
2. **Try the Research Dashboard**: Access http://localhost:8502
3. **Test the API**: Visit http://localhost:8000/docs
4. **Run Sample Scenarios**: Use the scenario simulation page
5. **Analyze Policies**: Upload policy documents for analysis

---

**🎉 Congratulations!** Your startup performance prediction system is now running with all functionalities working together!








