# Trading Backtester 

This repository serves as the home for my first quantitative finance project — a trading backtester built in Python.

## Project Overview

This project simulates and evaluates a moving average crossover trading strategy (Golden Cross) on S&P 500 stock data. It is designed to analyze historical performance and compare results against a buy-and-hold benchmark.

Designed as a "learn as you go" built progressively as I develop my skills in Python and data analysis.

Tyre Bolton -- CS @ University of Maryland

### UPDATE - June 20, 2026 
Over the past 2 weeks I have spent time building the core of the backtester. So far it: 

- Pulls historical stock data using yfinance 
-- I took time to learn how to properly use yfinance and explored various stock data (AAPL, TSLA, ect.)
- Calculates 50-day and 200-day Moving Average (MA) to find trends 
- Generates signals based on MA trends 
-- if 50-day MA crosses above 200-day MA (golden cross) a buy signal is generated 
-- if 50-day MA crossed below 200-day MA  (death cross) a sell signal is generated
- Simulates trades based on signals and a starting cash amount chosen by the trader
- Calculates performance metrics (win rate, average win/loss, max drawdown)
- Compares strategy against a buy-and-hold benchmark
- Visualizes price, moving averages, and trade signals with matplotlib 

**Key Finding**:  On AAPL (2012-2023) the strategy returned ~$55k on $10k starting capital, but buy-and-hold returned a ~300k - roughly 5x more than the golden cross strategy. 

- From this I learned that the golden cross strategy underperforms because of how often it sells, forcing me to sit on tons of cash for long stretches of time. Compared to the buy-and-hold stategy that basically never sells and captures all stock growth. 

### UPDATE-2 - June 20, 2026
I've refactored the code so that it could run the strategy on multiple stocks in a single execution. The backtester now loops through a list of tickers, and runs the full pipeline on each. I've also made the execution more user-friendly. The user controls what they see (trades, metrics, visualizations) rather than getting everything dumped at once.

**Key Finding**: One observation worth pointing out. 

While viewing the stock data for Meta (2012-2023), I noticed that the total profit from the Golden Cross strategy was greater than the Buy and Hold strategy, having a ratio of ~2.7x. The other data I've viewed have all had higher Buy and Hold ratios. Which means the golden cross strategy outperformed. 

Looking at the individual trades I noticed the strategy caught one massive winner between 2013 and 2017 gaining a profit of ~$21,490 at $10k starting capital and only lost ~$8k in the span of 20 years. 

But why did Meta (META) win when Apple (AAPL) Lost by 5x? The answer is volatility. Meta had sharp, avoidable crashes that the death cross helped the strategy evade. Allowing the stocks to be sold before drops and buying back in for recoveries. Apple, by contrast, was a smooth riser. Steady climb with few crashes to avoid, so the same stradegy just missed gains while sitting in cash.


### UPDATE-3 - August 7, 2026 
The final phase of my project is complete. Moved past single stock backtesting into looking at how a basket of stocks relate to each other. A correlation network built with networkx/

What it does: 

- Pulls daily return correlations across n-stock baskets. For this example, I used 12 stocks spanning tech, banking, energ, and consuemer staples (AAPL, GOOGL, META, MSFT, XOM, CVX, JPM, BAC, GS, PEP, KO, WMT) c.

- Converts correlation into a distance metric using Mantegna's transform (sqrt(2 * (1 - correlation))), so strongly correlated stocks end up "close" and weakly correlated stocks end up "far"
Builds a full weighted graph, then extracts the Minimum Spanning Tree 

- the cheapest set of connections that still links every stock, cutting out the redundant ones -- with N stocks, the MST always has exactly N-1 edges, no cycles

- Runs Louvain community detection to find natural clusters, without ever telling the algorithm what sector each stock belongs to

**Key Finding**: On the 5 stock tech basket (AAPL, MSFT, GOOGL, META, AMZN), GOOGL came out as the hub of the minimum spanning tree. Meaning it is the most broadly corralated name in connected to all 4 other stcks correlated name in that group. Everyone else only connected to GOOGL, not to each other directly.

Working on the community detection almost tripped me up. My first version fed distance values into a Louvain optimization algorithm, and it kept returning one giant community no matter what stocks I used. After a while of troubleshooting. I discovered that Louvain expects bigger weight = morer relaated(similarity) instead of distance, where smaller = more related. 

Fix ended up being simpler than the workaround I was trying: skip distance entirely for this step and just feed Louvain the correlation matrix directly, since correlation already is a similarity measure. Once I did that, running it on the 12-stock basket gave real, clean sector structure:

- Tech (AAPL, GOOGL, META, MSFT) - one community
- Banks (JPM, BAC, GS) - one community
- Energy + consumer staples (XOM, CVX, PEP, KO, WMT) - merged into one community rather than splitting

That last one is the interesting part - CVX/XOM were the single strongest pair in the whole matrix (0.84 correlation), but the algorithm still didn't peel them off into their own group separate from staples. Best explanation: the gap between "energy vs staples" wasn't sharp enough for modularity to justify the split, unlike tech and banks which were both clearly, tightly self-contained. Noting that as a real result rather than smoothing over it - not every sector boundary is going to show up cleanly just because GICS says it should exist.
