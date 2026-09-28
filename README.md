# Trading Backtester 

This repository serves as the home for my first quantitative finance project — a trading backtester built in Python.

## Project Overview

This project simulates and evaluates a moving average crossover trading strategy (Golden Cross) on 12 stocks across 4 sectors from 2015-2025 and compares it to a buy-and-hold strategy on profit and max drawdown. It also builds a correlation network, using minimum a spanning tree and community detection, to map how the stocks move together.  


### UPDATE-1 June 20th, 2026
I have spent time building the core of the backtester. So far it: 

- Pulls historical stock data using yfinance 
-- I took time to learn how to properly use yfinance and explored various stock data (AAPL, GOOGL, ect.)
- Calculates 50-day and 200-day Moving Average (MA) to find trends 
- Generates signals based on MA trends 
-- if 50-day MA crosses above 200-day MA (golden cross) a buy signal is generated 
-- if 50-day MA crossed below 200-day MA  (death cross) a sell signal is generated
- Simulates trades based on signals and a starting cash amount chosen by the trader
- Calculates performance metrics (win rate, average win/loss, max drawdown)
- Compares strategy against a buy-and-hold benchmark
- Visualizes price, moving averages, and trade signals with matplotlib 

~~**Key Finding**:  On AAPL (2012-2023) the strategy returned ~$55k on $10k starting capital, but buy-and-hold returned a ~300k - roughly 5x more than the golden cross strategy~~

> **Susprsed (see UPDATE-4):**  this compared strategy *profit* to buy-and-hold *total-value* with starting cash included. After fixing the bug and rerunning on 2015-2025, I gathered new results: Strategy made 0.29x of buy-and-hold profit. 
>
- ~~From this I learned that the golden cross strategy underperforms because of how often it sells, forcing me to sit on tons of cash for long stretches of time. Compared to the buy-and-hold stategy that basically never sells and captures all stock growth.~~
  
- **Revised (see UPDATE-4): ** On AAPL, trade frequency was not the issue. AAPL only had 6 trades. The death cross sold on Dec 24, 2018 at $34.81. The stock bottomed under 3.2% lower on Jan 3,2019, then the strategy re-enterned in May at $48.30, 39% above its exit. It avoided a 3% drop and missed a 39% recovery. Because moving averages are built from past prices, a slow 50/200 crossover only confirms a move after most of it has already happened

### UPDATE-2 June 20, 2026
I've refactored the code so that it could run the strategy on multiple stocks in a single execution. The backtester now loops through a list of tickers, and runs the full pipeline on each. I've also made the execution more user-friendly. 

**Key Finding**: One observation worth pointing out. 

~~While viewing the stock data for Meta (2012-2023), I noticed that the total profit from the Golden Cross strategy was greater than the Buy and Hold strategy, having a ratio of ~2.7x. The other data I've viewed have all had higher Buy and Hold ratios. Which means the golden cross strategy outperformed.~~

~~Looking at the individual trades I noticed the strategy caught one massive winner between 2013 and 2017 gaining a profit of ~$21,490 at $10k starting capital and only lost ~$8k in the span of 20 years.~~ 

**Superseded (see UPDATE-4):** the 2.7x came from bugd in my benchmark comparison. The ratio didn't show which side won, and buy-and-hold included starting cash while the strategy didn't. Corrected 2015-2025 results: the strategy made **0.47x** of buy-and-hold's profit. 


~~But why did Meta (META) win when Apple (AAPL) Lost by 5x? The answer is volatility. Meta had sharp, avoidable crashes that the death cross helped the strategy evade. Allowing the stocks to be sold before drops and buying back in for recoveries. Apple, by contrast, was a smooth riser. Steady climb with few crashes to avoid, so the same stradegy just missed gains while sitting in cash.~~ 
**Superseded (see UPDATE-4):** Though this gathered information came from a error, the volatility intuition still holds up partly. META had the deepest crash of all 12 stocks (-77% in  2022). The death cross sold at $331 and sat out the entire fall to $88. 

The real difference was not how *sharp* the crashes were, it was how *long* the crashes were. META's 2022 decline lasted most of the year, long enough for the slow 50/200 to get out early. AAPL's 2018 selloff only lasted 3 months, so by the time the death cross fired, the crash was nearly over.



### UPDATE-3 - August 7, 2026 
The final phase of my project is complete. Moved past single stock backtesting into looking at how a basket of stocks relate to each other. A correlation network built with networkx.

What it does: 

- Pulls daily return correlations across n-stock baskets. For this example, I used 12 stocks spanning tech, banking, energy, and consuemer staples (AAPL, GOOGL, META, MSFT, XOM, CVX, JPM, BAC, GS, PEP, KO, WMT).

- Converts correlation into a distance metric using Mantegna's transform (sqrt(2 * (1 - correlation))), so strongly correlated stocks end up "close" and weakly correlated stocks end up "far"
Builds a full weighted graph, then extracts the Minimum Spanning Tree 

- the cheapest set of connections that still links every stock, cutting out the redundant ones -- with N stocks, the MST always has exactly N-1 edges, no cycles

- Runs Louvain community detection to find natural clusters, without ever telling the algorithm what sector each stock belongs to

**Key Finding**: On (AAPL, MSFT, GOOGL, META), GOOGL came out as the hub of the minimum spanning tree. Meaning it is the most broadly correlated name in connected to all 3 other stocks correlated name in that group. Everyone else only connected to GOOGL, not to each other directly.

Working on the community detection almost tripped me up. My first version fed distance values into a Louvain optimization algorithm, and it kept returning one giant community no matter what stocks I used. After a while of troubleshooting. I discovered that Louvain expects bigger weight = more related(similarity) instead of distance, where smaller = more related. 

Fix ended up being simpler than the workaround I was trying: skip distance entirely for this step and just feed Louvain the correlation matrix directly, since correlation already is a similarity measure. Once I did that, running it on the 12-stock basket gave real, clean sector structure:

- Tech (AAPL, GOOGL, META, MSFT) - one community
- Banks (JPM, BAC, GS) - one community
- Energy + consumer staples (XOM, CVX, PEP, KO, WMT) - merged into one community rather than splitting



UPDATE-4 SEPTEMBER 26th, 2026: Fixes and Corrected Results

I went back through the code and found bugs that inflated or distored my earlier results. Fixing them changed several findings, so the ealirer ones are marked as superseded above


**What I fixed and why:**
- **Buy-and-hold comparison:** strategy *profit* was being compared to buy-and-hold *total value* (starting cash included), which skewed every ratio. Both are now profit.
- **Ratio direction:** the ratio flipped depending on which side won, so "2.7x" was ambiguous. It's now always strategy ÷ buy-and-hold: above 1 means the strategy won.
- **Max drawdown:** it was only checked on sell days, so crashes during a trade were invisible. It's now measured on daily portfolio value.
- **Lookahead bias:** trades executed at the same close that generated the signal. They now execute the next day.
- **Aligned windows:** all 12 stocks run 2015–2025, with 2014 as a warm-up so both moving averages are valid from day one, and buy-and-hold starts on the same date as the strategy.

**Setup:** $10,000 per stock · 2015-01-02 to 2025-12-31 · 50/200-day crossover · prices split- and dividend-adjusted (yfinance) · no fees or slippage

**Results:**

| Ticker | Strategy / B&H Profit | B&H Max DD | Strategy Max DD | Trades |
|---|---|---|---|---|
| AAPL | 0.29 | 38.5% | 45.6% | 6 |
| GOOGL | 0.57 | 44.3% | 30.9% | 8 |
| META | 0.47 | 76.7% | 38.7% | 6 |
| MSFT | 0.71 | 37.2% | 28.0% | 6 |
| XOM | 0.53 | 61.3% | 42.6% | 10 |
| CVX | 0.45 | 55.8% | 43.6% | 9 |
| JPM | 0.60 | 43.6% | 43.6% | 5 |
| BAC | 0.16 | 49.0% | 50.1% | 11 |
| GS | 0.50 | 48.8% | 47.6% | 9 |
| PEP | 0.42 | 30.3% | 28.8% | 8 |
| KO | 0.08 | 37.0% | 37.0% | 10 |
| WMT | 0.49 | 36.4% | 41.7% | 8 |

**Findings:**

- **Buy-and-hold won on profit for all 12 stocks.** The strategy kept a median of about half of buy-and-hold's profit.

- **The crossover is late, because moving averages are built from past prices.** On AAPL, the death cross sold on Dec 24, 2018 at $34.81. The stock bottomed just 3.2% lower on Jan 3, 2019, and the strategy didn't re-enter until May at $48.30, 39% above its exit. It avoided a 3% drop and missed a 39% recovery.

- **It only protects you from crashes that last longer than its lag.** META's 2022 decline lasted most of the year. The strategy sold at $331 and sat out the fall to $88, while buy-and-hold rode it down 77%. AAPL's 2018 selloff lasted about 3 months, which was over before the signal fired.

- **Choppy stocks get whipsawed.** KO had the worst results (0.08x) across 10 trades. Each loss was small, but the strategy bought back in higher tan it sold on all 8 entries. In April 2019 it sold at $37.82 and bought back 15 days later at $38.30. Three of its sells landed on the lowest close of the period it was out. The strategy never took a big loss. It just kept paying more to get back in. 

- **Drawdown protection was inconsistent.** Meaningfully smaller on 5 stocks (META, GOOGL, MSFT, XOM, CVX), about the same on 5, and worse on 2 (AAPL, WMT).

**Limitations:**
- No trading fees or slippage. These would hurt high-trade stocks like KO and BAC even more.
- One parameter set (50/200) and one time window.
- Survivorship bias: all 12 are large companies that exist today, so failed companies aren't tested.


