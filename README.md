## INST326 Information Retrieval
# Crypto API Wallet and Data Display
This project intends to pull data from an API (CoinGecko) and then use it to display various data. Users will also have the ability to "buy" various cryptos and see how much their crypto wallet has increased or decreased in value

**Project handled by William, Linwood, Christopher, Bushra**

***
This project focuses on cryptocurrency data retrieval and portfolio management. It integrates market data from CoinGecko to provides users with an interactive interface to track crypto investments.
***

Users struggle to understand what crypto is and how or what cryptos to invest in.  

This project aims to solve that by integrating live market data with wallet management and visualization tools to simulate real circumstances.

***

## Installation and Setup Instructions

First, you must import the src package. This requires the following code

> import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

Then, from src, you can use the available methods, as noted in function_reference.md in docs.

### Here is an example import:

> from src import PullData, display_market_data, user_interaction, summarize_market_performance

## Function library overview and organization
The source code for this project is organized within the src/ directory

> library_name.py

Serves as the core function library, containing the primary logic for interacting with the CoinGecko API, managing user wallets, and calculating value changes

> utils.py

Houses auxiliary functions that support data formatting, error handling, and logging.
Typical utilities include:

> examples/demo_script.py

Demonstrates basic usage of the core library—fetching crypto data, performing mock transactions, and displaying wallet performance.

> docs/

Contains detailed documentation and references.

>> function_reference.md

Comprehensive overview of each available function, including parameters and return types.

>> usage_examples.md

Practical demonstrations and tutorials for integrating the library.

## Contribution guidelines for team members

William is in charge of pulling from an API

Linwood is in charge of display for interaction

Christopher is in charge of displaying charts

Bushra is in charge of the interaction with the wallet

***

**README Contributors:** William,