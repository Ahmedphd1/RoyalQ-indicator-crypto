from binancelibrary import *
from calculateprice import *
# globals

print("Starting configuration")
amount = float(config['appstate']['amount']) # amount to buy crypto
opentrades = int(config['appstate']['opentrades']) # the maximum amount of trades taken
currenttrades = 0
startbot = False
callbackbool = True

print("Finished configuration")

# Those are the margin calls if the price drops, here in this example we have 4 margin calls
# [percentage_drop_to_call, x_buy_amout]
# in each margin call, the 1st element is the percentage drop to buy again, the 2nd element is the x amount to buy
# in this example, if the price drops 1%, buy $100
# if it then drops %2 from that, but another $100
# if it then drops %4 from that, but another $200
# if it then drops %6 from that, but another $200

print("Getting initial price")
# initiating starting price of the token
initateprice()

print("checking price")
seebalance()

print("Entering a trade")
if (createorder("buy", modquantity=amount) != False):  # buying the initial token with the price
    currenttrades += 1
    startbot = True
    print("Trade entered")

print("Starting bot")
# checking if we bought the initial token to enter the trade
if (startbot):
    print("Bot started")
    # checking for callback
    print("Checking for callback")
    while(callbackbool):
        callbackpercentage = checkforcallback()[0]  # getting callbackpercentage
        print(f"callback percentage: {callbackpercentage}")
        print(f"Price drop in percentage: {takeprofitcallback}")
        if (takeprofitcallback >= callbackpercentage): # if callback is lower or equal than the current percentage. sell
            if (createorder("sell", modquantity=amount) != False): # selling token
                callbackbool = False
                currenttrades -= 1
                print("Callback reached. Selling instrument")

    print("Starting main bot")
        # while the current trades is less than the max trades. keep running the program
    while (currenttrades < opentrades):
        try:
            # grabbing current percentage from initial price
            currentpercentage = calculatetakeprofit()

            # if take profit is equal or greater than the current percentage of the token, then buy
            print("take profit reached. buying token")
            if (createorder("buy", modquantity=amount) != False):  # buying the token with the specified amount
                print("token bought checking for callback")
                currenttrades += 1
                callbackbool = True

                # checking for callback
                while (callbackbool):
                    callbackpercentage = checkforcallback()[0]  # getting callbackpercentage

                    if (takeprofitcallback >= callbackpercentage):  # if callback is lower or equal than the current percentage. sell
                        print("Callback reached selling coin")
                        if (createorder("sell", modquantity=amount) != False):  # selling token
                            callbackbool = False
                            currenttrades -= 1

                            seebalance()
        except:
            print("cannot proccess order")
            sys.exit()
else:
    print("Cannot buy initial token. Please check api key or amount specificied...")
    print("exiting program")
    sys.exit()

