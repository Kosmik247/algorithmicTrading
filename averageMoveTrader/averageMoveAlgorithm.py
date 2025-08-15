import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')

def calc_strategy_performance(data, short_window, long_window):
    """
    Calculates the trading signals and positions for a simple moving average
    crossover strategy.

    Args:
        data (panda.Dataframe): DataFrame containing stock price data with a Close column.
        short_window (int): The number of days for the short moving average.
        long_window (int): The number of days for the long moving average.

    Returns:
        panda.DataFrame: A copy of the original DataFrame with Fast_MA, Slow_MA,
                      Signal and Position columns added.
    """
    
    df = data.copy() # Copydata to avoid modifying the original DataFrame
    
    # Calculate the moving averages using the user defined windows
    df['Fast_MA'] = df['Close'].rolling(window=short_window).mean()
    df['Slow_MA'] = df['Close'].rolling(window=long_window).mean()

   
    df['Signal'] = 0.0
    
    # Generate a signal of 1.0 when fast MA crosses above the slow MA
    df.loc[df.index[long_window:], 'Signal'] = np.where(df['Fast_MA'][long_window:] > df['Slow_MA'][long_window:], 1.0, 0.0)
    
    # Creating a crossover signal that only maps changes for buy/sell signals on plot
    df['Crossover'] = df['Signal'].diff()
    
    # Position column indicating if position is held based on signal from the PREVIOUS day.
    df['Position'] = df['Signal'].shift(1)
    
    return df

def calculate_metrics(data):
    """
    Calculates key performance metrics of the trading strategy.
    
    Args:
        data (panda.DataFrame): DataFrame with Close and Position columns.
    
    Returns:
        dict: A dictionary of performance metrics.
    """
    # Calculate returns
    data['Daily_Return'] = data['Close'].pct_change()
    data['Strategy_Return'] = data['Daily_Return'] * data['Position'].shift(1) # Shift position to avoid lookahead bias
    
    # Calculate cumulative returns
    data['Cumulative_Benchmark'] = (1 + data['Daily_Return']).cumprod()
    data['Cumulative_Strategy'] = (1 + data['Strategy_Return']).cumprod()
    
    # Total returns
    total_strategy_return = data['Cumulative_Strategy'].iloc[-1] - 1
    total_benchmark_return = data['Cumulative_Benchmark'].iloc[-1] - 1 # Create a benchmark return for comparison
    
    # Sharpe Ratio
    mean_daily_return = data['Strategy_Return'].mean()
    std_daily_return = data['Strategy_Return'].std()

    # Handle the case of zero standard deviation to avoid division by zero
    if std_daily_return == 0:
        annualised_sharpe = np.nan
    else:
        annualised_sharpe = (mean_daily_return * 252) / (std_daily_return * np.sqrt(252))
    
    # Maximum Drawdown which is the maximum observed loss from a peak to a trough
    data['Cumulative_Max'] = data['Cumulative_Strategy'].cummax()
    data['Drawdown'] = (data['Cumulative_Max'] - data['Cumulative_Strategy']) / data['Cumulative_Max']
    max_drawdown = data['Drawdown'].max()
    
    # Beta formula, this is a measure of volatility relative to the market, higher beta means more volatility
    beta = data['Strategy_Return'].cov(data['Daily_Return']) / data['Daily_Return'].var()

    # Alpha formula, this is the excess return of the strategy over the benchmark, higher alpha means better performance
    mean_strategy_return = data['Strategy_Return'].mean()
    mean_benchmark_return = data['Daily_Return'].mean()
    alpha = mean_strategy_return - (beta * mean_benchmark_return)
    annualised_alpha = alpha * 252

    # Annualised volatility, which is the standard deviation of returns scaled to annual terms
    annualised_volatility = data['Strategy_Return'].std() * np.sqrt(252)

    # Calmar ratio, which is a risk-adjusted return measure, a measure of return per unit of risk
    annualised_return = data['Strategy_Return'].mean() * 252
    if max_drawdown == 0: 
        calmar_ratio = np.nan
    else:
        calmar_ratio = annualised_return / max_drawdown

    return {"Total Strategy Return": total_strategy_return,
            "Total Buy-and-Hold Return": total_benchmark_return,
            "Sharpe Ratio": annualised_sharpe,
            "Maximum Drawdown": max_drawdown,
            "Beta": beta,
            "Annualised Alpha": annualised_alpha,
            "Annualised Volatility": annualised_volatility,
            "Calmar Ratio": calmar_ratio}

def optimise_strategy(data):
    """
    Performs a parameter sweep to find the optimal short and long window
    based on the highest Sharpe Ratio.
    
    Args:
        data (panda.DataFrame): The stock price data.
        
    Returns:
        tuple: A tuple containing the best short and long window values.
    """
    best_sharpe = -np.inf
    best_params = (0, 0)
    
    print("\n--- Running Parameter Optimization ---")
    
    # Define a range of values for the short and long windows
    short_window_range = range(10, 61, 5)  
    long_window_range = range(100, 251, 10)  

    for short in short_window_range:
        for long in long_window_range:
            # Skip invalid combinations where short window is not less than long
            if short >= long:
                continue
            
            # Calculate strategy performance for this parameter set
            temp_data = calc_strategy_performance(data, short, long)
            
            # Calculate metrics
            metrics = calculate_metrics(temp_data)
            
            # Check if this combination has a better Sharpe Ratio
            if metrics['Sharpe Ratio'] > best_sharpe:
                best_sharpe = metrics['Sharpe Ratio']
                best_params = (short, long)
                print(f"New best found: Short={short}, Long={long}, Sharpe={best_sharpe:.2f}")

    print("--- Optimization Complete ---")
    print(f"Best parameters are Short={best_params[0]}, Long={best_params[1]}")
    return best_params

def print_metrics(metrics):
    """
    Prints the performance metrics in a formatted way.
    
    Args:
        metrics (dict): A dictionary of performance metrics.
    """
    print("--- Performance Metrics ---")
    print(f"Total Strategy Return: {metrics['Total Strategy Return']:.2%}")
    print(f"Total Buy-and-Hold Return: {metrics['Total Buy-and-Hold Return']:.2%}")
    print(f"Sharpe Ratio: {metrics['Sharpe Ratio']:.2f}")
    print(f"Maximum Drawdown: {metrics['Maximum Drawdown']:.2%}")
    print(f"Beta: {metrics['Beta']:.2f}")
    print(f"Annualised Alpha: {metrics['Annualised Alpha']:.2f}")
    print(f"Annualised Volatility: {metrics['Annualised Volatility']:.2f}")
    print(f"Calmar Ratio: {metrics['Calmar Ratio']:.2f}")
    
def plot_data(data, short_window, long_window, metrics, ticker_symbol):
    """
    Plots the stock price, moving averages, and trading signals, as well as
    the cumulative returns of the strategy vs. a benchmark and the drawdown.
    
    Args:
        data (panda.DataFrame): The DataFrame with all calculated columns.
        short_window (int): The number of days for the short moving average.
        long_window (int): The number of days for the long moving average.
        metrics (dict): A dictionary of performance metrics to display in titles.
        ticker_symbol (str): The stock ticker symbol.
    """
    # 3 Subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 18), sharex=True)
    
    # Plot 1: Price and Signals
    ax1.plot(data['Close'], label='Close Price')
    ax1.plot(data['Fast_MA'], label=f'{short_window}-Day MA')
    ax1.plot(data['Slow_MA'], label=f'{long_window}-Day MA')

    # Plot buy signals when there is a positive crossover
    buy_signals = data.loc[data['Crossover'] == 1.0]
    ax1.plot(buy_signals.index,
             buy_signals['Close'],
             '^', markersize=10, color='g', label='Buy Signal')

    # Plot sell signals when there is a negative crossover
    sell_signals = data.loc[data['Crossover'] == -1.0]
    ax1.plot(sell_signals.index,
             sell_signals['Close'],
             'v', markersize=10, color='r', label='Sell Signal')
             
    ax1.set_title(f"Moving Average Crossover Trading Signals ({short_window} vs {long_window}) for {ticker_symbol}")
    ax1.set_ylabel('Stock Price ($)')
    ax1.legend()

    # Plot 2: Cumulative Returns
    ax2.plot(data['Cumulative_Strategy'], label='Strategy Returns', color='blue')
    ax2.plot(data['Cumulative_Benchmark'], label='Buy-and-Hold Returns', color='gray')
    ax2.set_title(f"Cumulative Returns | Strategy Return: {metrics['Total Strategy Return']:.2%}, Buy-and-Hold: {metrics['Total Buy-and-Hold Return']:.2%}")
    ax2.set_ylabel('Cumulative Return')
    ax2.legend()
    
    # Plot 3: Drawdown
    ax3.fill_between(data['Drawdown'].index, data['Drawdown'], color='red', alpha=0.3)
    ax3.set_title(f"Maximum Drawdown | Max Drawdown: {metrics['Maximum Drawdown']:.2%}")
    ax3.set_ylabel('Drawdown')
    ax3.set_xlabel('Date')
    
    plt.tight_layout()
    plt.show()
    

if __name__ == "__main__":
    ticker_symbol = input("Enter a ticker that you would like to analyze: ").upper()
    data = yf.download(ticker_symbol, start='2020-01-01', end='2024-01-01', auto_adjust=True)
    
    
    print("\nSelect an option:")
    print("1: Manually enter moving average windows")
    print("2: Automatically optimise for the best windows")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        short_window = int(input("Enter the short moving average window (default 50): ") or "50")
        long_window = int(input("Enter the long moving average window (default 200): ") or "200")
        
    elif choice == '2':
        short_window, long_window = optimise_strategy(data)
        
    else:
        print("Invalid choice. Exiting.")
        exit()

    data_with_signals = calc_strategy_performance(data, short_window, long_window)
    
    metrics = calculate_metrics(data_with_signals)
    print_metrics(metrics)
    
    plot_data(data_with_signals, short_window, long_window, metrics, ticker_symbol)
