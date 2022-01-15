from binancelibrary import *
import json

margincalls = json.loads(str(config['appstate']['margincalls']))
takeprofit = float(config['appstate']['takeprofit']) # percentage to take profit
takeprofitcallback = (float(config['appstate']['takeprofitcallback'])) * -1 # if price falls below this percentage. sell

startingtokenvalue = 0

def initateprice():
    try:
        global startingtokenvalue
        startingtokenvalue = getlatestprice()
        return True
    except:
        return False

def calculatetakeprofit():
    global takeprofit
    global startingtokenvalue

    try:
        diff = getlatestprice() - startingtokenvalue
        increase = diff / startingtokenvalue * 100

        return increase
    except:
        return 0

def checkforcallback():
    try:
        oldprice = getlatestprice()
        time.sleep(15)
        newprice = getlatestprice()

        diff = newprice - oldprice
        statepercentage = diff / startingtokenvalue * 100

        return statepercentage, True
    except:
        return 0, False

def checkformargincalls():
    global margincalls

    pass
