# TradBot

TradBot is an automated stock trading bot designed for the Alpaca Trading API. It enables hands-off management of stock trades, executing buy and sell orders based on configurable strategies and market conditions. Written in Python, TradBot is suitable for both paper trading and live accounts in the New York Stock Exchange (NYSE).

## Features

- **Automated Buy/Sell Decisions:** Monitors specified stocks and places orders according to user-defined parameters.
- **Trailing Stop Orders:** Schedules trailing stop orders to maximize gains and minimize losses, both when buying and selling.
- **Market Session Awareness:** Trades only during active market hours and sleeps when the market is closed or near closing.
- **Allowance Management:** Calculates and manages available funds, ensuring compliance with Pattern Day Trader (PDT) rules.
- **Logging & Reports:** Keeps a detailed log of all trades and sends end-of-day reports via email.
- **Robust Error Handling:** Handles internet connectivity issues and unexpected errors gracefully.
- **Modular Functions:** All trading and utility functions are modularized for easy maintenance and extension.

## How It Works

1. **Setup:** Configure your Alpaca API credentials and specify the stocks to monitor.
2. **Trading Loop:** The bot checks if the market is open and, if so, runs its trading loop:
    - Places buy orders if no position is held (or if position < 1 share).
    - Schedules trailing stop sell orders after a buy is filled.
    - Schedules trailing stop buy orders after a sell is filled.
    - Updates and logs all activity in real time.
3. **End of Day:** Sells all positions and cancels open orders 15 minutes before market close. Sends a summary report.
4. **Error Recovery:** If a connection error occurs, the bot waits and retries automatically.

## Disclaimer

This project is for educational purposes. Use at your own risk. Ensure you understand the risks of algorithmic trading and comply with all legal and brokerage requirements.

---

Made by Andres Candido, 2024. All rights reserved.
