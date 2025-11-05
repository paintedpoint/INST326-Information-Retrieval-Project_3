# Function Reference

## Overview

This document provides a reference for all major functions in the project. Each entry includes the function signature, description, parameters, return values, examples, and related functions.

## Table of Contents

Module: api_library

Class: PullData

Class: CryptoPortfolio

Module: utils

Class: 

Class: 

## Module: api_library

# **Class: PullData** 

# {

### def get_market_data(self, page: int = 1) -> pd.DataFrame

Gets the current market data for a list of 100 cryptocurrencies. Changing page allows viewing of different lists.

**Parameters**

    page           int       The current list of 100 cryptocurriencies

**Returns**

A pandas dataframe

**List of available keys**

    'id'
    'symbol'
    'name'
    'current_price'
    'market_cap'
    'market_cap_rank'
    'total_volume'
    'change_24h'
    'change_7d'

**Example:**

    dataPuller = PullData()
    market_data = dataPuller.get_market_data()
    display_market_data(market_data)

**Related functions**

    display_market_data()


### def get_crypto_details(self, crypto_id: str) -> Dict

Gets the crypto details of a single crypto

**Parameters**

    crypto_id       str     The name of a cryptocurrency

**Returns**

A pandas dataframe

**List of available keys**

    'id'
    'symbol'
    'name'
    'description'
    'current_price'
    'market_cap'
    'total_volume'
    'price_change_24h'
    'all_time_high'
    'all_time_low'
    'homepage'

**Example:**

    dataPuller = PullData()
    btc_details = dataPuller.get_crypto_details('bitcoin')
    print(f"Name: {btc_details['name']}")

Output: 

    "Name: Bitcoin"


### def get_historical_data(self, crypto_id: str, days: int = 30) -> pd.DataFrame

Gets the historical market data for a cryptocurrency.

**Parameters**

    crypto_id       str     The name of a cryptocurrency
    days            int     Days history to retrieve, max 365

**Returns**

A pandas dataframe

**List of available keys**

    'timestamp'
    'price'
    'date'

**Example:**

    dataPuller = PullData()
    eth_history = dataPuller.get_historical_data('bitcoin', days=7)
    print(eth_history)


### def get_current_price(self, crypto_ids: List[str], , vs_currency: str = "usd") -> Dict

Gets the current market data for a cryptocurrency/ies.

**Parameters**

    crypto_ids      list    The names of a cryptocurrency/ies
    vs_currency     str     The currency to display in

**Returns**

A dictionary

**Example:**

    dataPuller = PullData()
    crntBit = dataPuller.get_current_price(['bitcoin'])
    print(crntBit)

Outputs:

    {'bitcoin': 115109}

# }

# **Class: CryptoPortfolio**

# {

### def buy(self, crypto_id: str, amount: float):

Records a purchase of a specified amount of a cryptocurrency

**Parameters**

    crypto_id: str The CoinGecko ID of the cryptocurrency you want to buy.
    amount: float The number of units of the cryptocurrency to buy 

**Returns**

The function does not explicitly return anything (return None implicitly). Its main effect is side effects:It prints an error message if the price cannot be fetched. In the full class, it would also update portfolio holdings and transaction history.

**Example**

*Something Here*

**Output**

*Something Here*

### def sell(self, crypto_id: str, amount: float):

The sell function sells a specified amount of a cryptocurrency from the user’s portfolio.

**Parameter**

    crypto_id: str The CoinGecko ID of the cryprocurrency to sell
    amount: float The quantity of the cryptocurrency to sell

**Examples**

    portfolio.sell('bitcoin', 0.005)

**Output**

*Something Here*

### def portfolio_value(self):

Calculates and displays the total value of the portfolio based on current cryptocurrency holdings and live market prices.

**Returns**

total_value (float) — the sum of the value of all cryptocurrencies in the portfolio.
If there are no holdings, returns 0.0.

**Example**

    portfolio = MyPortfolioClass()
    portfolio.holdings = {
        'BTC': {'amount': 0.5},
        'ETH': {'amount': 2}
    }
    total = portfolio.portfolio_value()

**Output**

*Something Here*

### def show_transactions(self):

Displays the transaction history of the portfolio, showing details of each buy or sell transaction, including time, amount, cryptocurrency, price, and profit for sales.

**Examples**

    portfolio = MyPortfolioClass()
    portfolio.transactions[{'type': 'SELL', 'crypto': 'ETH', 'amount': 1, 'price': 2000, 'time': '2025-10-12 15:00', 'profit': 100}]
    portfolio.show_transactions()

**Output**

*Something Here*

# }

## Module: utils

# **Class: _______**

# {

### def display_market_data(df: pd.DataFrame, limit: int = 10) -> None

Displays market data in a user freindly format

**Parameters**

    df          pd.DataFrame        A dataframe generated from the API request

**Example:**

    dataPuller = PullData()
    market_data = dataPuller.get_market_data()
    display_market_data(market_data)


### def summarize_market_performance(df: pd.DataFrame) -> None

Displays the top gainer and top loser.

**Parameters**

    df          pd.DataFrame        A dataframe generated from the API request

**Example:**

    dataPuller = PullData()
    market_data = dataPuller.get_market_data()
    summarize_market_performance(market_data)


### def user_interaction(df: pd.DataFrame) -> None

A user interface including user selection

**Parameters**

    df          pd.DataFrame        A dataframe generated from the API request

**Example:**

    dataPuller = PullData()
    market_data = dataPuller.get_market_data()
    user_interaction(market_data)

# }

# **Class: _____**

# {



# }

# Function Reference Structure:

Brief Description

**Parameters**

    var_name           var_type       Brief description of var
    var_name2           var_type2       Brief description of var2

**Returns**

If applicable, describe returned item

**Example:**

    Code example using this fuction

**Related functions**

    List any other fuctions if this uses another fuction