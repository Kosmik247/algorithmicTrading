# Algorithmic Trading Backtester (Average Move)
This project is a Python-based tool for evaluating a simple moving **average crossover trading strategy** using historical stock data. It's designed to provide a comprehensive look at a strategy's performance, including metrics such as volatility and sharpe ratio.

This project uses the yahoo finance library in python, to allow the user to backtest data. This lets us simulate trades to see how this specific strategy would have performed in the past, identifying patterns and flaws before being employed on real money.

## Metrics

1. Sharpe Ratio: The ratio calculates the return generated for each unit of risk (volatility) taken. A higher Sharpe Ratio indicates a better risk-reward profile. For example, a strategy with a 10% return and low volatility is generally considered better than a strategy with a 15% return and very high volatility.

2. Alpha & Beta: These metrics measure a strategy's performance relative to the overall market (or the chosen benchmarkof a buy and hold strategy.).

    - Beta measures volatility. If your strategy has a Beta of 1.2, it's considered 20% more volatile than the market. A Beta of 0.8 means it's 20% less volatile.
    - Alpha measures excess return, telling you how the strategy outperformed the market taking into account volatility (Beta). A positive alpha suggests the strategy generates returns above what the market would expect for the associated risk level.

3. Calmar Ratio: This metric focuses on downside risk. It compares the average annual return to the maximum drawdown (the largest percentage drop from a peak to a trough in the portfolio's value). A high Calmar Ratio indicates a strategy that has delivered strong returns while avoiding large, sustained losses.

## How it works.
This backtester is built around a simple moving average crossover strategy. The core logic is as follows:

Moving Averages: The program calculates two moving averages: a "fast" moving average (e.g. 50 days) and a "slow" moving average (e.g. 200 days). These values are the default within the program if no input is provided.

### Signal Generation:

A buy signal is generated when the fast moving average crosses above the slow moving average. This suggests a potential uptrend, or that the stock is gaining momentum.

A sell signal is generated when the fast moving average crosses below the slow moving average. This suggests a potential downtrend, or that the stock is losing momentum.

- Simulated Trading: The algorithm simulates buying and selling a single share of the stock based on these signals and tracks the portfolio's performance over time.

- Evaluation: Once the backtest is complete, the program calculates and displays a suite of performance metrics and generates interactive plots to visualize the results. This provides a comprehensive, data-driven evaluation of the strategy's effectiveness.

### Key Features
- Moving Average Crossover Backtesting: Test a customizable moving average crossover strategy on any stock available through yfinance. **Limited to ONE stock.**

- Parameter Optimization: Automatically test a range of short and long moving average windows to find the combination that yields the highest Sharpe Ratio.

- Performance Metrics: The program calculates key metrics including total return, Sharpe Ratio, Alpha, Beta, Calmar Ratio, and annualized volatility.

- Visualization for the User: Interactive plots show the stock price with trading signals, the cumulative returns of the strategy vs. a buy-and-hold benchmark, and the strategy's maximum drawdown.

## Getting Started
### Prerequisites
To run this script, you'll need Python and a few libraries. You can install all the required dependencies at once using the provided requirements.txt file.

- pip install -r requirements.txt

**Usage**
Run the script from your terminal:

python averageMoveAlgorithm.py

The program will prompt you to enter a stock ticker. It will then give you a choice:

1. Manually enter moving average windows: This lets you test a specific combination of windows (e.g., a 20-day and 50-day MA).

2. Automatically optimize: The script will run a parameter sweep to find the best combination of moving averages for the highest Sharpe Ratio.

After your choice, the program will print the performance metrics and display a plot with all the visualizations.

# Future Features that could be added/ Improvements

- Implement other trading strategies, such as the RSI or MACD.

- Allow for a custom benchmark (e.g. S&P 500) for more accurate Alpha and Beta calculations.

- Add the ability to save backtest results to a CSV file.

- Create a simple graphical user interface (GUI) for a more user-friendly experience. (Could be done through an interactive web application, or through more advanced interfaces such as PyQt.)