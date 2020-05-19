from kiteconnect import KiteTicker
import trade_maker as tm


access_token='t76TZaPbsHbZ05kbsRBn0lwrod9f8Dql'
api_key='7lwrah449p8wk3i0'
tm_object=tm.Marination('2018-08-30','2018-09-11',access_token,api_key)
subscription=list(tm_object.holder_of_subscription_classes.keys())
print(subscription)
kws = KiteTicker(api_key=api_key, access_token=access_token)


def on_ticks(ws,ticks):

    tm_object.ticks_handler(ticks=ticks)


def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (VMART and TATAMOTORS here).
    ws.subscribe(subscription)

    # Set VMART to tick in `full` mode.
    ws.set_mode(ws.MODE_LTP, subscription)

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect()