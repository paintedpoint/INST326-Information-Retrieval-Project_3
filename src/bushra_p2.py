import requests
import time
from typing import Dict, List

class PullData:
    """Fetch and process cryptocurrency data from the CoinGecko API."""

    def __init__(self, base_url: str = "https://api.coingecko.com/api/v3", rate_limit_delay: float = 1.5):
        """
        Initialize PullData.

        Args:
            base_url (str): API base URL.
            rate_limit_delay (float): Minimum delay between requests in seconds.

        Raises:
            ValueError: If rate_limit_delay is negative.
        """
        if rate_limit_delay < 0:
            raise ValueError("Rate limit delay must be non-negative.")
        self._base_url = base_url
        self._rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0

    @property
    def base_url(self):
        return self._base_url

    def _rate_limit(self):
        """Ensure delay between API requests."""
        current_time = time.time()
        if current_time - self._last_request_time < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay)
        self._last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a safe, rate-limited API request with retries."""
        url = f"{self._base_url}/{endpoint}"
        for attempt in range(3):
            self._rate_limit()
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 429:
                    print("Rate limit reached; waiting 5 seconds...")
                    time.sleep(5)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        return {}

    def get_current_price(self, crypto_ids: List[str], vs_currency: str = "usd") -> Dict[str, float]:
        """Return current prices for multiple cryptocurrencies."""
        params = {"ids": ",".join(crypto_ids), "vs_currencies": vs_currency}
        data = self._make_request("simple/price", params)
        return {cid: info.get(vs_currency, 0) for cid, info in data.items()} if data else {}

    def __repr__(self):
        return f"PullData(base_url='{self._base_url}', rate_limit_delay={self._rate_limit_delay})"

    def __str__(self):
        return "PullData: CoinGecko API Connector"
class CryptoAsset:
    """Represents a cryptocurrency asset."""

    def __init__(self, crypto_id: str, name: str, symbol: str, current_price: float = 0.0):
        if not crypto_id.strip():
            raise ValueError("crypto_id cannot be empty.")
        if current_price < 0:
            raise ValueError("Price cannot be negative.")
        self._crypto_id = crypto_id
        self._name = name
        self._symbol = symbol
        self._current_price = current_price

    @property
    def crypto_id(self):
        return self._crypto_id

    @property
    def current_price(self):
        return self._current_price

    @current_price.setter
    def current_price(self, price: float):
        if price < 0:
            raise ValueError("Price must be non-negative.")
        self._current_price = price

    def __repr__(self):
        return f"CryptoAsset({self._crypto_id}, price={self._current_price:.2f})"

    def __str__(self):
        return f"{self._name} ({self._symbol.upper()}): ${self._current_price:.2f}"
from datetime import datetime

class Transaction:
    """Represents a single crypto buy or sell transaction."""

    def __init__(self, txn_type: str, crypto_id: str, amount: float, price: float, profit: float = 0.0):
        if txn_type not in ("BUY", "SELL"):
            raise ValueError("Transaction type must be 'BUY' or 'SELL'.")
        if amount <= 0 or price <= 0:
            raise ValueError("Amount and price must be positive.")
        self._txn_type = txn_type
        self._crypto_id = crypto_id
        self._amount = amount
        self._price = price
        self._profit = profit
        self._timestamp = datetime.now()

    @property
    def profit(self):
        return self._profit

    @property
    def crypto_id(self):
        return self._crypto_id

    def __repr__(self):
        return f"Transaction({self._txn_type}, {self._crypto_id}, amount={self._amount}, price={self._price})"

    def __str__(self):
        ts = self._timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if self._txn_type == "BUY":
            return f"[{ts}] BUY {self._amount} {self._crypto_id} @ ${self._price:.2f}"
        else:
            return f"[{ts}] SELL {self._amount} {self._crypto_id} @ ${self._price:.2f} (Profit: ${self._profit:.2f})"
from typing import Dict, List

class CryptoPortfolio:
    """Manage cryptocurrency holdings and transactions."""

    def __init__(self, data_puller: PullData):
        if not isinstance(data_puller, PullData):
            raise TypeError("data_puller must be an instance of PullData.")
        self._data_puller = data_puller
        self._holdings: Dict[str, Dict[str, float]] = {}
        self._transactions: List[Transaction] = []

    @property
    def holdings(self):
        return self._holdings

    def buy(self, asset: CryptoAsset, amount: float):
        """Buy a specified amount of a cryptocurrency."""
        prices = self._data_puller.get_current_price([asset.crypto_id])
        if asset.crypto_id not in prices:
            print("Error: Could not fetch price.")
            return
        price = prices[asset.crypto_id]
        asset.current_price = price

        if asset.crypto_id in self._holdings:
            prev = self._holdings[asset.crypto_id]
            total_value = prev['amount'] * prev['avg_buy_price'] + amount * price
            total_amount = prev['amount'] + amount
            prev['amount'] = total_amount
            prev['avg_buy_price'] = total_value / total_amount
        else:
            self._holdings[asset.crypto_id] = {'amount': amount, 'avg_buy_price': price}

        txn = Transaction("BUY", asset.crypto_id, amount, price)
        self._transactions.append(txn)
        print(txn)

    def sell(self, asset: CryptoAsset, amount: float):
        """Sell a specified amount of a cryptocurrency."""
        if asset.crypto_id not in self._holdings or self._holdings[asset.crypto_id]['amount'] < amount:
            print("Error: Insufficient holdings.")
            return

        prices = self._data_puller.get_current_price([asset.crypto_id])
        price = prices.get(asset.crypto_id, 0)
        cost_basis = amount * self._holdings[asset.crypto_id]['avg_buy_price']
        proceeds = amount * price
        profit = proceeds - cost_basis

        self._holdings[asset.crypto_id]['amount'] -= amount
        if self._holdings[asset.crypto_id]['amount'] == 0:
            del self._holdings[asset.crypto_id]

        txn = Transaction("SELL", asset.crypto_id, amount, price, profit)
        self._transactions.append(txn)
        print(txn)

    def portfolio_value(self):
        """Return and print total current portfolio value."""
        if not self._holdings:
            print("No holdings.")
            return 0.0

        ids = list(self._holdings.keys())
        prices = self._data_puller.get_current_price(ids)
        total = 0
        print("\nCurrent Portfolio Value:")
        for cid, info in self._holdings.items():
            amt = info['amount']
            price = prices.get(cid, 0)
            value = amt * price
            total += value
            print(f" - {cid:<10} {amt:.4f} @ ${price:.2f} = ${value:,.2f}")
        print(f"Total Value: ${total:,.2f}")
        return total

    def show_transactions(self):
        """Display transaction history."""
        if not self._transactions:
            print("No transactions yet.")
            return
        print("\nTransaction History:")
        for t in self._transactions:
            print(t)

    def __repr__(self):
        return f"CryptoPortfolio({len(self._holdings)} holdings)"

    def __str__(self):
        return f"Portfolio with {len(self._holdings)} assets"
class User:
    """Represents a user who owns a crypto portfolio."""

    def __init__(self, username: str):
        if not username.strip():
            raise ValueError("Username cannot be empty.")
        self._username = username
        self._portfolio: CryptoPortfolio | None = None

    def link_portfolio(self, portfolio: CryptoPortfolio):
        """Link a CryptoPortfolio to the user."""
        if not isinstance(portfolio, CryptoPortfolio):
            raise TypeError("Expected a CryptoPortfolio instance.")
        self._portfolio = portfolio

    def __str__(self):
        value = self._portfolio.portfolio_value() if self._portfolio else 0
        return f"User: {self._username} | Portfolio Value: ${value:,.2f}"

    def __repr__(self):
        return f"User({self._username})"
