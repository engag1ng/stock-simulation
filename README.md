# Metis
CFD trading simulation for back- and forward testing different trading strategies.

<img src="https://github.com/user-attachments/assets/ae2d0c41-c6ba-4ae9-8410-69bfeb31da9c" width=75% height=75%>

<img src="https://github.com/user-attachments/assets/741a3a4b-5e67-414c-a307-7ec6d6e360ed" width=75% height=75%>

⭐ Please star this repository — it motivates a lot!

## 🚀 About
Stocks and CFD's are a great way to start trading and earn some money. But what strategy should I use to **actually** make money 💵. This is where this simulator comes in. You can use predefined strategies or implement your own strategy and test how well it would perform long-term on any CFD listed by yfinance.

## 📝 Getting started
### Prerequisites
- Python >=3.13
### Installation
> [!NOTE]
> Note that the virtual environment **always** has to be active when trying to run simulations.

- Clone repository: `git clone https://github.com/engag1ng/stock-simulation.git`
- Create virtual environment: `python -m venv .venv`
- Activate virtual environment: `.venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

### Usage
1. Replace the parameters in `MAIN.py`, to your liking.
2. Run `python MAIN.py`

## ℹ️ Documentation
Before adding new features, indicators or strategies, it is important to understand, what each one is intended for.

Features: provide the ability to calculate values (columns) of data, that help make informed decisions for trading or just help to calcuate other values.

Indicators: typically returns a value between -10 and 10 which indicates, if we should buy (positive) or sell (negative) and how much, where 0 indicates holding, 10 indicates going all-in bullish and -10 indicates all-in bearish.

Strategies: Combining features and indicators to create an algorithm, that makes trading decisions, like buying / selling and setting stop-loss/take-profit. 

## Add a New Feature

**Location:** `features/`

1. Create a new file in the `features/` directory.
2. Define your feature function, for example:

```python
def feature_daily_return(df):
    return df['Close'].pct_change().fillna(0)
```

## Add a New Indicator

**Location:** `indicators/`

1. Create a new file or add to an existing one in the `indicators/` directory.
2. Use the `@register_indicator` decorator to register it automatically:

```python
from indicators import register_indicator

@register_indicator
def indicator_my_custom(df):
    return df['Close'].rolling(window=10).mean()
```

## Add a New Strategy

**Location:** `strategies/`

1. Create a new file or add to an existing one in the `strategies/` directory.
2. Subclass the `Strategy` base class and use the `@Strategy.register` decorator with a unique name:

```python
from strategies.base import Strategy

@Strategy.register("my_custom_strategy")
class MyCustomStrategy(Strategy):
    def execute(self, df, owned_stocks, price, capital):
        # Your buy/sell logic here
        return 0.1, [price * 0.95, 0.1], [price * 1.05, 0.1]
```

## ⏱️ Roadmap
- [ ] Implement new strategies
- [ ] Add extensive documentation
- [ ] Improve simulation sequencing
- [ ] Improve UI

## 🤝 Contributions
**Community contributions are very welcome.** Please see below how you can contribute...

1. Find bugs and report them.
2. Make recommendations.
3. Make improvements to the code base.
4. Make improvements to the documentation.

## 📃 License
This project is GNU GPLv3 licensed. Please have a look at the LICENSE.md for more information.

## 🗨️ Contact
Please contact me under constantin.reinhold@gmx.net
