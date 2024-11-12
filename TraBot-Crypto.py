from alpaca.trading.client import TradingClient
from TradBot_Funcs import *                             # import all functions
import datetime, time

my_key = "PKF13X4OWDESMYO15RG0"
my_secret_key = "SmGfsnjSlX9RhnQCFmqPn8Id3fw4K84mpWo09GRD"

Trading_Client = TradingClient(my_key, my_secret_key, paper=True) ## Log into Alpaca

symbol = "BTC/USD"
allowance = Trading_Client.get_account().buying_power


#Execute first Buy of the day at market openning
print("A new day begins!")
buy_crypto(Trading_Client, allowance, symbol)
HighestOrLowest_price = request_crypto_price(my_key, my_secret_key, symbol)

BuyOrSell = "Sell"

#This loop runs forever
while True:

    current_price = request_crypto_price(my_key, my_secret_key, symbol)

    if (BuyOrSell == "Sell"):

        if (current_price > HighestOrLowest_price):
            HighestOrLowest_price = current_price #Update new highest price
                
        elif (current_price <= (HighestOrLowest_price-(HighestOrLowest_price*0.003))): 
            #Sell if current price is 0.3% less than highest price reached
            TradingClient.close_all_positions(self=Trading_Client) #Sell all assets

            BuyOrSell = "Buy"
            HighestOrLowest_price = current_price #Store price at selling time
            
    elif (BuyOrSell == "Buy"):

        if (current_price < HighestOrLowest_price):
            HighestOrLowest_price = current_price #Update new lowest price

        elif (current_price >= (HighestOrLowest_price+(HighestOrLowest_price*0.003))):
            #Buy if current price is 0.3% more than lowest price reached
            allowance = round(float(Trading_Client.get_account().buying_power) - 25000, 2)
            buy_crypto(Trading_Client, allowance, symbol)

            BuyOrSell = "Sell"
            HighestOrLowest_price = current_price #Store price at selling time

    time.sleep(60)  # Sleep for 1 minute(s) (60 seconds) then check price again

    #Check if it's 6 pm to send the end-of-day report
    current_time = datetime.datetime.now()
    if current_time.hour == 18 and current_time.minute == 0:
        #Send End Of Day Report to email
        End_of_Day_Report(Trading_Client, "tradbot001@gmail.com", "lyrebwuypwlwzzvu", "andrescandido2000@gmail.com")
        print("End of the day report sent.")