import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src import PullData, Transaction, Buy, Sell, Portfolio, MarketData, Portfolio_Helper, Price_Charts_Graphs, CryptoMarketDisplay


dataPuller = PullData()
display = CryptoMarketDisplay(dataPuller.get_market_data())
market = MarketData()

choice = int(input("How much funds do you have?\n"))
portfo = Portfolio(choice)

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
        while(True):
            choice = input("What crypto do you want to buy? 1) Nevermind\n")
            if choice == "1":
                break
            choice2 = int(input("How much crypto do you want to buy?"))
            if choice2 <= 0:
                print("Not Valid, Try again")
                continue
            try:
                purchase = Buy(choice, dataPuller, choice2)
                portfo.makeTransaction(purchase)
                break
            except:
                print("I didn't understand what you wanted. Please try again")
        print("Purchased!")
    elif choice == "4":
        while(True):
            choice = input("What crypto do you want to sell? 1) Nevermind\n")
            if choice == "1":
                break
            choice2 = int(input("How much crypto do you want to sell?"))
            if choice2 <= 0:
                print("Not Valid, Try again")
                continue
            try:
                purchase = Sell(choice, dataPuller, choice2)
                portfo.makeTransaction(purchase)
                break
            except:
                print("I didn't understand what you wanted. Please try again")

        print("Sold!")
    elif choice == "5":
        portfo.seePortfolioValue()
        portfo.seePastTransactions()
    elif choice == "6":
        break
    else:
        print("I didn't understand that...")
print("BYE!")
