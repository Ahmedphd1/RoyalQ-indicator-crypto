from binancelibrary import *
from backtestlibrary import *
import json
import pickle
from datetime import datetime

print("Starting configuration")
amount = float(config['appstate']['amount']) # amount to buy crypto
opentrades = int(config['appstate']['opentrades']) # the maximum amount of trades taken
takeprofit = float(config['appstate']['takeprofit']) # percentage to take profit
takeprofitcallback = (float(config['appstate']['takeprofitcallback'])) * -1 # if price falls below this percentage. sell
currenttrades = 0
mypricedata = 0
mydate = 0
initprice = 0
conditioner = 0 # 0 for buy : 1 for sell
currentquantity = 0
takeprofitreached = False

if (input("Download historical data: Y/N: ").lower() == "Y".lower()):
    with open('outfile', 'wb') as fp:
        pickle.dump(gethistoricaldata(), fp)

with open('outfile', 'rb') as fp:
    itemlist = pickle.load(fp)
    mypricedata = itemlist[0]
    initprice = mypricedata[0]
    mydate = itemlist[1]

print(f"******************** Callback: {float(takeprofitcallback)} ***************************************")
print(f"******************** Using margin calls: {margincalls} ***************************************")
if (type(mypricedata) == list):
    print("Backtesting historical price data")
    for x in mypricedata:
        if conditioner == 0:
            print("Take profit reached. Attempting to buy")
            currentquantity = buyorder(float(amount), float(x))
            print({"status": "bought", "price": {float(x)}, "prev price": {float(mypricedata[mypricedata.index(x) - 1])}, "date": datetime.utcfromtimestamp(mydate[mypricedata.index(x) -1] / 1000).strftime('%Y-%m-%d %H:%M:%S')})
            currenttrades += 1
            conditioner = 1
        else:
            callbackpercentage = checkforcallback(float(mypricedata[mypricedata.index(x) - 1]), float(x))[0]
            currentpercentage = calculatetakeprofit(float(x), float(initprice))

            if ((takeprofit)  <= currentpercentage):
                takeprofitreached = True

            if (takeprofitcallback >= callbackpercentage and takeprofitreached):
                print("Callback reached. Selling token")
                sellorder(float(currentquantity), float(x))
                print({"status": "sold", "price": {float(x)}, "prev price": {float(mypricedata[mypricedata.index(x) - 1])}, "date": datetime.utcfromtimestamp(mydate[mypricedata.index(x) -1] / 1000).strftime('%Y-%m-%d %H:%M:%S'), "token percentage change": {callbackpercentage}, "your callback": {takeprofitcallback}})
                currenttrades -= 1
                conditioner = 0
                currentquantity = 0
                initprice = float(x)
                takeprofitreached = False
    if (currentquantity != 0):
        sellorder(float(currentquantity), float(mypricedata[-1]))

    print(f"This is profit in USDT: {calculateprofit()}")
else:
    print("Price data not downloaded. please download it")

