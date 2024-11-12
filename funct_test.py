from alpaca.trading.client import TradingClient
from TradBot_Funcs import *
import datetime

my_key = "PK6C08KRDG5YWQ1ZMCA3"
my_secret_key = "rWfq0uedd1kB5vrFmbB2mCCQ9GMeoA4JYSDYbamX"

symbol = "NVDA"

Trading_Client = TradingClient(my_key, my_secret_key, paper=True) ## Log into Alpaca

#End_of_Day_Report(Trading_Client, "tradbot001@gmail.com", "lyrebwuypwlwzzvu", "andrescandido2000@gmail.com")

#TradingClient.close_all_positions(self=Trading_Client) #Sell all assets

#print(str(get_current_market_time(my_key, my_secret_key)) + " - 1st Buy: Bought " + get_position_amount(Trading_Client,symbol) + " at 100" )

print(check_internet_connection())

#print(time_until_open(my_key, my_secret_key))

#request_crypto_price(my_key, my_secret_key, symbol)

#print(Trading_Client.get_account().account_number)

print(current_balance(Trading_Client))

#current_price = request_stock_price(my_key, my_secret_key, symbol)

#buy_stock(Trading_Client, moneys, symbol)

#TradingClient.close_all_positions(self=Trading_Client) #Sell all assets

#print(time_until_open(my_key, my_secret_key))

#print(get_current_market_time(my_key, my_secret_key)) #Current time of US stock market (timezone = Eastern Time)

#time.sleep(300)  # Sleep for 5 minutes (300 seconds)
#time_until_open(my_key, my_secret_key)