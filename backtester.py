# Trading Backtester 

import yfinance as yf
import pandas as pd
from rich import print
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np 
import networkx as nx
import community as community_louvain

# Preparing data - Create Moving Average and Buy/Sell Signals
# download_start is the start date for downloading data, 
# eval_start is the start date for evaluating the strategy, 
# end_date is the end date for evaluating the strategy.
def prepare_data(ticker, download_start, eval_start, end_date):
    stock_data = yf.download(ticker, start= download_start, end=end_date)
    stock_data.columns = stock_data.columns.droplevel(1)
 
    # Calculate 50 day and 200 day Moving Average to find trends 
    #50 Day 
    stock_data['MA50'] = stock_data['Close'].rolling(window = 50).mean()

    #200 day
    stock_data['MA200'] = stock_data['Close'].rolling(window = 200).mean()

    # Generating Buy And Sell Signals based on MA trends
    # These trends are based on the Golden Cross and Death Cross strategy. 
    # A buy signal is generated when the 50-day moving average crosses above the 200-day moving average (Golden Cross). 
    # A sell signal is generated when the 50-day moving average crosses below the 200-day moving average (Death Cross).
    stock_data['Signal'] = 0 
    stock_data.loc[(stock_data['MA50'] > stock_data['MA200']) & (stock_data['MA50'].shift(1) < stock_data['MA200'].shift(1)) ,'Signal'] = 1 #Buy
    stock_data.loc[(stock_data['MA50'] < stock_data['MA200']) & (stock_data['MA50'].shift(1) > stock_data['MA200'].shift(1)) ,'Signal'] = -1 #Sell

    stock_data['Signal'] = stock_data['Signal'].shift(1).fillna(0)
    stock_data = stock_data.loc[eval_start:]
    return stock_data 

# Simulating Trades - These trades are based on the signals generated  by the moving averages. 
# The simulation will track the number of shares bought and sold, as well as the profit or loss from each trade.
def simulate_trades(stock_data,cash):
    shares = 0
    buy_price = 0
    buy_date = None
    trade = []
    profit = 0
    equity = []
    for i, row, in stock_data.iterrows():

        #Buy signal
        if row['Signal'] == 1 and not shares:
            buy_date = i
            buy_price = row['Close']
            shares = cash / buy_price
        #Sell signal
        if row['Signal'] == -1 and shares:
            sell_date = i
            sell_price = row['Close']
            proceeds = shares * sell_price
            cost_basis = shares * buy_price
            profit = proceeds - cost_basis
            cash = proceeds 
            trade.append({
                 'buy_date': buy_date,
                'buy_price': float(buy_price),
                'sell_date': sell_date,
                'profit': round(float(profit), 2), 
                'balance': round(float(cash),2)
                })
            shares = 0
        equity.append(shares * row['Close'] if shares else cash)

    # If a position is still open at the end of the backtest window,
    # close it out at the last available price so it's not silently dropped.
    if shares > 0:
        last_date = stock_data.index[-1]
        last_price = stock_data['Close'].iloc[-1]
        proceeds = shares * last_price
        cost_basis = shares * buy_price
        profit = proceeds - cost_basis
        cash = proceeds

        trade.append({
            'buy_date': buy_date,
            'buy_price': float(buy_price),
            'sell_date': last_date,
            'profit': float(profit),
            'balance': round(float(cash), 2)
        })

    return trade , equity

# Performance Metrics - Generating performance metrics based on the trades simulated. 
# These metrics will help evaluate the effectiveness of the trading strategy.
def calculate_metric(trades, equity):
    total_profit = 0 
    win_rate = 0.0
    avg_win = 0
    avg_loss = 0 
    drawdown = 0.0
    max_drawdown = 0.0
    performance_metric = []
    peak = equity[0] if equity else 0

    # Total profit - Sum of all profits from trades
    total_profit = sum(trade['profit'] for trade  in trades )

    # Win Rate - (num of profits > 0 / num of trades) * 100
    win_rate =  (sum(trade['profit'] > 0 for trade  in trades ) / len(trades))   *100 if trades else 0 #case if trades are 0

    winning_profits = [trade['profit'] for trade in trades if trade['profit'] > 0]
    losing_profits = [trade['profit'] for trade in trades if trade['profit'] < 0]

    # Average Win - average of all the wins 
    avg_win = sum(winning_profits) / len(winning_profits) if winning_profits else 0 #case if wins are 0
    # Average Loss - average of all losses
    avg_loss = sum(losing_profits) / len(losing_profits) if losing_profits else 0

    # Drawdown - term for any drop 
    for value in equity:
        if value > peak:
            peak = value
        drawdown = ((peak - value) / peak) * 100 
        if drawdown > max_drawdown:
            max_drawdown = drawdown


    performance_metric.append({
        'Trades': len(trades),
        'Total Profit': total_profit, 
        'Win Rate': win_rate,
        'Average Win': avg_win,
        'Average Loss': avg_loss,
        'Max Drawdown': max_drawdown,
    })
    return  performance_metric

# Benchmark Comparison - Comparing my trading strategy 
# final balance to my total profit from a buy and hold strategy.
def calculate_buy_and_hold(stock_data, cash):
    first_price = stock_data['Close'].iloc[0]
    last_price =  stock_data['Close'].iloc[-1]
    shares = cash / first_price
    final_value = shares * last_price
    return float(final_value - cash)

def benchmark_comparison(strategy_profit, buy_hold_profit):
    difference = strategy_profit - buy_hold_profit
    ratio = 0.0
    final_comparison = []
    if buy_hold_profit > 0:
        ratio = round(strategy_profit / buy_hold_profit, 2)
    else:
        ratio = 'n/a'
    final_comparison.append({
        'Strategy Profit': round(strategy_profit, 2),
        'Buy & Hold Profit': round(buy_hold_profit, 2),
        'Difference': round(difference, 2),
        'Strategy to Buy & Hold Ratio': ratio
    })
    return final_comparison

#Correlation Matrix - Measures how each pair of stocks move together based on daily return values
def get_correlation_matrix(tickers, start_date, end_date):
    data = yf.download(tickers, start= start_date, end=end_date)
    closing_price = data["Close"]
    returns = closing_price.pct_change().dropna()
    correlation_matrix = returns.corr()
    return correlation_matrix

def correlation_to_distance(correlation_matrix):
    distance = np.sqrt(2 * (1-correlation_matrix))
    return distance

def create_n_graphs(tickers, dist):
    G = nx.Graph()
    for i, tickers_i in enumerate(tickers):
        for j, tickers_j in enumerate(tickers):
         if  i < j:
             G.add_edge(tickers_i, tickers_j, weight = dist.loc[tickers_i, tickers_j])
    return G

def extract_mst(G):
    mst = nx.minimum_spanning_tree(G, weight = 'weight')
    return mst

def detect_communities(G):
    partition = community_louvain.best_partition(G, weight = 'weight')
    return partition

def create_similarity_graph(tickers, corr):
    G = nx.Graph()
    for i, ticker_i in enumerate(tickers):
        for j, ticker_j in enumerate(tickers):
            if i < j:
                G.add_edge(ticker_i, ticker_j, weight=corr.loc[ticker_i, ticker_j])
    return G

def visualize_communities(G, partition, title = "Stock Correlation Communities"):
    pos = nx.spring_layout(G, seed=42)
    
    num_communities = len(set(partition.values()))
    colors = mpl.colormaps['tab10'].resampled(num_communities)
    node_colors = [colors(partition[node]) for node in G.nodes()]
    
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, 
            node_size=800, font_size=9, font_weight='bold')
    plt.title(title) 
    plt.show()
# Setup for multiple tickers. We will loop through each ticker and perform the backtesting process. 
# All across one time frame.
tickers = [
    'AAPL', 'GOOGL', 'META', 'MSFT',   # tech
    'XOM', 'CVX',                      # energy
    'JPM', 'BAC', 'GS',                # banks
    'PEP', 'KO', 'WMT'                 # consumer staples
] #stock tickers
download_start = '2014-01-01'
eval_start = '2015-01-01'
end_date = '2026-01-01'
starting_cash = int(input("Starting Cash: $")) #starting cash

# Loop through each ticker and perform backtesting
for ticker in tickers:
    stock_data = prepare_data(ticker, download_start, eval_start, end_date)
    print(f"\nBacktesting {ticker} from {stock_data.index[0].date()} to {stock_data.index[-1].date()} (MA warm-up from {download_start[:4]})...")
    trades, equity = simulate_trades(stock_data,starting_cash)
    performance_metrics = calculate_metric(trades, equity)
    buy_hold_profit = calculate_buy_and_hold(stock_data, starting_cash)
    strategy_profit = performance_metrics[0]['Total Profit']
    comparison = benchmark_comparison(strategy_profit, buy_hold_profit)
    print(f"Performance Metrics for {ticker}")
    print(performance_metrics)
    print(f"Benchmark Comparison for {ticker}")
    print(comparison)
    print(f"view trades for {ticker}? (y/n)")
    view_trades = input().lower()
    if view_trades == 'y':
        print(f"Trades for {ticker}:")
        for trade in trades:
            print(trade)
    else: print("Trades skipped.")
    print("next? (y/n)")
    next_ticker = input().lower()
    if next_ticker == 'y':
        continue
    else: break

#Testing Correlation Matrix 
   
while True:
    print("Would you like to view the correlation matrix for these tickers? (y/n)")
    see_matrix = input().lower()
    if see_matrix == 'y':
        gather_matrix = get_correlation_matrix(tickers,eval_start, end_date)      
        print(gather_matrix.round(2))
        dist = correlation_to_distance(gather_matrix)
        Graphs = create_n_graphs(tickers, dist)

        while  True:
            print("Would you like to generate a graph? (y/n)")
            see_graph = input().lower()
            if see_graph == 'y': 
                pos = nx.spring_layout(Graphs)
                nx.draw(Graphs, pos, with_labels=True)
                plt.show()
                #Generating Minium Spanning Tree to show 
                # strongest correlated relations

                mst = extract_mst(Graphs)
                plt.figure()
                pos_mst = nx.spring_layout(mst)
                nx.draw(mst, pos_mst, with_labels = True)
                plt.show()
                break
            elif see_graph == 'n':
                print("skipping...")
                break
                
                #Generating Community Detection wth Color coded Graphing
        while True:
             print("Visualize community detection? (y/n)") 
             see_communities = input().lower()
             if see_communities == 'y':
                G_similarity = create_similarity_graph(tickers, gather_matrix)
                partition = detect_communities(G_similarity)
                visualize_communities(Graphs, partition)
                break
             elif see_communities == 'n':
                print("skipping...")
                break
        break
    elif see_matrix == 'n':
        print('skipping.')
        break

#Visualizing Golden Cross Strategy 
while True:

    print("Would you like to visualize a Golden Cross Strategy? (y/n)")
    visualize = input().lower()
    if visualize == 'y':
        print(f"Which ticker would you like to visualize? ({tickers})")
        ticker = input().upper()
        if ticker not in tickers:
            print(f"{ticker} is not in the list of tickers. Please choose from {tickers}.")
        else:
            stock_data = prepare_data(ticker, download_start, eval_start, end_date)
            print(f"Visualizing {ticker} Golden Cross Strategy from {stock_data.index[0].year}-{stock_data.index[-1].year} (MA warm-up from {download_start})...")
            plt.style.use('seaborn-v0_8-darkgrid')

            plt.figure(figsize=(14, 7))  

            plt.plot(stock_data['Close'], label = 'Close Price')
            plt.plot(stock_data['MA50'], label = '50-Day MA')
            plt.plot(stock_data['MA200'], label = "200-day MA")

            buys = stock_data[stock_data['Signal'] == 1]
            plt.scatter(buys.index, buys['Close'], color='green', marker='^', s=100, label='Buy')

            sells = stock_data[stock_data['Signal'] == -1]
            plt.scatter(sells.index, sells['Close'], color='red', marker='v', s=100, label='Sell')
            plt.title(f"{ticker} Golden Cross Strategy ({stock_data.index[0].year}-{stock_data.index[-1].year})")
            plt.xlabel('Date')
            plt.ylabel('Price ($)')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.show()
    else:
        print("Visualization skipped.") 
        break 