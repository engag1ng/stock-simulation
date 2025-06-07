from tkinter import Tk, Label, Entry, Button
import re

def spawn_ui():
    """
    Launch a simple Tkinter-based graphical user interface (GUI) to collect trading simulation parameters.

    The UI prompts the user to input:
    - Start capital (integer)
    - Transaction fee (float, e.g., 0.01 for 1%)
    - Yearly custody fee (float, e.g., 0.02 for 2%)
    - Trading strategy (string key referencing a strategy)
    - Ticker symbol for stock data (string, e.g., "^GSPC")
    - Backtesting period (string, e.g., "10y" for 10 years)
    - Simulation period (string, e.g., "10y" for 10 years)
    - Precompute values (comma-separated string of indicator names)

    Input validation:
    - Start capital accepts only integers.
    - Transaction fee and custody fee accept signed decimal numbers.

    The UI blocks execution until the user confirms or closes the window.
    
    Returns:
        tuple or None: A tuple containing the parsed input values in the order:
            (capital: int,
             transaction_fee: float,
             yearly_custody_fee: float,
             strategy_key: str,
             ticker: str,
             real_period: str,
             sim_period: str,
             precompute_string: str)
        
        Returns None if the window is closed without confirmation.

    Usage:
        params = spawn_ui()
        if params is not None:
            capital, transaction_fee, custody_fee, strategy_key, ticker, real_period, sim_period, precompute = params

    """
    def only_integers(char):
        return char == "" or char.isdigit()

    def integers_and_floats(char):
        return char == "" or re.fullmatch(r'-?\d*\.?\d*', char) is not None

    root = Tk()
    result = {}

    validate_integer = (root.register(only_integers), '%P')
    validate_int_and_float = (root.register(integers_and_floats), '%P')

    Label(root, text="Start capital").grid(row=0)
    capital_entry = Entry(root, validate='key', validatecommand=validate_integer)
    capital_entry.grid(row=0, column=1)
    capital_entry.insert(0, "10000")

    Label(root, text="Transaction fee").grid(row=1)
    transaction_fee_entry = Entry(root, validate='key', validatecommand=validate_int_and_float)
    transaction_fee_entry.grid(row=1, column=1)
    transaction_fee_entry.insert(0, "0.01")

    Label(root, text="Yearly custody fee").grid(row=2)
    custody_fee_entry = Entry(root, validate='key', validatecommand=validate_int_and_float)
    custody_fee_entry.grid(row=2, column=1)
    custody_fee_entry.insert(0, "0.02")

    Label(root, text="Trading strategy").grid(row=3)
    strategy_entry = Entry(root)
    strategy_entry.grid(row=3, column=1)
    strategy_entry.insert(0, "strategy_three_ema_crossover")

    Label(root, text="Ticker").grid(row=4)
    ticker_entry = Entry(root)
    ticker_entry.grid(row=4, column=1)
    ticker_entry.insert(0, "^GSPC")

    Label(root, text="Backtesting period").grid(row=5)
    real_time_entry = Entry(root)
    real_time_entry.grid(row=5, column=1)
    real_time_entry.insert(0, "10y")

    Label(root, text="Simulation period").grid(row=6)
    sim_time_entry = Entry(root)
    sim_time_entry.grid(row=6, column=1)
    sim_time_entry.insert(0, "10y")

    Label(root, text="Precompute values (comma separated)").grid(row=7)
    precompute_entry = Entry(root)
    precompute_entry.grid(row=7, column=1)
    precompute_entry.insert(0, "indicator_three_ema_crossover")

    def execute_button():
        result['values'] = (
            int(capital_entry.get()),
            float(transaction_fee_entry.get()),
            float(custody_fee_entry.get()),
            strategy_entry.get(),
            ticker_entry.get(),
            real_time_entry.get(),
            sim_time_entry.get(),
            precompute_entry.get()
        )
        root.destroy()

    Button(root, text="Confirm", command=execute_button).grid(row=8, column=1)
    root.bind("<Return>", lambda event: execute_button())
    
    root.mainloop()

    return result.get('values')  # Will return None if the user closed the window