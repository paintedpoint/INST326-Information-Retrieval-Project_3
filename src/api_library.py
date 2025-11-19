from abc import abstractmethod
import requests
import pandas as pd
from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import unittest

class PullData:
    """
    Class for fetching and processing data from CoinGecko API
    Work by William
    """

    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3"
        self.last_request_time = 0
        self.rate_limit_delay = 10.0
        self.max_retries = 5

    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        while True:
            # Enforce minimum time between requests
            now = time.time()
            elapsed = now - self.last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)

            # Attempt request once caller executes
            self.last_request_time = time.time()

            # After caller executes the actual request, check response
            # We can monkey-patch requests.get temporarily to inject retry handling
            original_get = requests.get

            def limited_get(*args, **kwargs):
                retries = 0
                while True:
                    resp = original_get(*args, **kwargs)
                    if resp.status_code == 429:  # Too Many Requests
                        retry_after = resp.headers.get("Retry-After")
                        if retry_after:
                            wait = float(retry_after)
                        else:
                            wait = self.rate_limit_delay * (2 ** retries)
                        print(f"429 received — retrying in {wait:.1f}s...")
                        time.sleep(wait)
                        retries += 1
                        if retries > self.max_retries:
                            raise RuntimeError("Exceeded retry limit after rate limiting")
                        continue
                    return resp

            requests.get = limited_get
            return

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make a rate-limited request to the API
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        self._rate_limit()
        url = f"{self.url}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        
    def get_market_data(self, page: int = 1) -> pd.DataFrame:
        """
        Get current market data for multiple cryptocurrencies
        
        Args:
            page: Page number
            
        Returns:
            DataFrame with market data
        """
        params = {
            "vs_currency": 'usd',
            "order": "market_cap_desc",
            "per_page": 100,
            "page": page,
            "sparkline": False,
            "price_change_percentage": "24h,7d"
        }
        
        data = self._make_request("coins/markets", params)

        if not data:
            return pd.DataFrame()
        
        # Convert to DataFrame and select relevant columns
        df = pd.DataFrame(data)
        df = df[[
            'id', 'symbol', 'name', 'current_price', 
            'market_cap', 'market_cap_rank', 'total_volume',
            'price_change_percentage_24h', 'price_change_percentage_7d_in_currency'
        ]]
        
        # Rename columns
        df = df.rename(columns={
            'price_change_percentage_24h': 'change_24h',
            'price_change_percentage_7d_in_currency': 'change_7d'
        })
        
        return df
    
    def get_crypto_details(self, crypto_id: str) -> Dict:
        """
        Get detailed information about a specific cryptocurrency
        
        Args:
            crypto_id: CoinGecko ID (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            Dictionary with crypto details including description
        """
        data = self._make_request(f"coins/{crypto_id}")
        
        if not data:
            return {}
        
        # Extract only relevant information
        details = {
            'id'                : data.get('id'),
            'symbol'            : data.get('symbol', '').upper(),
            'name'              : data.get('name'),
            'description'       : data.get('description', {}).get('en', 'No description available'),
            'current_price'     : data.get('market_data', {}).get('current_price', {}).get('usd'),
            'market_cap'        : data.get('market_data', {}).get('market_cap', {}).get('usd'),
            'total_volume'      : data.get('market_data', {}).get('total_volume', {}).get('usd'),
            'price_change_24h'  : data.get('market_data', {}).get('price_change_percentage_24h'),
            'all_time_high'     : data.get('market_data', {}).get('ath', {}).get('usd'),
            'all_time_low'      : data.get('market_data', {}).get('atl', {}).get('usd'),
            'homepage'          : data.get('links', {}).get('homepage', [''])[0]
        }
        
        return details
    
    def get_historical_data(self, crypto_id: str, days: int = 30) -> pd.DataFrame:
        """
        Get historical price data for a cryptocurrency
        
        Args:
            crypto_id: CoinGecko ID (e.g., 'bitcoin', 'ethereum')
            days: Number of days of historical data (max 365)
            
        Returns:
            DataFrame with timestamp and price columns
        """
        params = {
            "vs_currency": 'usd',
            "days": days
        }
        
        data = self._make_request(f"coins/{crypto_id}/market_chart", params)
        
        if not data or 'prices' not in data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['date'] = df['timestamp'].dt.date
        
        return df
    
    def get_current_price(self, crypto_ids: List[str], vs_currency: str = "usd") -> Dict:
        """
        Get current prices for multiple cryptocurrencies
        
        Args:
            crypto_ids: List of CoinGecko IDs
            vs_currency: Currency to compare against
            
        Returns:
            Dictionary mapping crypto_id to price
        """
        params = {
            "ids": ",".join(crypto_ids),
            "vs_currencies": vs_currency
        }
        
        data = self._make_request("simple/price", params)
        if not data:
            return {}
        
        # Flatten the nested structure
        prices = {crypto_id: info.get(vs_currency, 0) 
                 for crypto_id, info in data.items()}
        
        return prices

class Transaction:
    pointPrice: int

    def __init__(self, crypto_id: str, datapuller: PullData, amount):
        self.crypto_id = crypto_id
        self.datapuller = datapuller
        self.amount = amount
        self._timestamp = datetime.now()

    @abstractmethod
    def value(self):
        pass

    def name(self):
        return self.crypto_id

    def amount(self):
        return self.amount
    
    def __str__(self):
        pass

    def __repr__(self):
        pass

class Buy(Transaction):
    def __init__(self, crypto_id: str, datapuller: PullData, amount):
        super(crypto_id, datapuller, amount)
        
        price_data = self.data_puller.get_current_price([crypto_id])
        if not price_data or crypto_id not in price_data:
            print("Error: Could not fetch price for", crypto_id)
            return
        
        self.pointPrice = price_data[crypto_id]

    def value(self):
        return -1 * self.amount * self.pointPrice

class Sell(Transaction):
    def __init__(self, crypto_id: str, datapuller: PullData, amount):
        super(crypto_id, datapuller, amount)
        
        price_data = self.data_puller.get_current_price([crypto_id])
        if not price_data or crypto_id not in price_data:
            print("Error: Could not fetch price for", crypto_id)
            return
        
        self.pointPrice = price_data[crypto_id]

    def value(self):
        return self.amount * self.pointPrice

class Portfolio:
    def __init__(self, startingFunds: float):
        self._transactions = List[Transaction]
        self.funds = startingFunds
        self.portfolio_value = 0

    def makeTransaction(self, transaction: Transaction):
        self._transactions.append(transaction)
        self.funds += transaction.value()

    def seePastTransactions(self) -> None:
        print(self._transactions)

    def seeCurrentFunds(self) -> float:
        return round(self.funds, 2)

    def seePortfolioValue(self) -> float:
        pass


    

# class CryptoPortfolio:
#     """
#     Class to manage cryptocurrency purchases and sales
#     """

#     def __init__(self, data_puller: PullData):
#         self.data_puller = data_puller
#         self.holdings = {}  # {crypto_id: {'amount': float, 'avg_buy_price': float}}
#         self.transactions = []  # list of transaction dictionaries

#     def buy(self, crypto_id: str, amount: float):
#         """Buy a specified amount of a cryptocurrency"""
#         price_data = self.data_puller.get_current_price([crypto_id])
#         if not price_data or crypto_id not in price_data:
#             print("Error: Could not fetch price for", crypto_id)
#             return
        
#         current_price = price_data[crypto_id]
#         cost = amount * current_price

#         # Update holdings
#         if crypto_id in self.holdings:
#             prev = self.holdings[crypto_id]
#             total_value = prev['amount'] * prev['avg_buy_price'] + cost
#             total_amount = prev['amount'] + amount
#             prev['amount'] = total_amount
#             prev['avg_buy_price'] = total_value / total_amount
#         else:
#             self.holdings[crypto_id] = {'amount': amount, 'avg_buy_price': current_price}

#         # Record transaction
#         self.transactions.append({
#             'type': 'BUY',
#             'crypto': crypto_id,
#             'amount': amount,
#             'price': current_price,
#             'time': datetime.now()
#         })
#         print(f"Bought {amount} {crypto_id} at ${current_price:.2f} each (${cost:.2f} total)")

#     def sell(self, crypto_id: str, amount: float):
#         """Sell a specified amount of a cryptocurrency"""
#         if crypto_id not in self.holdings or self.holdings[crypto_id]['amount'] < amount:
#             print("Error: Not enough holdings to sell.")
#             return
        
#         price_data = self.data_puller.get_current_price([crypto_id])
#         if not price_data or crypto_id not in price_data:
#             print("Error: Could not fetch price for", crypto_id)
#             return
        
#         current_price = price_data[crypto_id]
#         proceeds = amount * current_price
#         cost_basis = amount * self.holdings[crypto_id]['avg_buy_price']
#         profit = proceeds - cost_basis

#         self.holdings[crypto_id]['amount'] -= amount
#         if self.holdings[crypto_id]['amount'] == 0:
#             del self.holdings[crypto_id]

#         self.transactions.append({
#             'type': 'SELL',
#             'crypto': crypto_id,
#             'amount': amount,
#             'price': current_price,
#             'profit': profit,
#             'time': datetime.now()
#         })
#         print(f" Sold {amount} {crypto_id} at ${current_price:.2f} each "
#               f"(${proceeds:.2f} total, Profit: ${profit:.2f})")

#     def portfolio_value(self):
#         """Return the total value of current holdings based on live prices"""
#         if not self.holdings:
#             print("No holdings in portfolio.")
#             return 0.0

#         ids = list(self.holdings.keys())
#         prices = self.data_puller.get_current_price(ids)
#         total_value = 0

#         print("\n Current Portfolio Value:")
#         for crypto_id in ids:
#             amount = self.holdings[crypto_id]['amount']
#             price = prices.get(crypto_id, 0)
#             value = amount * price
#             total_value += value
#             print(f" - {crypto_id:<10} {amount:.4f} @ ${price:.2f} = ${value:,.2f}")

#         print(f" Total Portfolio Value: ${total_value:,.2f}")
#         return total_value

#     def show_transactions(self):
#         """Display transaction history"""
#         if not self.transactions:
#             print("No transactions yet.")
#             return
        
#         print("\n Transaction History:")
#         for t in self.transactions:
#             if t['type'] == 'BUY':
#                 print(f"{t['time']} | BUY  {t['amount']} {t['crypto']} @ ${t['price']:.2f}")
#             else:
#                 print(f"{t['time']} | SELL {t['amount']} {t['crypto']} @ ${t['price']:.2f} "
#                       f"(Profit: ${t['profit']:.2f})")

# class CryptoAsset:
#     """Represents a cryptocurrency asset."""

#     def __init__(self, crypto_id: str, name: str, symbol: str, current_price: float = 0.0):
#         if not crypto_id.strip():
#             raise ValueError("crypto_id cannot be empty.")
#         if current_price < 0:
#             raise ValueError("Price cannot be negative.")
#         self._crypto_id = crypto_id
#         self._name = name
#         self._symbol = symbol
#         self._current_price = current_price

#     @property
#     def crypto_id(self):
#         return self._crypto_id

#     @property
#     def current_price(self):
#         return self._current_price

#     @current_price.setter
#     def current_price(self, price: float):
#         if price < 0:
#             raise ValueError("Price must be non-negative.")
#         self._current_price = price

#     def __repr__(self):
#         return f"CryptoAsset({self._crypto_id}, price={self._current_price:.2f})"

#     def __str__(self):
#         return f"{self._name} ({self._symbol.upper()}): ${self._current_price:.2f}"

# class Transaction:
#     """Represents a single crypto buy or sell transaction."""

#     def __init__(self, txn_type: str, crypto_id: str, amount: float, price: float, profit: float = 0.0):
#         if txn_type not in ("BUY", "SELL"):
#             raise ValueError("Transaction type must be 'BUY' or 'SELL'.")
#         if amount <= 0 or price <= 0:
#             raise ValueError("Amount and price must be positive.")
#         self._txn_type = txn_type
#         self._crypto_id = crypto_id
#         self._amount = amount
#         self._price = price
#         self._profit = profit
#         self._timestamp = datetime.now()

#     @property
#     def profit(self):
#         return self._profit

#     @property
#     def crypto_id(self):
#         return self._crypto_id

#     def __repr__(self):
#         return f"Transaction({self._txn_type}, {self._crypto_id}, amount={self._amount}, price={self._price})"

#     def __str__(self):
#         ts = self._timestamp.strftime("%Y-%m-%d %H:%M:%S")
#         if self._txn_type == "BUY":
#             return f"[{ts}] BUY {self._amount} {self._crypto_id} @ ${self._price:.2f}"
#         else:
#             return f"[{ts}] SELL {self._amount} {self._crypto_id} @ ${self._price:.2f} (Profit: ${self._profit:.2f})"

# class User:
#     """Represents a user who owns a crypto portfolio."""

#     def __init__(self, username: str):
#         if not username.strip():
#             raise ValueError("Username cannot be empty.")
#         self._username = username
#         self._portfolio: CryptoPortfolio | None = None

#     def link_portfolio(self, portfolio: CryptoPortfolio):
#         """Link a CryptoPortfolio to the user."""
#         if not isinstance(portfolio, CryptoPortfolio):
#             raise TypeError("Expected a CryptoPortfolio instance.")
#         self._portfolio = portfolio

#     def __str__(self):
#         value = self._portfolio.portfolio_value() if self._portfolio else 0
#         return f"User: {self._username} | Portfolio Value: ${value:,.2f}"

#     def __repr__(self):
#         return f"User({self._username})"

class MarketData:
    """
    Grabs Market data(Cryptocurrency) From API
    Works by Christopher
    """

    def __init__(self, start_currency: str = 'usd'):
        """
        Args:
            start_currency (str): Currency for price data (Uses USD)
        
        Raises:
            ValueError: If start_currency is invaild or empty
        """
        if not start_currency or not start_currency.strip():
            raise ValueError("Base currency cannot be empty")

        self._base_currency = start_currency
        self._data = pd.DataFrame()
        self._previous_updates = None
        self._api_url = "https://api.coingecko.com/api/v3/coins/markets"

    @property
    def data(self):
        # pd.dataFrame -> Gets current market data
        return self._data.copy()

    @property
    def previous_update(self) -> bool:
        # datetime Gets timestamp from last update
        return self._previous_updates

    def fetch_data(self, limit: int = 100):
        """
        Fetch Market data from CoinGecko
        
        Args:
            limit(int): Num of Crypto to fetch

        Returns:
            bool: True if works, False if doesn't
        
        Raises:
            ValueError: If limit is out of range

        """
        if not 1<= limit <= 250:
            raise ValueError("Limit must be in 1 - 250")
        
        try:
            params = {
                'vs_currency': self._base_currency,
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }

            print(f"Fetching {limit} Crypto...")
            response = requests.get(self._api_url, params=params, timeout=10)

            if response.status_code == 429:
                print("Limit Exceed. Please Wait.")
                return False
            
            response.raise_for_status()
            data = response.json()

            if not data:
                print("API is empty")
                return False
            
            crypto_list = []
            for i in data:
                if not all(j in i for j in ['name', 'symbol', 'current_price']):
                    continue

                crypto_list.append({
                    'name': i.get('name', 'Unknown'),
                    'symbol': i.get('symbol', 'unknown'),
                    'current_price': i.get('current_price', 0),
                    'change_24h': i.get('price_change_percentage_24h', 0),
                    'market_cap': i.get('market_cap', 0),
                    'volume_24h': i.get('total_volume', 0),
                    'high_24h': i.get('high_24h', 0),
                    'low_24h': i.get('low_24h', 0)
                })
             
            if not crypto_list:
                print("No Coin found")
                return False

            self._data = pd.DataFrame(crypto_list)
            self._previous_updates = datetime.now()
            print("Successfully fetched")
            return True
        except requests.exceptions.Timeout:
            print("❌ Request timeout. Check your internet connection.")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection error. Check your internet connection.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching data: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def get_crypto_price(self, symbol: str):
        """
        Gets current price for a Specific cyptocurrency

        Args:
            symbol = Crypto symbol
        
        Returns:
            float: Current price
        
        Raises:
            ValueError: If symbol - empty
        """

        if not symbol or not symbol.strip():
            raise ValueError("Symbol cannot be empty")
        
        if self._data.empty:
            return None
        
        lower_symbol = symbol.lower().strip()
        crypto = self._data[self._data['symbol'] == lower_symbol]

        if not crypto.empty:
            return crypto.iloc[0]['current_price']
        return None
    
    def display_top(self, limit: int = 10):
        """
        Display formatted table of top crypto

        Args:
            limit(int): Num of crypto to display
        """
        if self._data.empty:
            print("No data available")
            return
        print(f"\n{'Name':<20} {'Symbol':<10} {'Price (USD)':>15} {'24h Change':>15}")
        print("-" * 70)
        
        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"

        for _, row in self._data.head(limit).iterrows():
            name = row['name']
            symbol = row['symbol'].upper()
            price = row['current_price']
            change = row['change_24h']
            
            if change >= 0:
                color = GREEN
                arrow = "▲"
                sign = "+"
            else:
                color = RED
                arrow = "▼"
                sign = ""
            
            print(f"{name:<20} {symbol:<10} ${price:>14,.2f} {color}{arrow} {sign}{change:.2f}%{RESET}")
        
        print("-" * 70)

class Portfolio_Helper:
    """
    Creates a mock portofolio to generate Charts and Graphs

    """   

    def __init__(self, user: str, portfolio_id: str):
        pass

    def get_user_name(self):
        pass
    
class Price_Charts_Graphs:
    """
    Generates Charts from Crypto Data Using matplot

    """

    def __init__(self):
        """
        Initialize chart generator
        """
        self._default_figure_size = (12,6)
        self._color_positive = "#2ecc71"
        self._color_negative = "#e74c3c"
    
    def create_price_chart(self, market_data = MarketData, top_n: int = 10,
                           save_path: Optional[str] = None):
        if not isinstance(market_data, MarketData):
            raise TypeError("market_data must be a MarketData instance")
        
        if not 1 <= top_n <= 50:
            raise ValueError("top_n must be between 1 and 50")
        
        if market_data.data.empty:
            print("No data available for chart")
            return False
        
        try:
            df = market_data.data.head(top_n).copy()
            df['label'] = df['symbol'].str.upper() + ' - ' + df['name']
            
            plt.figure(figsize=self._default_figure_size)
            plt.barh(df['label'], df['current_price'], color='#3498db')
            plt.xlabel('Price (USD)', fontsize=12, fontweight='bold')
            plt.ylabel('Cryptocurrency', fontsize=12, fontweight='bold')
            plt.title(f'Top {top_n} Cryptocurrencies by Price', fontsize=14, fontweight='bold')
            plt.gca().invert_yaxis()
            
            for i, price in enumerate(df['current_price']):
                plt.text(price, i, f' ${price:,.2f}', va='center', fontsize=9)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"[DONE] Chart saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error creating chart: {e}")
            plt.close()
            return False
    
    def create_changing_chart(self, market_data = MarketData, top_n: int = 10,
                              save_path: Optional[str] = None):
        """Create bar chart of 24-hour price changes.
        
        Args:
            market_data (MarketData): Market data object
            top_n (int): Number of cryptos to display
            save_path (str): Optional path to save chart
            
        Returns:
            bool: True if successful
        """
        if not isinstance(market_data, MarketData):
            raise TypeError("market_data must be a MarketData instance")
        
        if market_data.data.empty:
            print("[ERROR]No data available for chart")
            return False
        
        try:
            df = market_data.data.head(top_n).copy()
            df['label'] = df['symbol'].str.upper() + ' - ' + df['name']
            
            colors = [self._color_positive if x >= 0 else self._color_negative 
                     for x in df['change_24h']]
            
            plt.figure(figsize=self._default_figure_size)
            plt.barh(df['label'], df['change_24h'], color=colors)
            plt.xlabel('24h Change (%)', fontsize=12, fontweight='bold')
            plt.ylabel('Cryptocurrency', fontsize=12, fontweight='bold')
            plt.title(f'24-Hour Price Changes - Top {top_n}', fontsize=14, fontweight='bold')
            plt.gca().invert_yaxis()
            plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            
            for i, change in enumerate(df['change_24h']):
                sign = '+' if change >= 0 else ''
                plt.text(change, i, f' {sign}{change:.2f}%', va='center', fontsize=9)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"[DONE] Chart saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error creating chart: {e}")
            plt.close()
            return False