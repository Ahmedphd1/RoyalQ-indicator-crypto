from binancelibrary import *
from configparser import ConfigParser

file = "config.ini"
config = ConfigParser()
config.read(file)

fromdate = str(config['appstate']['fromdate'])
todate = str(config['appstate']['todate'])
token = config['appstate']['symbol'].replace("/", "")
margincalls = json.loads(str(config['appstate']['margincalls']))

startingbalanceusdt = float(config['appstate']['amount']) * float(config['appstate']['opentrades'])
firstprice = startingbalanceusdt

def gethistoricaldata(): # token = btcusdt: date = 1 nov 2021
    mylist = []
    mydate = []
    mydata = client.get_historical_klines(token, client.KLINE_INTERVAL_1MINUTE, fromdate, todate)

    for data in mydata:
        mylist.append(data[1])
        mydate.append(data[0])

    return mylist, mydate

def calculatetakeprofit(currentprice, initiatedprice):

    try:
        diff = currentprice - initiatedprice
        increase = diff / initiatedprice * 100

        return increase
    except:
        return 0

def checkforcallback(lastprice, currentprice):
    try:
        oldprice = lastprice
        newprice = currentprice

        diff = newprice - oldprice
        statepercentage = diff / lastprice * 100

        return statepercentage, True
    except:
        return 0, False

def calculateprofit():
    myprofit = startingbalanceusdt - firstprice

    return myprofit

def buyorder(amount, btcprice):
    global startingbalanceusdt

    startingbalanceusdt -= amount

    quantity = amount / btcprice

    return quantity


def sellorder(quantity, btcprice):
    global startingbalanceusdt

    price = quantity * btcprice
    startingbalanceusdt += price




