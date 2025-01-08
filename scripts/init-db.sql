-- Initialize database schema

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL,
    metric_type VARCHAR(20) NOT NULL,
    value JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on coin_id and timestamp
CREATE INDEX IF NOT EXISTS idx_metrics_coin_timestamp 
    ON metrics(coin_id, timestamp);

-- Analysis results cache
CREATE TABLE IF NOT EXISTS analysis_cache (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- Create index on cache lookup
CREATE INDEX IF NOT EXISTS idx_analysis_cache_lookup 
    ON analysis_cache(coin_id, timeframe, expires_at);