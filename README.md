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

**Key Finding**:  On AAPL (2010-2023) the strategy returned ~$55k on $10k starting capital, but buy-and-hold returned a ~300k - roughly 5x more than the golden cross strategy. 

- From this I learned that the golden cross strategy underperforms because of how often it sells, forcing me to sit on tons of cash for long stretches of time. Compared to the buy-and-hold stategy that basically never sells and captures all stock growth. 

### UPDATE - June 20, 2026 
I've refactored the code so that it could run the strategy on multiple stocks in a single execution. The backtester now loops through a list of tickers, and runs the full pipeline on each. I've also made the execution more user-friendly. The user controls what they see (trades, metrics, visualizations) rather than getting everything dumped at once.

**Key Finding**: One observation worth pointing out. 

While viewing the stock data for Meta (META 2010-2023) , I noticed that the total profit from the Golden Cross strategy was greater than the Buy and Hold strategy, having a ratio of ~2.7x. The other data I've viewed have all had higher Buy and Hold ratios. Which means the golden cross strategy outperformed. 

Looking at the individual trades I noticed the strategy caught one massive winner between 2013 and 2017 gaining a profit of ~$21,490 at $10k starting capital and only lost ~$8k in the span of 20 years. 

But why did Meta (META) win when Apple (AAPL) Lost by 5x? The answer is volatility. Meta had sharp, avoidable crashes that the death cross helped the strategy evade. Allowing the stocks to be sold before drops and buying back in for recoveries. Apple, by contrast, was a smooth riser. Steady climb with few crashes to avoid, so the same stradegy just missed gains while sitting in cash.
