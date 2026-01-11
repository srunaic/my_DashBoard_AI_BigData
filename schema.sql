CREATE DATABASE IF NOT EXISTS dashboard_db;
USE dashboard_db;

-- 1. Raw Data Layer: Stores original data sources exactly as fetched
-- Intended for Auditability and Data Lake concept
CREATE TABLE IF NOT EXISTS macro_raw (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    symbol VARCHAR(50) NOT NULL,    -- GOLD_USD_OZ, SILVER_USD_OZ, USDKRW, CPI_INDEX, etc.
    value DECIMAL(18, 6),           -- High precision for raw values
    unit VARCHAR(20),               -- USD/oz, KRW, index, %
    source VARCHAR(50),             -- yfinance, FRED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_raw_entry (date, symbol)
);

-- 2. Derived Data Layer: Stores calculated business metrics
-- "Gold 1 Don (KRW)" lives here.
CREATE TABLE IF NOT EXISTS macro_derived (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    metric VARCHAR(50) NOT NULL,    -- GOLD_KRW_DON, SILVER_KRW_DON, REAL_GOLD_PRICE
    value DECIMAL(18, 2),           -- Final values for display (usually currency)
    calculation_version VARCHAR(20) DEFAULT 'v1.0', -- To track formula changes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_derived_entry (date, metric)
);

-- 3. Analysis/Signals Layer: Stores Regime and Decisions
CREATE TABLE IF NOT EXISTS market_regime (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    regime_type VARCHAR(50), -- Risk-On, Risk-Off
    confidence_score FLOAT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Legacy tables - kept for reference or migration, but deprecating in favor of macro_raw/derived
-- market_data (Deprecated)
-- macro_indicators (Deprecated)
