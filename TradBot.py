from alpaca.trading.client import TradingClient
from TradBot_Funcs import *                             # import all functions
import datetime, time

# Made By Andres Candido 2024.
# All Rigths Reserved.

my_key = "PK6C08KRDG5YWQ1ZMCA3"
my_secret_key = "rWfq0uedd1kB5vrFmbB2mCCQ9GMeoA4JYSDYbamX"

Trading_Client = TradingClient(my_key, my_secret_key, paper=True) ## Log into Alpaca

symbol = "NVDA"
#If day trading stocks, account needs to have at least $25000 at all times. If not, Pattern Day Trader (PDT) Protection will restrict account
allowance = round(float(Trading_Client.get_account().buying_power) - 25000, 2)


#Loop forever?
while True:
    try:
        #Check calendar, if market does not open today sleep until next market open. Also sleep if market did open today but has already closed (we end our day 5 mins before closing time)
        if( (check_calendar(my_key, my_secret_key, datetime.date.today()) == False) or ( (check_calendar(my_key, my_secret_key, datetime.date.today()) == True) and (get_current_market_time(my_key, my_secret_key) >= (get_market_closing_time(my_key, my_secret_key)-datetime.timedelta(minutes=5))))):
            write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - Sleeping until market opens...")
            time.sleep(time_until_open(my_key, my_secret_key))

        else:
            write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - A new day begins!")

            #Execute first Buy of the day at market openning if position not already held
            if (check_position(Trading_Client,symbol) == False):
                buy_stock(Trading_Client, allowance, symbol)
                HighestOrLowest_price = request_stock_price(my_key, my_secret_key, symbol)
                openning_price = HighestOrLowest_price
                write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - 1st Buy: Bought " + get_position_amount(Trading_Client,symbol) + " at " + str(HighestOrLowest_price) )
            else:
                HighestOrLowest_price = request_stock_price(my_key, my_secret_key, symbol)
                openning_price = HighestOrLowest_price
                write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - " + get_position_amount(Trading_Client,symbol) + " already in portfolio, current value per share: " + str(HighestOrLowest_price) )

            BuyOrSell = "LookingToSell"


            #This loop runs until 5 minutes before the market closes for the day
            while (get_current_market_time(my_key, my_secret_key) < (get_market_closing_time(my_key, my_secret_key)-datetime.timedelta(minutes=5))):

                current_price = request_stock_price(my_key, my_secret_key, symbol)

                if (BuyOrSell == "LookingToSell"):

                    if (current_price > HighestOrLowest_price):
                        HighestOrLowest_price = current_price #Update new highest price
                        
                    elif (current_price <= (HighestOrLowest_price-(openning_price*0.002))): 
                        #Sell if current price is 0.2% less than highest price reached
                        TradingClient.close_all_positions(self=Trading_Client) #Sell all assets
                        write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - Sold all " + str(symbol) + " at " + str(current_price) )
                        allowance = round(float(Trading_Client.get_account().buying_power) - 25000, 2) #Update allowance for snowball potential

                        BuyOrSell = "LookingToBuy"
                        HighestOrLowest_price = current_price #Store price at selling time
                    
                elif (BuyOrSell == "LookingToBuy"):

                    if (current_price < HighestOrLowest_price):
                        HighestOrLowest_price = current_price #Update new lowest price

                    elif (current_price >= (HighestOrLowest_price+(openning_price*0.002))):
                        #Buy if current price is 0.2% more than lowest price reached
                        buy_stock(Trading_Client, allowance, symbol)
                        write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - Bought " + get_position_amount(Trading_Client,symbol) + " at " + str(current_price) )

                        BuyOrSell = "LookingToSell"
                        HighestOrLowest_price = current_price #Store price at selling time

                time.sleep(60)  # Sleep for 1 minute(s) (60 seconds) then check price again, repeat until market closes

            #Send End Of Day Report to email
            write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - End of the day, sending report")
            End_of_Day_Report(Trading_Client, "tradbot001@gmail.com", "lyrebwuypwlwzzvu", "andrescandido2000@gmail.com")

    except requests.ConnectionError as e:
        if ( check_internet_connection()==False ):
            write_to_log("ERROR: -------------> Internet connection lost. Retrying...")
        else:
            write_to_log(f"ERROR: -------------> Internet connection OK, something else went wrong. Retrying...\nError message: {e}")
        
        time.sleep(60)  # Sleep for 1 minute(s) (60 seconds) then check internet connection again
 