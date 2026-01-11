# 🏦 AI & Big Data Macro-Economic Analysis System
**(귀금속·화폐 가치 기반 거시경제 분석 및 의사결정 지원 시스템)**

An enterprise-grade dashboard that monitors **Gold, Silver, Currency Values (DXY, KRW), and Macro Indicators (CPI, Rates)** to determine market regimes (Risk-On/Off) and support management decisions.

## 🚀 Key Features

### 1. Automated Data Pipeline (`src/pipeline`)
- **Real-time Market Data**: Fetches Gold, Silver, S&P 500, DXY, USD/KRW using `yfinance`.
- **Macro Economics**: Auto-fetches US CPI, M2 Money Supply, Interest Rates via `fredapi`.
- **Robust Ingestion**: Type-safe ingestion into MySQL database with historical data support.

### 2. Market Regime Analysis (`src/analysis/regime.py`)
- **Rule-Based Classification**: Automatically detects market states:
    - 🟢 **Risk-On (Growth)**: Stock Market Rally + Weak Dollar
    - 🔴 **Risk-Off (Fear)**: Stock Drop + Strong Gold/Dollar
    - 🛡️ **Inflation Hedge**: Rising Gold + Weak Dollar
    - 📉 **Deflation**: Strong Dollar + Falling Assets
- **Ambiguity Handling**: Robust logic to handle data outliers and scalar comparisons.

### 3. Financial Metrics (`src/analysis/calculators.py`)
- **Real Gold Price**: Calibrated for inflation (CPI).
- **Correlation Analysis**: Dynamic asset correlations (e.g., Gold vs. Interest Rates).

### 4. Interactive Dashboard (`app.py`)
- **KPI Cards**: Live price updates.
- **Traffic Light System**: Instant visual feedback on Market Regime.
- **Streamlit UI**: Clean, responsive interface for data exploration.

---

## 🛠️ Technology Stack
- **Language**: Python 3.10+
- **Framework**: Streamlit
- **Data Source**: Yahoo Finance, Federal Reserve Economic Data (FRED)
- **Database**: MySQL (XAMPP/Local)
- **Visualization**: Plotly, Streamlit Native Charts
- **Infrastructure**: GitHub Actions (CI/CD)

---

## ⚙️ How to Run Locally

### 1. Prerequisites
- Python 3.8+ installed
- XAMPP (MySQL) running on Port 3306
- FRED API Key (Get it from [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html))

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/srunaic/my_DashBoard_AI_BigData.git
cd my_DashBoard_AI_BigData

# Create Virtual Environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=dashboard_db
FRED_API_KEY=your_api_key_here
```

### 4. Database Setup
```bash
# Run schema migration script
python src/pipeline/setup_db.py

# Ingest historical data
python src/pipeline/ingest.py
```

### 5. Launch Dashboard
```bash
streamlit run app.py
```

---

## 📊 Folder Structure
```
D:\Github\DashBoard_AI_BigData\
├── src/
│   ├── analysis/       # Business Logic (Regime, Metrics)
│   ├── modules/        # Utility Connectors (DB)
│   ├── pipeline/       # Data Ingestion (Collector, Ingest)
│   └── ui/             # Dashboard Views
├── data/               # Local Data Cache
├── .github/workflows/  # CI/CD Configuration
├── app.py              # Main Entry Point
├── schema.sql          # Database Schema
└── requirements.txt    # Dependencies
```

## 📅 Roadmap
- [x] Data Pipeline Implementation
- [x] Market Regime Classification
- [ ] AI Trend Prediction (Prophet/LSTM)
- [ ] Simulation Scenarios
- [ ] User Alert System

---
*Built for High-Level Decision Support.*
