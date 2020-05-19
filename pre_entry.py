import pandas as pd
from kiteconnect import KiteConnect
import talib as ta


class PreEntry:
    def __init__(self, data, api_key, access_token):
        self.activated = False
        self.data = data
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token=access_token)
        self.long_position = False
        self.short_position = False
        self.master_df_updated = pd.DataFrame
        self.buy_price=None
        self.sell_price=None

    def tick_handler(self, tick):
        if self.data['long'] is True:
            if tick['last_price'] >= self.data['long_trigger']:
                self.data['long'] = False
                self.long_position = True
                # threading
                order_id = self.kite.place_order(tradingsymbol=self.data['symbol'], exchange=self.kite.EXCHANGE_NSE,
                                                 transaction_type=self.kite.TRANSACTION_TYPE_BUY,
                                                 quantity=self.data['quantity'],
                                                 variety=self.kite.VARIETY_REGULAR,
                                                 order_type=self.kite.ORDER_TYPE_MARKET, product=self.kite.PRODUCT_MIS)

                print(order_id)

        if self.data['short'] is True:
            if tick['last_price'] <= self.data['short_trigger']:
                self.data['short'] = False
                self.short_position = True
                order_id = self.kite.place_order(tradingsymbol=self.data['symbol'], exchange=self.kite.EXCHANGE_NSE,
                                                 transaction_type=self.kite.TRANSACTION_TYPE_SELL,
                                                 quantity=self.data['quantity'],
                                                 variety=self.kite.VARIETY_REGULAR,
                                                 order_type=self.kite.ORDER_TYPE_MARKET, product=self.kite.PRODUCT_MIS)
                print(order_id)


    def entry(self, df_ohlc, np_emas, tick):
        self.master_df_updated = df_ohlc
        self.master_df_updated['wr'] = ta.WILLR(self.master_df_updated['high'], self.master_df_updated['low'],
                                                self.master_df_updated['close'], timeperiod=40)
        list_r = self.master_df_updated['wr'].tolist()
        if self.activated is False:
            for i in range(-1, -1 * len(list_r), -1):
                if list_r[i] < -80 and self.data['long'] is True:
                    self.activated = True
                    break
                if list_r[i] > -20 and self.data['long'] is True:
                    self.activated = False
                    break
                if list_r[i] > -20 and self.data['short'] is True:
                    self.activated = True
                    break
                if list_r[i] <= -80 and self.data['short'] is True:
                    self.activated = False
                    break

        elif self.activated is True:
            print(self.data['symbol'])
            if self.data['long'] is True and tick['last_price'] > np_emas[0, -1] and tick['last_price'] > np_emas[1, -1] and list_r[-1] >= -20:
                self.long_position = True
                self.activated = False
                self.buy_price=tick['last_price']
                # threading
                order_id = self.kite.place_order(tradingsymbol=self.data['symbol'], exchange=self.kite.EXCHANGE_NSE,
                                                 transaction_type=self.kite.TRANSACTION_TYPE_BUY,
                                                 quantity=self.data['quantity'],
                                                 variety=self.kite.VARIETY_REGULAR,
                                                 order_type=self.kite.ORDER_TYPE_MARKET, product=self.kite.PRODUCT_MIS)
                print(order_id)

            if self.data['short'] is True and tick['last_price'] < np_emas[0, -1] and tick['last_price'] < np_emas[
                1, -1] and list_r[-1] <= -80:
                self.short_position = True
                self.activated = False
                self.sell_price=tick['last_price']
                order_id = self.kite.place_order(tradingsymbol=self.data['symbol'], exchange=self.kite.EXCHANGE_NSE,
                                                 transaction_type=self.kite.TRANSACTION_TYPE_SELL,
                                                 quantity=self.data['quantity'],
                                                 variety=self.kite.VARIETY_REGULAR,
                                                 order_type=self.kite.ORDER_TYPE_MARKET, product=self.kite.PRODUCT_MIS)

                print(order_id)
