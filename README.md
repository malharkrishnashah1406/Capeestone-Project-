# Startup Performance Prediction System

A comprehensive system for analyzing startup performance and predicting financial impact of events using domain-specific analysis, Monte Carlo simulation, and policy argument mining.

## 🚀 Features

### Core Components

1. **Domain-Specific Analysis**
   - 10 specialized domains (VC/PE, SaaS, FinTech, HealthTech, etc.)
   - Domain-specific feature extraction and risk modeling
   - Custom simulation responses for each domain

2. **Monte Carlo Simulation Engine**
   - Scenario-based stress testing
   - What-if analysis capabilities
   - Portfolio risk monitoring
   - Correlated shock generation

3. **Policy Argument Mining**
   - Claim detection and stance analysis
   - Argument graph construction
   - Entity linking and frame mining
   - Policy impact assessment

4. **API Layer**
   - FastAPI-based REST API
   - Comprehensive endpoints for all functionality
   - Real-time data processing
   - Integration capabilities

5. **Web Interface**
   - Streamlit-based dashboard
   - Interactive visualizations
   - Real-time monitoring
   - User-friendly controls

### 🔬 Research-Grade Functionalities

6. **Hybrid Modeling (Econometrics + ML)**
   - Survival analysis with Cox Proportional Hazards and Weibull AFT models
   - Machine learning models (XGBoost, LightGBM, Ensemble)
   - Comparative analysis between traditional and ML approaches
   - Research-ready export formats (LaTeX, CSV, JSON)

7. **Causal Inference Engine**
   - DoWhy-style counterfactual analysis
   - Propensity score matching and instrumental variables
   - "What if" scenario analysis for policy impact
   - Robustness checks and sensitivity analysis

8. **Graph-Based Risk Networks**
   - Temporal knowledge graphs for startup ecosystems
   - Shock propagation through network connections
   - Multi-entity relationships (startups, investors, accelerators, policies)
   - Cascade effect analysis and critical node identification

9. **Multimodal Data Fusion**
   - Integration of structured (financial KPIs), unstructured (news, social), and semi-structured (patents, policies) data
   - TF-IDF, LDA, and NMF embeddings for text data
   - Dynamic risk indices similar to VIX for startup domains
   - Real-time risk assessment with multiple data sources

10. **Research Dashboard**
    - Comprehensive research interface with all advanced functionalities
    - Interactive visualizations for model comparisons
    - Export capabilities for academic publications
    - Benchmarking and performance evaluation tools

## 📁 Project Structure

```
├── src/
│   ├── domains/                 # Domain-specific analysis modules
│   │   ├── base.py             # Base domain interface
│   │   ├── venture_capital.py  # VC/PE domain
│   │   ├── saas.py            # SaaS domain
│   │   ├── fintech.py         # FinTech domain
│   │   └── ...                # Other domains
│   ├── simulation/             # Monte Carlo simulation engine
│   │   ├── shocks.py          # Shock generation
│   │   ├── scenario_engine.py # Scenario simulation
│   │   └── domain_response.py # Domain response modeling
│   ├── policy_argument_mining/ # Policy analysis
│   │   ├── ingestion.py       # Document ingestion
│   │   ├── claim_detection.py # Claim detection
│   │   ├── stance_detection.py # Stance analysis
│   │   └── ...                # Other mining components
│   ├── api/                   # FastAPI application
│   │   ├── server.py          # Main API server
│   │   └── routes/            # API endpoints
│   ├── utils/                 # Utility functions
│   │   ├── validators.py      # Data validation
│   │   ├── helpers.py         # Helper functions
│   │   └── registry.py        # Domain registry
│   ├── research/              # Research-grade functionalities
│   │   ├── hybrid_models.py   # Hybrid modeling (Econometrics + ML)
│   │   ├── causal_inference.py # Causal inference engine
│   │   ├── graph_networks.py  # Graph-based risk networks
│   │   └── multimodal_fusion.py # Multimodal data fusion
│   └── main.py               # Streamlit main application
├── streamlit_app/
│   ├── pages/                # Streamlit pages
│   │   ├── 1_Domain_Analysis.py
│   │   ├── 2_Scenario_Simulation.py
│   │   ├── 3_Policy_Analysis.py
│   │   ├── 4_Portfolio_Risk_Monitor.py
│   │   └── 5_Research_Dashboard.py
│   └── Home.py               # Main dashboard
├── tests/                    # Comprehensive test suite
├── config/                   # Configuration files
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd startup-performance-prediction
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database credentials
   ```

## 🚀 Quick Start

### Run the Streamlit Application
```bash
streamlit run src/main.py
```

### Run the FastAPI Server
```bash
cd src
uvicorn api.server:app --reload
```

### Research Dashboard
```bash
cd streamlit_app
streamlit run pages/5_Research_Dashboard.py
```

### Run Tests
```bash
python simple_test.py
```

## 🔬 Research Capabilities

### Hybrid Modeling
- **Survival Analysis**: Cox Proportional Hazards, Weibull AFT, Kaplan-Meier
- **Machine Learning**: XGBoost, LightGBM, Ensemble methods
- **Comparative Analysis**: Traditional vs ML approaches with statistical significance testing
- **Export Formats**: LaTeX tables, CSV data, JSON metadata for research papers

### Causal Inference
- **Counterfactual Analysis**: "What if" scenarios for policy impact assessment
- **Estimation Methods**: Propensity score matching, exact matching, regression adjustment, instrumental variables
- **Robustness Checks**: Sensitivity analysis, placebo tests, subgroup analysis
- **Research Outputs**: Effect sizes, confidence intervals, p-values, causal graphs

### Graph Networks
- **Temporal Knowledge Graphs**: Multi-entity relationships over time
- **Shock Propagation**: Network-based risk transmission modeling
- **Cascade Analysis**: Critical node identification and impact assessment
- **Visualization**: Interactive network graphs and propagation maps

### Multimodal Fusion
- **Data Integration**: Structured (financial), unstructured (news/social), semi-structured (patents/policies)
- **Embedding Methods**: TF-IDF, Latent Dirichlet Allocation (LDA), Non-negative Matrix Factorization (NMF)
- **Dynamic Indices**: Real-time risk indices similar to financial volatility indices
- **Feature Importance**: SHAP-style explanations for risk predictions

## 📊 Domain Analysis

The system supports 10 specialized domains:

1. **Venture Capital / Private Equity**
   - Fund performance metrics
   - Portfolio company health
   - Market dynamics analysis

2. **SaaS**
   - ARR growth analysis
   - Churn prediction
   - Unit economics modeling

3. **FinTech**
   - Transaction volume analysis
   - Regulatory compliance
   - Fraud detection

4. **HealthTech/Biotech**
   - Clinical trial analysis
   - Regulatory approval prediction
   - R&D pipeline assessment

5. **GreenTech**
   - Carbon pricing exposure
   - ESG compliance
   - Climate risk assessment

6. **RegTech/Policy**
   - Regulatory compliance scoring
   - Policy advocacy effectiveness
   - Stakeholder network analysis

7. **Cross-Border**
   - Geographic diversification
   - Currency exposure
   - Regulatory complexity

8. **Public Sector Funded**
   - Government funding analysis
   - Policy alignment scoring
   - Bureaucratic complexity

9. **MediaTech/PoliticalTech**
   - Content moderation scale
   - Political sensitivity
   - User engagement metrics

10. **Accelerators**
    - Cohort success rates
    - Network strength
    - Funding availability

## 🎯 Simulation Capabilities

### Scenario Types
- **Severe Recession**: Economic downturn with market crash
- **Tech Regulation**: Regulatory changes and cybersecurity breaches
- **Trade Conflict**: Trade wars and political instability
- **Climate Crisis**: Extreme weather and regulatory changes
- **Pandemic Response**: Public health emergencies
- **Liquidity Crisis**: Policy rate changes and market crash
- **Black Swan**: Multiple simultaneous shocks

### Monte Carlo Features
- 1000+ iterations per scenario
- Correlated shock generation
- Domain-specific response modeling
- Risk metric calculation (VaR, CVaR)
- Portfolio-level aggregation

## 🔍 Policy Analysis

### Argument Mining Pipeline
1. **Document Ingestion**: Parse policy documents and transcripts
2. **Preprocessing**: Clean and normalize text
3. **Claim Detection**: Identify assertions and arguments
4. **Stance Detection**: Determine support/oppose/neutral positions
5. **Role Labeling**: Classify argument roles (claim, premise, attack)
6. **Frame Mining**: Detect narrative frames and themes
7. **Entity Linking**: Link mentions to known entities
8. **Graph Construction**: Build argument networks
9. **Scoring**: Calculate salience, credibility, uncertainty

### Analysis Features
- Real-time policy monitoring
- Impact assessment on different domains
- Stakeholder analysis
- Compliance tracking
- Timeline management

## 📈 API Endpoints

### Domains
- `GET /api/v1/domains/` - List all domains
- `GET /api/v1/domains/{domain_key}` - Get domain info
- `POST /api/v1/domains/{domain_key}/simulate` - Run domain simulation

### Scenarios
- `POST /api/v1/scenarios/run` - Run custom scenario
- `POST /api/v1/scenarios/run/{scenario_name}` - Run predefined scenario
- `POST /api/v1/scenarios/what-if` - What-if analysis

### Portfolios
- `POST /api/v1/portfolios/` - Create portfolio
- `POST /api/v1/portfolios/{portfolio_id}/simulate` - Portfolio simulation
- `GET /api/v1/portfolios/{portfolio_id}/exposure` - Domain exposure

### Arguments
- `POST /api/v1/arguments/ingest` - Ingest policy document
- `POST /api/v1/arguments/analyze` - Analyze arguments
- `GET /api/v1/arguments/graph` - Get argument graph

### Policies
- `POST /api/v1/policies/` - Create policy
- `POST /api/v1/policies/{policy_id}/analyze` - Policy analysis
- `GET /api/v1/policies/{policy_id}/impact` - Impact analysis

## 🧪 Testing

The system includes comprehensive tests:

```bash
# Run simple tests
python simple_test.py

# Run full test suite
python run_tests.py

# Run specific test modules
python -m unittest tests.test_domains
python -m unittest tests.test_simulation
python -m unittest tests.test_utils
```

## 🔧 Configuration

### Environment Variables
```bash
# API Keys
NEWS_API_KEY=your_news_api_key
GNEWS_API_KEY=your_gnews_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### Domain Configuration
Edit `config/domains.yaml` to customize domain parameters:
```yaml
venture_capital:
  risk_factors:
    - liquidity_tightening
    - rate_hikes
    - exit_window_closure
  features:
    - dry_powder
    - fund_age_years
    - dpi
```

## 📊 Data Sources

### News and Events
- NewsAPI for real-time news
- GNews for global news coverage
- Web scraping for specific sources
- RSS feeds for continuous monitoring

### Policy Documents
- Government websites
- Regulatory agency publications
- Parliamentary transcripts
- Central bank communications

### Market Data
- Financial APIs (YFinance)
- Economic indicators
- Currency exchange rates
- Commodity prices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test examples

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core domain analysis
- ✅ Basic simulation engine
- ✅ Policy argument mining
- ✅ API framework
- ✅ Web interface

### Phase 2 (Next)
- 🔄 Advanced ML models
- 🔄 Real-time data streaming
- 🔄 Advanced visualizations
- 🔄 Mobile app

### Phase 3 (Future)
- 📋 Blockchain integration
- 📋 AI-powered insights
- 📋 Predictive analytics
- 📋 Enterprise features

---

**Built with ❤️ for startup ecosystem analysis** 