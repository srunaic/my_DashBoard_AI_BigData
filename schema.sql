CREATE DATABASE IF NOT EXISTS dashboard_db;
USE dashboard_db;

-- 1. Raw Data Layer: Stores original data sources exactly as fetched
CREATE TABLE IF NOT EXISTS macro_raw (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    value DECIMAL(18, 6),
    unit VARCHAR(20),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_raw_entry (date, symbol)
);

-- 2. Derived Data Layer: Stores calculated business metrics
CREATE TABLE IF NOT EXISTS macro_derived (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    metric VARCHAR(50) NOT NULL,
    value DECIMAL(18, 2),
    calculation_version VARCHAR(20) DEFAULT 'v1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_derived_entry (date, metric)
);

-- 3. Analysis/Signals Layer: Stores Regime and Decisions
CREATE TABLE IF NOT EXISTS market_regime (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    regime_type VARCHAR(50),
    confidence_score FLOAT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PHASE 2 ADDITIONS ----------------------------------------

-- 4. Domestic Market Raw (Physical Prices)
CREATE TABLE IF NOT EXISTS domestic_market_raw (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    price_type VARCHAR(20) NOT NULL, -- 'BUYing' (살때), 'SELLing' (팔때)
    value DECIMAL(18, 2) NOT NULL,   -- Price in KRW per 3.75g (usually)
    unit VARCHAR(20) DEFAULT 'KRW/3.75g',
    source VARCHAR(50) DEFAULT 'KOREA_GOLD_EXCHANGE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_domestic_entry (date, price_type, source)
);

-- 5. Market Premium Derived (Distortion Analysis)
CREATE TABLE IF NOT EXISTS market_premium_derived (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    theoretical_price DECIMAL(18, 2), -- Calculated from Intl Spot * FX
    physical_price DECIMAL(18, 2),    -- From domestic_market_raw
    premium_amount DECIMAL(18, 2),    -- Physical - Theoretical
    premium_rate FLOAT,               -- (Physical/Theoretical - 1) * 100
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_premium_entry (date)
);
