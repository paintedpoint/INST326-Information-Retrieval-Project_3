# Usage Examples

## Overview
This document demonstrates how to use all major components of the project, including:
- API data retrieval (`api_library.py`)
- Market visualization and summaries (`utils.py`)
- Portfolio management and transactions (`CryptoPortfolio` class)

Each example shows typical function usage and expected output.

# Module: api_library

# Class: PullData

## Example 1 — Fetch and Display Market Data
```python
from api_library import PullData

dataPuller = PullData()
market_data = dataPuller.get_market_data()
print(market_data.head())
```
Description:

Retrieves the top 100 cryptocurrencies by market capitalization and prints the first few rows of the DataFrame.

## Example 2 — Fetch Details for a Specific Cryptocurrency
```python
from src import PullData

btc_details = dataPuller.get_crypto_details('bitcoin')
print(f"Name: {btc_details['name']}")
print(f"Price: ${btc_details['current_price']:,.2f}")
```
Description:

Fetches detailed market information for Bitcoin including name, price, and description.

## Example 3 — Fetch Historical Price Data
```python
from src import PullData

btc_history = dataPuller.get_historical_data('bitcoin', days=7)
print(btc_history.tail())
```
Description:
Retrieves 7 days of historical price data for Bitcoin and prints the last few entries.

## Example 4 — Get Current Prices for Multiple Cryptos
```python
prices = dataPuller.get_current_price(['bitcoin', 'ethereum', 'solana'])
print(prices)
```

Expected Output:
```python
{'bitcoin': 67842, 'ethereum': 3831, 'solana': 172.34}
```

# Class: CryptoPortfolio

## Example 5 — Initialize and Buy Cryptocurrencies
```python
from api_library import CryptoPortfolio, PullData

dataPuller = PullData()
portfolio = CryptoPortfolio(dataPuller)

portfolio.buy('bitcoin', 0.01)
portfolio.buy('ethereum', 0.05)
```
Description:

Creates a new portfolio and records crypto purchases using real-time prices.

Expected Output:
```python
Bought 0.01 bitcoin at $68,000.00 each ($680.00 total)
Bought 0.05 ethereum at $3,800.00 each ($190.00 total)
```

## Example 6 — Sell Cryptocurrency Holdings
```python
portfolio.sell('bitcoin', 0.005)
```
Description:

Sells a portion of Bitcoin holdings and records profit or loss.

Expected Output:
```python
Sold 0.005 bitcoin at $69,000.00 each ($345.00 total, Profit: $10.50)
```

## Example 7 — View Current Portfolio Value
```python
portfolio.portfolio_value()
```
Description:

Calculates total portfolio value in USD based on live market prices.

Expected Output:
```python
Current Portfolio Value:
 - bitcoin     0.0050 @ $68,500.00 = $342.50
 - ethereum    0.0500 @ $3,750.00 = $187.50
Total Portfolio Value: $530.00
```

## Example 8 — View Transaction History
```python
portfolio.show_transactions()
```
Description:

Displays all buy and sell transactions, including timestamps, prices, and profit for each sale.

Expected Output:
```py
Transaction History:
2025-10-11 15:43:20 | BUY  0.0100 bitcoin @ $68,000.00
2025-10-11 16:02:45 | SELL 0.0050 bitcoin @ $69,000.00 (Profit: $10.50)
```
# Module: utils

## Example 9 — Display Market Data in User-Friendly Format
```py
from utils import display_market_data

display_market_data(market_data)
```
Description:

Prints a formatted, color-coded display of cryptocurrencies showing price and 24-hour changes.

Expected Output:
```
Name                 Symbol      Price (USD)     24h Change
------------------------------------------------------------
Bitcoin              BTC         68,421.25         ▼ -0.45%
Ethereum             ETH          3,782.10         ▲ +0.32%
...
```

## Example 10 — Display Top Gainers and Losers
```py
from utils import summarize_market_performance

summarize_market_performance(market_data)
```
Description:

Displays the top gainer and loser based on 24-hour performance.

Expected Output:
```py
Top Gainer: Solana (+5.82%)
Top Loser: Dogecoin (-8.11%)
```



### Notes

All data is retrieved from the CoinGecko API.
