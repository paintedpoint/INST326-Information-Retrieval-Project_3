import requests
import pandas as pd
from typing import Dict, List
import time
from datetime import datetime

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
    
class CryptoPortfolio:
    """
    Class to manage cryptocurrency purchases and sales
    """

    def __init__(self, data_puller: PullData):
        self.data_puller = data_puller
        self.holdings = {}  # {crypto_id: {'amount': float, 'avg_buy_price': float}}
        self.transactions = []  # list of transaction dictionaries

    def buy(self, crypto_id: str, amount: float):
        """Buy a specified amount of a cryptocurrency"""
        price_data = self.data_puller.get_current_price([crypto_id])
        if not price_data or crypto_id not in price_data:
            print("Error: Could not fetch price for", crypto_id)
            return
        
        current_price = price_data[crypto_id]
        cost = amount * current_price

        # Update holdings
        if crypto_id in self.holdings:
            prev = self.holdings[crypto_id]
            total_value = prev['amount'] * prev['avg_buy_price'] + cost
            total_amount = prev['amount'] + amount
            prev['amount'] = total_amount
            prev['avg_buy_price'] = total_value / total_amount
        else:
            self.holdings[crypto_id] = {'amount': amount, 'avg_buy_price': current_price}

        # Record transaction
        self.transactions.append({
            'type': 'BUY',
            'crypto': crypto_id,
            'amount': amount,
            'price': current_price,
            'time': datetime.now()
        })
        print(f"Bought {amount} {crypto_id} at ${current_price:.2f} each (${cost:.2f} total)")

    def sell(self, crypto_id: str, amount: float):
        """Sell a specified amount of a cryptocurrency"""
        if crypto_id not in self.holdings or self.holdings[crypto_id]['amount'] < amount:
            print("Error: Not enough holdings to sell.")
            return
        
        price_data = self.data_puller.get_current_price([crypto_id])
        if not price_data or crypto_id not in price_data:
            print("Error: Could not fetch price for", crypto_id)
            return
        
        current_price = price_data[crypto_id]
        proceeds = amount * current_price
        cost_basis = amount * self.holdings[crypto_id]['avg_buy_price']
        profit = proceeds - cost_basis

        self.holdings[crypto_id]['amount'] -= amount
        if self.holdings[crypto_id]['amount'] == 0:
            del self.holdings[crypto_id]

        self.transactions.append({
            'type': 'SELL',
            'crypto': crypto_id,
            'amount': amount,
            'price': current_price,
            'profit': profit,
            'time': datetime.now()
        })
        print(f" Sold {amount} {crypto_id} at ${current_price:.2f} each "
              f"(${proceeds:.2f} total, Profit: ${profit:.2f})")

    def portfolio_value(self):
        """Return the total value of current holdings based on live prices"""
        if not self.holdings:
            print("No holdings in portfolio.")
            return 0.0

        ids = list(self.holdings.keys())
        prices = self.data_puller.get_current_price(ids)
        total_value = 0

        print("\n Current Portfolio Value:")
        for crypto_id in ids:
            amount = self.holdings[crypto_id]['amount']
            price = prices.get(crypto_id, 0)
            value = amount * price
            total_value += value
            print(f" - {crypto_id:<10} {amount:.4f} @ ${price:.2f} = ${value:,.2f}")

        print(f" Total Portfolio Value: ${total_value:,.2f}")
        return total_value

    def show_transactions(self):
        """Display transaction history"""
        if not self.transactions:
            print("No transactions yet.")
            return
        
        print("\n Transaction History:")
        for t in self.transactions:
            if t['type'] == 'BUY':
                print(f"{t['time']} | BUY  {t['amount']} {t['crypto']} @ ${t['price']:.2f}")
            else:
                print(f"{t['time']} | SELL {t['amount']} {t['crypto']} @ ${t['price']:.2f} "
                      f"(Profit: ${t['profit']:.2f})")
                

