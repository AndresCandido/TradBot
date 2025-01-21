import requests
import datetime
from alpaca.trading.requests import MarketOrderRequest, TrailingStopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def current_balance(Trading_Client):
    # Get our account information.
    account = Trading_Client.get_account()
    Balance_Report = "Portfolio balance: $" + account.buying_power

    Balance_Report = Balance_Report + "\nTotal portfolio equity: $" + account.equity

    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    percent_change = round(((float(account.equity) - float(account.last_equity)) * 100) / float(account.last_equity), 2)
    Balance_Report = Balance_Report + f'\nToday\'s Total portfolio equity change: ${balance_change} ({percent_change}%)'

    # Check our effective balance (current balance -$25000) and our effective percent change
    effective_balance = round((float(account.equity) - 25000), 2)
    effective_percent_change = round( ( ((float(account.equity) - 25000) - (float(account.last_equity) - 25000)) * 100) / (float(account.last_equity) - 25000), 2)
    Balance_Report = Balance_Report + f'\nToday\'s allowance and effective equity change: ${effective_balance} ({effective_percent_change}%)'

    #print(Balance_Report)
    return(Balance_Report)

def request_stock_price(my_key, my_secret_key, symbol):
    url = "https://data.alpaca.markets/v2/stocks/bars/latest?symbols=" + symbol + "&feed=iex"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": my_key,
        "APCA-API-SECRET-KEY": my_secret_key
    }

    response = requests.get(url, headers=headers)
    #print(response.text)

    # Extract current stock price from request
    request = response.text
    sub1 = '{"c":'
    sub2 = ',"h":'
    
    # getting index of substrings
    idx1 = request.find(sub1)
    idx2 = request.find(sub2)
    
    # length of substring 1 is added to
    # get string from next character
    current_price = request[idx1 + len(sub1): idx2]
    
    # printing result
    print(symbol + " current price: " + current_price)
    return(float(current_price))

def request_crypto_price(my_key, my_secret_key, symbol):
    url = f"https://data.alpaca.markets/v1beta3/crypto/us/latest/orderbooks?symbols={symbol}"
    headers = {
        'APCA-API-KEY-ID': my_key,
        'APCA-API-SECRET-KEY': my_secret_key
    }
    
    response = requests.get(url, headers=headers)

    data = response.json()
    #print(data)
    best_ask_price = data['orderbooks'][symbol]['a'][0]['p']  # Lowest ask price
    best_bid_price = data['orderbooks'][symbol]['b'][0]['p']  # Highest bid price
            
    # Calculate mid-market price
    mid_market_price = (best_ask_price + best_bid_price) / 2
    print("midpoint value: " + str(mid_market_price))
    return(mid_market_price)

def check_position(Trading_Client, symbol):
    try:
        position = Trading_Client.get_open_position(symbol)
    except:
        return False
         
    return True

def get_position_amount(Trading_Client, symbol):
    portfolio = Trading_Client.get_all_positions()
    position = Trading_Client.get_open_position(symbol)
    found = False

    #print(portfolio)
    #print(position)

    for position in portfolio:
        if (position.symbol == symbol):
            found = True
            amount = position.qty

    if(found == True):
        return amount
    else:
        return "Position not found"       

def MarketOrder_buy_stock(Trading_Client, notional_amount, symbol):
    
    market_order_data = MarketOrderRequest(
        symbol = symbol,
        notional = notional_amount,
        side = OrderSide.BUY,
        time_in_force = TimeInForce.DAY
    )

    market_order = Trading_Client.submit_order(market_order_data)
    return(market_order.id)

def TrailingStopOrder_buy_stock(Trading_Client, current_price, notional_amount, symbol, percent):

    qty_amount = notional_amount // current_price #The // operator performs floor division, which rounds down the result to the nearest integer.

    TS_order_data = TrailingStopOrderRequest(
        symbol = symbol,
        qty = qty_amount,
        side = OrderSide.BUY,
        time_in_force = TimeInForce.GTC,
        trail_percent = percent
    )

    TS_order = Trading_Client.submit_order(TS_order_data)
    return(TS_order.id)

def TrailingStopOrder_sell_stock(Trading_Client, current_price, notional_amount, symbol, percent):

    #qty_amount = notional_amount // current_price # alternative qty_amount operation if we do not want to sell all
    qty_amount = float(get_position_amount(Trading_Client,symbol)) // 1 #The // operator performs floor division, which rounds down the result to the nearest integer.

    TS_order_data = TrailingStopOrderRequest(
        symbol = symbol,
        qty = qty_amount,
        side = OrderSide.SELL,
        time_in_force = TimeInForce.GTC,
        trail_percent = percent
    )

    TS_order = Trading_Client.submit_order(TS_order_data)
    return(TS_order.id)

def check_order_status(my_key, my_secret_key, order_id):
    url = "https://paper-api.alpaca.markets/v2/orders/" + str(order_id)

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": my_key,
        "APCA-API-SECRET-KEY": my_secret_key
    }

    response = requests.get(url, headers=headers)
    response = response.text

    # Find the "status" key and extract its value
    start_index = response.find('"status":') + len('"status":')
    end_index = response.find(',', start_index)

    # Strip unwanted characters like quotes and whitespace
    status = response[start_index:end_index].strip().strip('"')

    return(status)

def get_leftover(my_key, my_secret_key, order_id, allowance):
    url = "https://paper-api.alpaca.markets/v2/orders/" + str(order_id)

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": my_key,
        "APCA-API-SECRET-KEY": my_secret_key
    }

    response = requests.get(url, headers=headers)
    response = response.text

    # Find the "filled_qty" and "filled_avg_price" key and extract their values
    qty_start_index = response.find('"filled_qty":') + len('"filled_qty":')
    qty_end_index = response.find(',', qty_start_index)

    price_start_index = response.find('"filled_avg_price":') + len('"filled_avg_price":')
    price_end_index = response.find(',', price_start_index)

    # Strip unwanted characters like quotes and whitespace
    qty = float(response[qty_start_index:qty_end_index].strip().strip('"'))
    price = float(response[price_start_index:price_end_index].strip().strip('"'))

    return(allowance - round(qty * price,2))



def update_allowance(my_key, my_secret_key, order_id, leftover_allowance):
    url = "https://paper-api.alpaca.markets/v2/orders/" + str(order_id)

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": my_key,
        "APCA-API-SECRET-KEY": my_secret_key
    }

    response = requests.get(url, headers=headers)
    response = response.text

    # Find the "filled_qty" and "filled_avg_price" key and extract their values
    qty_start_index = response.find('"filled_qty":') + len('"filled_qty":')
    qty_end_index = response.find(',', qty_start_index)

    price_start_index = response.find('"filled_avg_price":') + len('"filled_avg_price":')
    price_end_index = response.find(',', price_start_index)

    # Strip unwanted characters like quotes and whitespace
    qty = float(response[qty_start_index:qty_end_index].strip().strip('"'))
    price = float(response[price_start_index:price_end_index].strip().strip('"'))

    #Add lasts order's total value to the leftover allowance to get new allowance amount
    return(leftover_allowance + round(qty * price,2))
    
def buy_crypto(Trading_Client, amount, symbol):
    
    market_order_data = MarketOrderRequest(
        symbol = symbol,
        notional = amount,
        side = OrderSide.BUY,
        time_in_force = TimeInForce.GTC
    )

    market_order = Trading_Client.submit_order(market_order_data)
    #print(market_order)

def check_calendar(my_key, my_secret_key, date):
    date = str(date)
    date = date.replace("-", "")  # remove "-" from date

    url = "https://paper-api.alpaca.markets/v2/calendar?start=" + date + "&end=" + date

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": my_key,
        "APCA-API-SECRET-KEY": my_secret_key
    }

    response = requests.get(url, headers=headers)

    #print(response.text)

    if (response.text == "[]"): is_open = False # Market's closed
    else: is_open = True 

    return(is_open)

def check_clock(my_key, my_secret_key):
    url = "https://paper-api.alpaca.markets/v2/clock"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": my_key,
        "APCA-API-SECRET-KEY": my_secret_key
    }

    response = requests.get(url, headers=headers)

    #print(response.text)
    return(response.text)

def time_until_open(my_key, my_secret_key):
    clock = check_clock(my_key, my_secret_key)

    # Extract current time and openning time from clock
    sub1 = '{"timestamp":"'
    sub2 = '",is_open":'

    sub3 = '"next_open":"'
    sub4 = '","next_close":'


    # getting index of substrings
    idx1 = clock.find(sub1)
    idx2 = clock.find(sub2)

    idx3 = clock.find(sub3)
    idx4 = clock.find(sub4)

    # length of substring 1 is added to
    # get string from next character
    current_time = clock[idx1 + len(sub1): idx2] 

    current_date = current_time[0:10]
    current_time = current_time[11:19]

    #print(current_date)
    #print(current_time)

    openning_time = clock[idx3 + len(sub3): idx4] 

    openning_date = openning_time[0:10]
    openning_time = openning_time[11:19]

    #print(openning_date)
    #print(openning_time)

    format_date = '%Y-%m-%d'
    current_date = datetime.datetime.strptime(current_date, format_date)
    openning_date = datetime.datetime.strptime(openning_date, format_date)

    format_time = '%H:%M:%S'
    current_time = datetime.datetime.strptime(current_time, format_time)
    openning_time = datetime.datetime.strptime(openning_time, format_time)

    current_hours = current_time.hour
    current_minutes = current_time.minute
    current_seconds = current_time.second
    current_time = current_hours * 3600 + current_minutes * 60 + current_seconds

    openning_hours = openning_time.hour
    openning_minutes = openning_time.minute
    openning_seconds = openning_time.second
    openning_time = openning_hours * 3600 + openning_minutes * 60 + openning_seconds

    time_until_open = (((openning_date - current_date).days * 24 * 60 * 60) - current_time) + openning_time

    #print(time_until_open)
    return(time_until_open)

def get_current_market_time(my_key, my_secret_key):
    clock = check_clock(my_key, my_secret_key)

    # Extract current time from clock
    sub1 = '{"timestamp":"'
    sub2 = '",is_open":'  

    # getting index of substrings
    idx1 = clock.find(sub1)
    idx2 = clock.find(sub2)

    current_time = clock[idx1 + len(sub1): idx2] 
    current_time = current_time[0:19]
    #print(current_time)

    current_time = datetime.datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%S")
    #print(current_time)
    
    return (current_time)

def get_market_closing_time(my_key, my_secret_key):
    clock = check_clock(my_key, my_secret_key)

    # Extract current time from clock
    sub1 = ',"next_close":"' 

    # getting index of substrings
    idx1 = clock.find(sub1)

    closing_time = clock[idx1 + len(sub1):] 
    closing_time = closing_time[0:19]
    #print(closing_time)

    closing_time = datetime.datetime.strptime(closing_time, "%Y-%m-%dT%H:%M:%S")
    #print(closing_time)
    
    return (closing_time)

def check_internet_connection():
    try:
        # Attempt to reach Google with a simple GET request
        requests.get("http://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def write_to_log(entry):
    with open("Today'sLog.txt", "a") as file:  # Open in append mode
        file.write(entry + "\n")  # Write the string with a newline
        print(entry)

def clear_log():
    with open("Today'sLog.txt", "w") as file:  # Open in write mode
        file.truncate(0)  # Clear the file contents

def End_of_Day_Report(Trading_Client, from_email, from_password, to_email):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "End of Day Report " + str(datetime.date.today()) #subject
    
    # Attach the email body
    msg.attach(MIMEText(current_balance(Trading_Client), 'plain'))

    # Attach "Today'sLog.txt" file
    filename = "Today'sLog.txt"
    with open(filename, "rb") as attachment:
        # Directly use MIMEApplication to handle the attachment
        part = MIMEApplication(attachment.read(), Name=filename)
    part['Content-Disposition'] = f'attachment; filename="{filename}"'
    msg.attach(part)

    try:
        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # For Gmail SMTP
        server.starttls()  # Secure the connection

        # Login to the email account
        server.login(from_email, from_password) # Password for email server = lyrebwuypwlwzzvu

        # Send the email
        server.send_message(msg)
        write_to_log("Email sent successfully!")

        # Clear the Log text file
        clear_log()
        
    except Exception as e:
        write_to_log(f"ERROR: -------------> Failed to send email: {e}")
        
    finally:
        # Terminate the SMTP session and close the connection
        server.quit()