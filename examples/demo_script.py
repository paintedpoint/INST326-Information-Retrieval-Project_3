import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src import PullData, CryptoPortfolio, CryptoAsset, Transaction, User, MarketData, Portfolio_Helper, Price_Charts_Graphs, CryptoMarketDisplay


dataPuller = PullData()
display = CryptoMarketDisplay(dataPuller.get_market_data())
market = MarketData()
# user = User("Test_User")

display.menu()

while(True):
    choice = input(
"""
What do you want to do?
1) View Charts
2) View Table
3) Buy Crypto
4) Sell Crypto
5) View Portfolio
6) Exit
"""
    )
    if choice == "1":
        if market.fetch_data(limit=50):
            charts = Price_Charts_Graphs()

            choice = input(
"""
Which Chart do you want?
1) Price Chart
2) 24h Change Chart
3) Nevermind
"""
)
            while(True):
                if choice == "1":
                    print("\n * Generating Price Chart...")
                    charts.create_price_chart(market, top_n=15)  # Pass market object, not data
                elif choice == "2":
                    print("\n * Generating 24h Change Chart...")
                    charts.create_changing_chart(market, top_n=15)  # Correct method name
                elif choice == "3":
                    break
                else:
                    print("I didn't understand that.")
    elif choice == "2":
        display.display_market_data()
    elif choice == "3":
        print('unfinished')
    elif choice == "4":
        print('unfinished')
    elif choice == "5":
        print('unfinished')


    elif choice == "6":
        break
    else:
        print("I didn't understand that...")
print("BYE!")

# print("="*70)
# print("CRYPTO CHARTS DEMO")
# print("="*70)

# # Works!



# print("=" * 60)
# print("Testing Crypto Data Manager")
# print("=" * 60)

# # Get market data and display with color-coded arrows
# print("\nGetting top 10 cryptocurrencies by market cap...")
# market_data = dataPuller.get_market_data()
# marketDisplay.display_market_data(market_data)

# # Get crypto details
# print("\nGetting Bitcoin details...")
# btc_details = dataPuller.get_crypto_details('bitcoin')
# print(f"Name: {btc_details['name']}")
# print(f"Price: ${btc_details['current_price']:,.2f}")
# print(f"Description: {btc_details['description'][:200]}...")

# # Get historical data
# print("\nGetting 7-day historical data for Bitcoin...")
# eth_history = dataPuller.get_historical_data('bitcoin', days=7)
# print(eth_history.tail())

# # Opens a menu where users can select between viewing top gainer/loser or top 10 cryptos
# print("=" * 60)
# print("CRYPTO PRICE TRACKER (API + USER INTERACTION)")
# print("=" * 60)

# data_puller = PullData()
# market_data = data_puller.get_market_data()

# if market_data.empty:
#     print("⚠️  Failed to retrieve market data. Please try again later.")
# else:
#     # Start interactive menu (lets user pick what to do)
#     user_interaction(market_data)

#     # Optional: Also run the basic data display afterward
#     print("\nFinal Summary (Top Gainers & Losers):")
#     summarize_market_performance(market_data)

# print("=" * 60)
# print(" CRYPTO PORTFOLIO MANAGER ")
# print("=" * 60)

# data_puller = PullData()
# portfolio = CryptoPortfolio(data_puller)
# prices = data_puller.get_current_price(["bitcoin", "ethereum"])

# # Example buys
# portfolio.buy("bitcoin", 0.001)
# portfolio.buy("ethereum", 0.02)

# # Example sell
# portfolio.sell("bitcoin", 0.0005)

# # Portfolio summary
# portfolio.portfolio_value()
# portfolio.show_transactions()

