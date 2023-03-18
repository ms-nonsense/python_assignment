CREATE DATABASE IF NOT EXISTS python_exercise;
CREATE TABLE IF NOT EXISTS python_exercise.financial_data (
    symbol          VARCHAR(20)     NOT NULL,
    date            DATE            NOT NULL,
    open_price      DECIMAL(8, 4)   SIGNED  NOT NULL,
    close_price     DECIMAL(8, 4)   SIGNED  NOT NULL,
    volume          INT             SIGNED NOT NULL,
    PRIMARY KEY (symbol, date)
);