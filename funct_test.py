from alpaca.trading.client import TradingClient
from TradBot_Funcs import *
import datetime

my_key = "PKX9BESW83A25ZKN8E0G"
my_secret_key = "gevvhYGI71oQd6W7mZ1QKoUU9dVL57CCQdsdPQ82"

symbol = "PLTR"

Trading_Client = TradingClient(my_key, my_secret_key, paper=True) ## Log into Alpaca


#TradingClient.cancel_orders(self=Trading_Client)

#TradingClient.close_all_positions(self=Trading_Client) #Sell all assets

#clear_log()

if (check_position(Trading_Client,symbol) == False or (check_position(Trading_Client,symbol) == True and float(get_position_amount(Trading_Client,symbol)) < 1.00)):
    print(get_position_amount(Trading_Client,symbol))
else:
    print("peener")

print(check_position(Trading_Client,symbol))

print(get_position_amount(Trading_Client,symbol))

print(check_internet_connection())

#End_of_Day_Report(Trading_Client, "tradbot001@gmail.com", "lyrebwuypwlwzzvu", "andrescandido2000@gmail.com")

#print(update_allowance(my_key, my_secret_key, "ef983233-9430-4768-b732-4f7f9e8a7054"))

#print(time_until_open(my_key, my_secret_key))

#request_crypto_price(my_key, my_secret_key, symbol)

#print(Trading_Client.get_account().account_number)

#print(current_balance(Trading_Client))

#current_price = request_stock_price(my_key, my_secret_key, symbol)

#print(time_until_open(my_key, my_secret_key))

#print(get_current_market_time(my_key, my_secret_key)) #Current time of US stock market (timezone = Eastern Time)

#time.sleep(300)  # Sleep for 5 minutes (300 seconds)
#time_until_open(my_key, my_secret_key)