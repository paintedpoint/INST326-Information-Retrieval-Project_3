import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src import PullData, CryptoPortfolio, display_market_data, user_interaction, summarize_market_performance

def main():
    """
    Run the interactive crypto tracker demo.
    Work by Linwood
    """
    print("=" * 60)
    print("CRYPTO PRICE TRACKER (API + USER INTERACTION)")
    print("=" * 60)

    data_puller = PullData()
    market_data = data_puller.get_market_data()

    if market_data.empty:
        print("⚠️  Failed to retrieve market data. Please try again later.")
        return

    # Start interactive menu (lets user pick what to do)
    user_interaction(market_data)

    # Optional: Also run the basic data display afterward
    print("\nFinal Summary (Top Gainers & Losers):")
    summarize_market_performance(market_data)

dataPuller = PullData()
print("=" * 60)
print("Testing Crypto Data Manager")
print("=" * 60)

# Get market data and display with color-coded arrows
print("\nGetting top 10 cryptocurrencies by market cap...")
market_data = dataPuller.get_market_data()
display_market_data(market_data)

# Get crypto details
print("\nGetting Bitcoin details...")
btc_details = dataPuller.get_crypto_details('bitcoin')
print(f"Name: {btc_details['name']}")
print(f"Price: ${btc_details['current_price']:,.2f}")
print(f"Description: {btc_details['description'][:200]}...")

# Get historical data
print("\nGetting 7-day historical data for Bitcoin...")
eth_history = dataPuller.get_historical_data('bitcoin', days=7)
print(eth_history.tail())

# Opens a menu where users can select between viewing top gainer/loser or top 10 cryptos
if __name__ == "__main__":
    main()

print("=" * 60)
print(" CRYPTO PORTFOLIO MANAGER ")
print("=" * 60)

data_puller = PullData()
portfolio = CryptoPortfolio(data_puller)
prices = data_puller.get_current_price(["bitcoin", "ethereum"])

# Example buys
portfolio.buy("bitcoin", 0.001)
portfolio.buy("ethereum", 0.02)

# Example sell
portfolio.sell("bitcoin", 0.0005)

# Portfolio summary
portfolio.portfolio_value()
portfolio.show_transactions()