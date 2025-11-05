import requests
import pandas as pd 
import matplotlib.pyplot as plt
import unittest
from typing import Dict, List, Optional
from datetime import datetime, timedelta

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


# Demo Code
if __name__ == "__main__":
    print("="*70)
    print("CRYPTO CHARTS DEMO")
    print("="*70)

    market = MarketData()

    if market.fetch_data(limit=50):
        charts = Price_Charts_Graphs()
        
        print("\n * Generating Price Chart...")
        charts.create_price_chart(market, top_n=15)  # Pass market object, not data
        
        print("\n * Generating 24h Change Chart...")
        charts.create_changing_chart(market, top_n=15)  # Correct method name
        
        print("\n✅ DONE!")
    else:
        print("[ERROR] Failed to fetch data")

