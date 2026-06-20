# Python BackTester 

import yfinance as yf
import pandas as pd
from rich import print
import matplotlib.pyplot as plt


#Pull stock data from 2020-2023
ticker = 'TSLA'
start_date = '2000-01-01'
end_date = '2020-12-31'
stock_data = yf.download(ticker, start= start_date, end=end_date)
stock_data.columns = stock_data.columns.droplevel(1)
cash = int(input("Starting Cash: $")) #starting cash
#Calculate 50 day and 200 day Moving-Avergage to find trends 

#50 Day 

stock_data['MA50'] = stock_data['Close'].rolling(window = 50).mean()

#200 day
stock_data['MA200'] = stock_data['Close'].rolling(window = 200).mean()



#Generating Signals--
stock_data['Signal'] = 0 

stock_data.loc[(stock_data['MA50'] > stock_data['MA200']) & (stock_data['MA50'].shift(1) < stock_data['MA200'].shift(1)) ,'Signal'] = 1 #Buy
stock_data.loc[(stock_data['MA50'] < stock_data['MA200']) & (stock_data['MA50'].shift(1) > stock_data['MA200'].shift(1)) ,'Signal'] = -1 #Sell



def simulate_trades(stock_data):
    shares = 0
    buy_price = 0
    buy_date = None
    trade = []
    profit = 0
    for i, row, in stock_data.iterrows():

        #buy signal
        if row['Signal'] == 1 and not shares:
            buy_date = i
            buy_price = row['Close']
            shares = cash / buy_price
            
        if row['Signal'] == -1 and shares:
            sell_date = i
            sell_price = row['Close']
            profit = (shares * sell_price) - (shares * buy_price)
            balance  = cash + profit
            trade.append({
                 'buy_date': buy_date,
                'buy_price': buy_price,
                'sell_date': sell_date,
                'profit': profit, 
                'balance': round(balance,2)
                })
            shares = 0
    return trade

trades = simulate_trades(stock_data)
print(trades)

        
#Performance Metrics 
def calcuate_metric(trades):
    total_profit = 0 
    win_rate = 0.0
    avg_win = 0
    avg_loss = 0 
    drawdown = 0.0
    max_drawdown = 0.0
    performance_metric = []

    #total profit
    total_profit = sum(trade['profit'] for trade  in trades )
    #win rate - (num of profits > 0 / num of trades) * 100
    win_rate =  (sum(trade['profit'] > 0 for trade  in trades ) / len(trades)) 

    winning_profits = [trade['profit'] for trade in trades if trade['profit'] > 0]
    losing_profits = [trade['profit'] for trade in trades if trade['profit'] < 0]
    #average_win - average of all the wins 
    avg_win = sum(winning_profits) / len(winning_profits) if winning_profits else 0 #case if wins are 0
    #average_loss - average of all losses
    avg_loss = sum(losing_profits) / len(losing_profits) if losing_profits else 0

    #drawdoqn - term for any drop 
    peak = trades[0]['balance']

    for  trade in trades:
        balance = trade['balance']
        if  balance > peak:
            peak = balance 
        drawdown = ((peak - balance) / peak ) * 100

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

metrics = calcuate_metric(trades)
print(metrics)
     
#Benchmark Comparison - Comparing my trading strategy 
#final balance to my buy/hold final value.  
def calculate_buy_and_hold(stock_data, cash):
    first_price = stock_data['Close'].iloc[0]
    last_price =  stock_data['Close'].iloc[-1]
    shares = cash / first_price
    final_value = shares * last_price
    return final_value

strategy_profit = metrics[0]['Total Profit']
buy_hold_value = calculate_buy_and_hold(stock_data, cash)

def benchmark_comparison(strategy_profit, buy_hold_value):
    difference = 0
    ratio = 0.0
    final_comparison = []
    if strategy_profit > buy_hold_value:
        difference = strategy_profit - buy_hold_value
        ratio = strategy_profit /  buy_hold_value
    elif buy_hold_value > strategy_profit:
        difference = buy_hold_value - strategy_profit
        ratio = buy_hold_value /  strategy_profit
    else:
        difference = 0
        ratio = 1 
    final_comparison.append({
        'Strategy Profit': strategy_profit,
        'Buy & Hold Profit': buy_hold_value,
        'Difference': difference,
        'Ratio': ratio
            })
    return final_comparison

final_comparison = benchmark_comparison(strategy_profit,buy_hold_value)
print(final_comparison)    

#Visualizing this Data 

plt.style.use('seaborn-v0_8-darkgrid')

plt.figure(figsize=(14, 7))  

plt.plot(stock_data['Close'], label = 'Close Price')
plt.plot(stock_data['MA50'], label = '50-Day MA')
plt.plot(stock_data['MA200'], label = "200-day MA")

buys = stock_data[stock_data['Signal'] == 1]
plt.scatter(buys.index, buys['Close'], color='green', marker='^', s=100, label='Buy')

sells = stock_data[stock_data['Signal'] == -1]
plt.scatter(sells.index, sells['Close'], color='red', marker='v', s=100, label='Sell')

plt.title(f"{ticker} Golden Cross Strategy (2020-2021)")
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()