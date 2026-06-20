# Trading Backtester 

This repository serves as the home for my first quantitative finance project — a trading backtester built in Python.

## Project Overview

This project simulates and evaluates a moving average crossover trading strategy (Golden Cross) on S&P 500 stock data. It is designed to analyze historical performance and compare results against a buy-and-hold benchmark.

-- > Designed as a "learn as you go" built progressively as I develop my skills in Python and data analysis 

Tyre Bolton -- CS @ University of Maryland

### UPDATE - June 20, 2026 
Over the past 2 weeks I have spent time building the core of the backtester. So far it: 

- Pulls historical stock data using yfinance 
-- Took time to learn how to properly use yfinance and explored various stock data (AAPL, TSLA, ect.)
- Calculates 50-day and 200-day Moving Average (MA) to find trends 
- Generates signals based on MA trends 
-- if 50-day MA crosses above 200-day MA (golden cross) a buy signal is generated 
-- if 50-day MA crossed below 200-day MA  (death cross) a sell signal is generated
- Simulates trades based on signals and a starting cash amount chosen by the trader
- Calculates performance metrics (win rate, average win/loss, max drawdown)
- Compares strategy against a buy-and-hold benchmark
- Visualizes price, moving averages, and trade signals with matplotlib 

**Key Finding so far**:  On AAPL (2000-2020) the strategy returned ~$95k on $10k starting capital, but buy-and-hold returned a whopping ~$1.55M - roughly 16x more than the golden cross strategy. 
- From this I learned that the golden cross strategy underperforms because of how often it sells, forcing me to sit on tons of cash for long stretches of time. Compared to the buy-and-hold stategy that basically never sells and captures all stock growth. 
