from alpaca.trading.client import TradingClient
from TradBot_Funcs import *                             # import all functions
import datetime, time

# Made By Andres Candido 2024.
# All Rigths Reserved.

#------------------------------ SETUP ------------------------------#

my_key = "PKYQD3XECSF0T2SHPVS0"
my_secret_key = "PJbDMuORm6ct0m2YxaxjHCgZsMmTdorCc6Oa1gMJ"

Trading_Client = TradingClient(my_key, my_secret_key, paper=True) # Log into Alpaca, set paper=false if trading with real money

symbol = ["PLTR"] 

TSO_Sell = 0.5 # TrailingStopOrder will sell assets if current price is (TSO_Sell)% lower than highest price reached
TSO_Buy = 0.75 # TrailingStopOrder will buy assets if current price is (TSO_Buy)% higher than lowest price reached

#If day trading stocks, account needs to have at least $25000 at all times. If not, Pattern Day Trader (PDT) Protection will restrict account.
#Allowance is the money available for trade, if there are multiple stocks in the symbol list allowance will be divided equally.
allowance = round(float(Trading_Client.get_account().buying_power) - 25000, 2)

#Initialize variable lists:
allowance = [round(allowance/len(symbol),2)] * len(symbol)
leftover_allowance = [0.0] * len(symbol)
Order_Is_Scheduled = [False] * len(symbol)
BuyOrSell = ["LookingToSell"] * len(symbol)
Buy_Order_id = [None] * len(symbol)
Sell_Order_id = [None] * len(symbol)


#------------------------------ MAIN LOOP ------------------------------#

#Loop forever?
while True:
    try:
        #Check calendar, if market does not open today sleep until next market open. Also sleep if market did open today but has already closed (we end our day 5 mins before closing time)
        if( (check_calendar(my_key, my_secret_key, datetime.date.today()) == False) or ( (check_calendar(my_key, my_secret_key, datetime.date.today()) == True) and (get_current_market_time(my_key, my_secret_key) >= (get_market_closing_time(my_key, my_secret_key)-datetime.timedelta(minutes=5))))):
            write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - Sleeping until market opens...")
            time.sleep(time_until_open(my_key, my_secret_key))

        else:
            write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - A new day begins!")

            for i in range(len(symbol)):
                #Execute first Buy (Market Order) of the day at market openning if ( (position isn't already held) OR (position is held but is less than 1 share) ) AND (a TSO_BUY order isn't already scheduled).
                if ( (check_position(Trading_Client,symbol[i]) == False or ( (check_position(Trading_Client,symbol[i]) == True and float(get_position_amount(Trading_Client,symbol[i])) < 1.00))) and (Order_Is_Scheduled[i] == False) ):
                    Buy_Order_id[i] = MarketOrder_buy_stock(Trading_Client, allowance[i], symbol[i])
                    current_price = request_stock_price(my_key, my_secret_key, symbol[i])
                    write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - 1st Buy: Bought " + get_position_amount(Trading_Client,symbol[i]) + " shares of " + symbol[i] + " each at $" + str(current_price) )
                else:
                    current_price = request_stock_price(my_key, my_secret_key, symbol[i])
                    write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - " + get_position_amount(Trading_Client,symbol[i]) + " shares of " + symbol[i] + " already in portfolio, current value per share: $" + str(current_price) )


            #This loop runs until 5 minutes before the market closes for the day
            while (get_current_market_time(my_key, my_secret_key) < (get_market_closing_time(my_key, my_secret_key)-datetime.timedelta(minutes=5))):

                #Go over all stocks in symbol list 
                for i in range(len(symbol)):

                    current_price = request_stock_price(my_key, my_secret_key, symbol[i])

                    if (BuyOrSell[i] == "LookingToSell"):

                        if (check_order_status(my_key, my_secret_key, Buy_Order_id[i]) == "filled" and Order_Is_Scheduled[i] == False):
                            # Schedule TrailingStopOrder to sell asset when Buy_Order is filled
                            # TrailingStopOrder will sell assets if current price is (TSO_Sell)% lower than highest price reached
                            Sell_Order_id[i] = TrailingStopOrder_sell_stock(Trading_Client, current_price, allowance[i], symbol[i], TSO_Sell)
                            # Update Scheduled_Sell_Order to prevent scheduling multiple orders 
                            Order_Is_Scheduled[i] = True

                        elif (check_order_status(my_key, my_secret_key, Sell_Order_id[i]) == "filled"): 
                            #If previous Sell has gone through write it to Log and update allowance amount
                            write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - Sold " + str(symbol[i]) + " at " + str(current_price) )
                            allowance[i] = update_allowance(my_key, my_secret_key, Sell_Order_id[i], leftover_allowance[i]) # Update allowance
                            
                            # Reset Scheduled_Sell_Order and update BuyOrSell to change behavior 
                            Order_Is_Scheduled[i] = False
                            BuyOrSell[i] = "LookingToBuy"
                        

                    elif (BuyOrSell[i] == "LookingToBuy"):

                        if (check_order_status(my_key, my_secret_key, Sell_Order_id[i]) == "filled" and Order_Is_Scheduled[i] == False):
                            # Schedule TrailingStopOrder to Buy asset when Sell_Order is filled
                            # TrailingStopOrder will buy assets if current price is (TSO_Buy)% higher than lowest price reached
                            Buy_Order_id[i] = TrailingStopOrder_buy_stock(Trading_Client, current_price, allowance[i], symbol[i], TSO_Buy)
                            # Update Scheduled_Buy_Order to prevent scheduling multiple orders 
                            Order_Is_Scheduled[i] = True

                        elif (check_order_status(my_key, my_secret_key, Buy_Order_id[i]) == "filled"):
                            #If previous Buy_Order has gone through write it to Log 
                            write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - Bought " + get_position_amount(Trading_Client,symbol[i]) + " shares of " + symbol[i] + " at " + str(current_price) )

                            #Get the amount of leftover allowance (allowance - money used in buy order), we will use this value in the update_allowance function 
                            leftover_allowance[i] = get_leftover(my_key, my_secret_key, Buy_Order_id[i], allowance[i])
                            print("Leftover allowance:" + leftover_allowance[i]) #testing
                            
                            # Reset Scheduled_Buy_Order and update BuyOrSell to change behavior 
                            Order_Is_Scheduled[i] = False
                            BuyOrSell[i] = "LookingToSell"

                time.sleep(60)  # Sleep for 1 minute(s) (60 seconds) then check if current TrailingStopOrder has gone through, repeat until market closes
                #print(allowance,Order_Is_Scheduled,BuyOrSell,Buy_Order_id,Sell_Order_id)

            #Send End Of Day Report to email
            write_to_log( str(get_current_market_time(my_key, my_secret_key)) + " - End of the day, sending report")
            End_of_Day_Report(Trading_Client, "tradbot001@gmail.com", "lyrebwuypwlwzzvu", "andrescandido2000@gmail.com")

    except requests.ConnectionError as e:
        if ( check_internet_connection()==False ):
            write_to_log("ERROR: -------------> Internet connection lost. Waiting to reboot...")
        else:
            write_to_log(f"ERROR: -------------> Internet connection OK, something else went wrong. Retrying...\nError message: {e}")
        
        time.sleep(60)  # Sleep for 1 minute(s) (60 seconds) then check internet connection again
 