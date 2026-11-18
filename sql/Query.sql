CREATE TABLE IF NOT EXISTS daily_stock_prices (
    date DATE,
    open NUMERIC(10,2),
    high NUMERIC(10,2),
    low NUMERIC(10,2),
    close NUMERIC(10,2),
    volume BIGINT,
    symbol VARCHAR,
    PRIMARY KEY (symbol, date)
);

INSERT INTO daily_stock_prices (date, open, high, low, close, volume, symbol)
SELECT date, open, high, low, close, volume, symbol FROM staging_stock_prices
ON CONFLICT (symbol, date) DO UPDATE 
SET open = EXCLUDED.open,
    high = EXCLUDED.high,
    low = EXCLUDED.low,
    close = EXCLUDED.close,
    volume = EXCLUDED.volume;