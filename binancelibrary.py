import hmac
import math
import time
import hashlib
from decimal import Decimal
import requests
import json
from urllib.parse import urlencode
import sys
import traceback
from configparser import ConfigParser
import datetime
from binance.client import Client
from binance.helpers import  round_step_size

file = "config.ini"
config = ConfigParser()
config.read(file)

if int(config['appstate']['state']) == 0:
    client = Client(str(config['appstate']['testapikey']), str(config['appstate']['testsecretkey']))
    SECRET = str(config['appstate']['testsecretkey'])
    KEY = str(config['appstate']['testapikey'])
else:
    client = Client(str(config['appstate']['apikey']), str(config['appstate']['secretkey']))
    SECRET = str(config['appstate']['secretkey'])
    KEY = str(config['appstate']['apikey'])

today = datetime.date.today()

''' ======  begin of functions, you don't need to touch ====== '''
def hashing(query_string):

    return hmac.new(SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def get_timestamp():
    return int(time.time() * 1000)

def dispatch_request(http_method):

    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json;charset=utf-8',
        'X-MBX-APIKEY': KEY
    })
    return {
        'GET': session.get,
        'DELETE': session.delete,
        'PUT': session.put,
        'POST': session.post,
    }.get(http_method, 'GET')

# used for sending request requires the signature
def send_signed_request(http_method, url_path, payload={}):

    if int(config['appstate']['state']) == 0:
        BASE_URL = 'https://testnet.binance.vision'  # testnet base url
    else:
        BASE_URL = 'https://api.binance.com'  # real url

    query_string = urlencode(payload)
    # replace single quote to double quote
    query_string = query_string.replace('%27', '%22')
    if query_string:
        query_string = "{}&timestamp={}".format(query_string, get_timestamp())
    else:
        query_string = 'timestamp={}'.format(get_timestamp())

    url = BASE_URL + url_path + '?' + query_string + '&signature=' + hashing(query_string)

    params = {'url': url, 'params': {}}
    response = dispatch_request(http_method)(**params)
    return response.json()

# used for sending public data request
def send_public_request(url_path, payload={}):

    if int(config['appstate']['state']) == 0:
        BASE_URL = 'https://testnet.binance.vision'  # testnet base url
    else:
        BASE_URL = 'https://api.binance.com'  # real url

    query_string = urlencode(payload, True)
    url = BASE_URL + url_path
    if query_string:
        url = url + '?' + query_string

    response = dispatch_request('GET')(url=url)
    return response.json()

def getprice():
    try:
        if str(config['appstate']['symbol']):

            params = {
                "symbol": str(config['appstate']['symbol'].replace("/", "")),
            }

            response = send_public_request("/api/v3/ticker/price", params)

            if "price" in response:
                return float(response["price"])
            elif "code" in response:
                            print(f"Error: Cannot get price...: {response['code']}, {response}. Exiting program")

                            sys.exit()
    except Exception as e:
        print("Cannot get instrument price. please fill the symbol label: {0}".format(e))
        traceback.print_exc()
        sys.exit()

def createorder(condition=None, modquantity=None):

    try:
        if condition == "buy":

            print("buying instrument")

            params = {
                "symbol": str(config['appstate']['symbol'].replace("/", "")),
                "side": "BUY",
                "type": "MARKET",
                "quantity":  getquantity(modquantity),

            }

            response = send_signed_request('POST', '/api/v3/order', params)

            time.sleep(1)

            print(response)

            if "code" in response:
                print(f"buy order error: {response}. Exiting program")
                return False

            if "status" in response:
                if response["status"] == "FILLED":
                    print(f"Order bought for: {str(config['appstate']['symbol'])}, Price: {response['price']}, Quantity: {response['executedQty']}")

        elif condition == "sell":

            print("selling instrument")

            params = {
                "symbol": str(config['appstate']['symbol'].replace("/", "")),
                "side": "SELL",
                "type": "MARKET",
                "quantity": getquantity(modquantity),

            }

            response = send_signed_request('POST', '/api/v3/order', params)

            time.sleep(1)

            if "code" in response:
                print(f"sell order error: {response}. Exiting program")
                return False

            if "status" in response:
                if response["status"] == "FILLED":

                    print(f"Order sold for: {str(config['appstate']['symbol'])}, Price: {response['price']}, Quantity: {response['executedQty']}")

                elif response["status"] == "EXPIRED":
                    print("Currency has no liquidity. you should check the open orders manually to sell")
                    return False

    except Exception as e:
        print("Cannot place order")

def getlatestprice():
    prices = client.get_all_tickers()
    for symbols in prices:
        if symbols['symbol'] == str(config['appstate']['symbol'].replace("/", "")):
            return int(float(symbols['price']))

def seebalance():
    try:
        response = send_signed_request('GET', '/api/v3/account')

        if "code" in response:
            print(f"Convert error: {response}. Exiting program")
            sys.exit()

        if "balances" in response:
            print("THIS IS YOUR BALANCE")
            for balance in response['balances']:
                print(balance)
    except:
        print("cannot get order")

def getusdtbalance():
    try:
        response = send_signed_request('GET', '/api/v3/account')

        if "code" in response:
            print(f"Convert error: {response}. Exiting program")
            sys.exit()

        if "balances" in response:
            for balance in response['balances']:
                if balance['asset'] == "USDT":
                    return float(balance['free'])
    except:
        print("cannot get order")

def getquantity(amount):
    response = send_public_request("/api/v3/exchangeInfo")

    for symbol in response['symbols']:
        if symbol['symbol'] == config['appstate']['symbol'].replace("/", ""):
            precision = symbol['filters'][2]['stepSize']

            quantity = amount / getlatestprice()

            amt_str = round_step_size(float(quantity), float(precision))

            return amt_str

