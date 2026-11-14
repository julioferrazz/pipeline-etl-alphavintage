CREATE TABLE IF NOT EXISTS daily_stock_prices (
    date DATE,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT,
    symbol VARCHAR,
    PRIMARY KEY (symbol, date)
);