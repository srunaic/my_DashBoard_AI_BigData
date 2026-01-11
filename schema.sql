CREATE DATABASE IF NOT EXISTS dashboard_db;
USE dashboard_db;

-- Table for Raw Market Data (Daily/Intraday)
CREATE TABLE IF NOT EXISTS market_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    close_price DECIMAL(18, 4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date_symbol (date, symbol)
);

-- Table for Macro Indicators (Monthly/Weekly)
CREATE TABLE IF NOT EXISTS macro_indicators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    indicator_name VARCHAR(50) NOT NULL, -- e.g., 'CPI', 'M2'
    value DECIMAL(18, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date_indicator (date, indicator_name)
);

-- Table for Derived Analysis/Signals
CREATE TABLE IF NOT EXISTS market_regime (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    regime_type VARCHAR(50), -- 'Risk-On', 'Inflation_Hedge', etc.
    confidence_score FLOAT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
