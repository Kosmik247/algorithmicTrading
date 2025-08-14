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
        data (pd.DataFrame): DataFrame containing stock price data with a 'Close' column.
        short_window (int): The number of days for the short moving average.
        long_window (int): The number of days for the long moving average.

    Returns:
        pd.DataFrame: A copy of the original DataFrame with 'Fast_MA', 'Slow_MA',
                      'Signal', and 'Position' columns added.
    """
    # Create a copy to avoid the SettingWithCopyWarning
    df = data.copy()
    
    # Calculate the moving averages using the user-defined windows
    df['Fast_MA'] = df['Close'].rolling(window=short_window).mean()
    df['Slow_MA'] = df['Close'].rolling(window=long_window).mean()

    df['Signal'] = 0.0
    
    # Generate a raw signal of 1.0 when fast MA crosses above the slow MA
    df.loc[df.index[long_window:], 'Signal'] = np.where(df['Fast_MA'][long_window:] > df['Slow_MA'][long_window:], 1.0, 0.0)
    
    # Creating a crossover signal that only maps changes for buy/sell signals on plot
    df['Crossover'] = df['Signal'].diff()
    
    # Position column indicating if position is held based on signal from the PREVIOUS day.
    df['Position'] = df['Signal'].shift(1)
    
    return df

def analyze_strategy_performance(data):
    """
    Calculates and prints the key performance metrics of the trading strategy.
    
    Args:
        data (pd.DataFrame): DataFrame with 'Close' and 'Position' columns.
    
    Returns:
        pd.DataFrame: The original DataFrame with performance metric columns added.
    """
    # Calculate returns
    data['Daily_Return'] = data['Close'].pct_change()
    data['Strategy_Return'] = data['Daily_Return'] * data['Position'].shift(1)
    
    # Calculate cumulative returns
    data['Cumulative_Benchmark'] = (1 + data['Daily_Return']).cumprod()
    data['Cumulative_Strategy'] = (1 + data['Strategy_Return']).cumprod()
    
    # Calculate key metrics
    total_strategy_return = data['Cumulative_Strategy'].iloc[-1] - 1
    total_benchmark_return = data['Cumulative_Benchmark'].iloc[-1] - 1
    
    # Sharpe Ratio
    mean_daily_return = data['Strategy_Return'].mean()
    std_daily_return = data['Strategy_Return'].std()

    # Handle the case of zero standard deviation to avoid division by zero
    if std_daily_return == 0:
        annualized_sharpe = np.nan
    else:
        annualized_sharpe = (mean_daily_return * 252) / (std_daily_return * np.sqrt(252))
    
    # Maximum Drawdown which is the maximum observed loss from a peak to a trough
    data['Cumulative_Max'] = data['Cumulative_Strategy'].cummax()
    data['Drawdown'] = (data['Cumulative_Max'] - data['Cumulative_Strategy']) / data['Cumulative_Max']
    max_drawdown = data['Drawdown'].max()
    
    
    print("--- Performance Metrics ---")
    print(f"Total Strategy Return: {total_strategy_return:.2%}")
    print(f"Total Buy-and-Hold Return: {total_benchmark_return:.2%}")
    print(f"Sharpe Ratio: {annualized_sharpe:.2f}")
    print(f"Maximum Drawdown: {max_drawdown:.2%}")
    
    return data

def plot_data(data, short_window, long_window):
    """
    Plots the stock price, moving averages, and trading signals, as well as
    the cumulative returns of the strategy vs. a benchmark.
    
    Args:
        data (pd.DataFrame): The DataFrame with all calculated columns.
        short_window (int): The number of days for the short moving average.
        long_window (int): The number of days for the long moving average.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
    
    ax1.plot(data['Close'], label='Close Price')
    ax1.plot(data['Fast_MA'], label=f'{short_window}-Day MA')
    ax1.plot(data['Slow_MA'], label=f'{long_window}-Day MA')

    # Plot buy signals when there is a positive crossover, not relying on signals column
    buy_signals = data.loc[data['Crossover'] == 1.0]
    ax1.plot(buy_signals.index,
             buy_signals['Close'],
             '^', markersize=10, color='g', label='Buy Signal')

    # Selling when negative crossover occurs
    sell_signals = data.loc[data['Crossover'] == -1.0]
    ax1.plot(sell_signals.index,
             sell_signals['Close'],
             'v', markersize=10, color='r', label='Sell Signal')
             
    ax1.set_title(f'Moving Average Crossover Trading Signals ({short_window} vs {long_window})')
    ax1.set_ylabel('Stock Price')
    ax1.legend()

    # Plot 2: Cumulative Returns
    ax2.plot(data['Cumulative_Strategy'], label='Strategy Returns', color='blue')
    ax2.plot(data['Cumulative_Benchmark'], label='Buy-and-Hold Returns', color='gray')
    ax2.set_title('Cumulative Returns')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Cumulative Return')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
    

if __name__ == "__main__":
    ticker_symbol = input("Enter a ticker that you would like to analyze: ").upper()
    data = yf.download(ticker_symbol, start='2020-01-01', end='2024-01-01', auto_adjust=True)
    
    
    short_window_input = input("Enter the short moving average window (default 50): ") or "50"
    long_window_input = input("Enter the long moving average window (default 200): ") or "200"
    
    short_window = int(short_window_input)
    long_window = int(long_window_input)

    
    data_with_signals = calc_strategy_performance(data, short_window, long_window)
    
    
    data_with_metrics = analyze_strategy_performance(data_with_signals)
   
    plot_data(data_with_metrics, short_window, long_window)
