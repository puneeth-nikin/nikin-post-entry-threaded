import time
from kiteconnect import KiteConnect
import pandas as pd
import numpy as np
import std_dev as sd
import datetime
import threading
import talib as ta


class Stock:
    def __init__(self, dict_data, trade_value, api_key, access_token):

        self.partial_sold = False
        self.partial_bought=False
        self.master_df = pd.DataFrame()
        self.symbol = dict_data['symbol']
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token=access_token)
        self.short = False
        self.stock = dict_data
        self.hist_data = self.stock['data'].sort_index()
        self.long = False
        self.trade_value = trade_value
        self.long_stop_loss = None
        self.short_stop_loss = None
        self.ltp = None
        self.selected_ema = 30
        self.time_last = 0
        self.time_now = 914
        self.tick_holder = []
        self.ticks = pd.DataFrame()
        self.period_highs_lows = np.empty(shape=[2, 1])
        self.ema_periods = np.array([np.arange(2, 52, step=1), np.arange(2, 52, step=1)])
        self.std_dev_holder = sd.Grinder(self.hist_data)
        self.std_dev_holder.standard_deviation_calculator()
        self.emas_high=pd.DataFrame()
        self.emas_low=pd.DataFrame()
        self.np_emas_low=None
        self.np_emas_high = None
        self.np_stoploss=np.empty(shape=(self.hist_data.shape[0],2))
        self.np_stoploss[:]=np.nan
        self.first=True
        self.buy_price=None
        self.sell_price=None
        self.quantity=0
        self.original_quantity=0

    def tick_handler(self, tick):
        self.ltp = tick['last_price']
        self.tick_holder.append(self.ltp)

        self.time_now = (time.localtime(time.time()).tm_hour * 100) + time.localtime(time.time()).tm_min

        if self.time_now > self.time_last and (self.time_now%5==0 or self.first==True):
            self.first=False
            self.time_last = self.time_now
            dict_ohlc = {'open': self.tick_holder[0], 'high': max(self.tick_holder), 'low': min(self.tick_holder),
                         'close': self.tick_holder[-1]}

            pd_ohlc = pd.DataFrame(dict_ohlc, index=pd.DatetimeIndex([datetime.datetime.now()], tz='Asia/Kolkata'))

            self.hist_data = self.hist_data.append(pd_ohlc)
            # check for index
            self.hist_data = self.hist_data.sort_index()
            self.tick_holder.clear()
            self.master_df=self.hist_data

            for i in range(2, 100):
                ema_period = 'ema' + str(i)
                self.emas_high[ema_period] = ta.EMA(self.hist_data['high'], timeperiod=i)
                self.emas_low[ema_period] = ta.EMA(self.hist_data['low'], timeperiod=i)
                self.master_df['high_'+ema_period]=ta.EMA(self.hist_data['high'], timeperiod=i)
                self.master_df['low_'+ema_period]=ta.EMA(self.hist_data['low'], timeperiod=i)
            self.np_emas_high=np.array(self.emas_high)
            self.np_emas_low = np.array(self.emas_low)

            self.std_dev_holder = sd.Grinder(self.hist_data)
            self.std_dev_holder.standard_deviation_calculator()

            std_dev_current_long = self.std_dev_holder.percent_standard_deviation_highs[-1, -1]
            multiplier_long = self.std_dev_holder.percent_standard_deviation_mean_highs[-1]
            ratio_long = int(round(self.selected_ema / (std_dev_current_long / multiplier_long)))
            self.long_stop_loss = self.std_dev_holder.np_emas[1, min( ratio_long - 2,8)]

            std_dev_current_short = self.std_dev_holder.percent_standard_deviation_lows[-1, -1]
            multiplier_short = self.std_dev_holder.percent_standard_deviation_mean_lows[-1]
            ratio_short = int(round(self.selected_ema / (std_dev_current_short / multiplier_short)))
            self.short_stop_loss = self.std_dev_holder.np_emas[0,min( ratio_short - 2,8)]

            np.vstack((self.np_stoploss,[[self.long_stop_loss,self.short_stop_loss]]))

            print(self.symbol,self.short,multiplier_short,ratio_short,self.short_stop_loss,std_dev_current_short,self.std_dev_holder.np_emas)
            """
            self.master_df['standard_deviations_50_highs']=pd.Series(list(self.std_dev_holder.standard_deviation_highs_original[:,-2]),index=self.master_df.index)
            self.master_df['standard_deviations_50_low']=pd.Series(list(self.std_dev_holder.standard_deviation_lows_original[:,-2]),index=self.master_df.index)

            self.master_df['long_stop_loss']=pd.Series(list(self.np_stoploss[:,0]),index=self.master_df.index)
            self.master_df['short_stop_loss']=pd.Series(list(self.np_stoploss[:,1]),index=self.master_df.index)
            thread_write_files=threading.Thread(target=self.writer())
            thread_write_files.start()
            """

        if self.long or self.short:
            self.position_handler()

        return self.long,self.short


    def position_handler(self):
        if self.long:
            if self.ltp/self.buy_price>1.01 and self.partial_sold is False:
                self.original_quantity = self.quantity
                partial_quantity=round(0.66*self.quantity)
                self.partial_sold=True

                self.quantity=self.quantity-partial_quantity
                order_id = self.kite.place_order(tradingsymbol=self.symbol, exchange=self.kite.EXCHANGE_NSE,
                                                 transaction_type=self.kite.TRANSACTION_TYPE_SELL,
                                                 quantity=partial_quantity,
                                                 variety=self.kite.VARIETY_REGULAR,
                                                 order_type=self.kite.ORDER_TYPE_MARKET, product=self.kite.PRODUCT_MIS)
                print(order_id)
            if self.ltp < self.long_stop_loss:
                self.long=False
                self.partial_sold=False

                order_id = self.kite.place_order(tradingsymbol=self.symbol, exchange=self.kite.EXCHANGE_NSE,
                                                 transaction_type=self.kite.TRANSACTION_TYPE_SELL,
                                                 quantity=self.quantity,
                                                 variety=self.kite.VARIETY_REGULAR,
                                                 order_type=self.kite.ORDER_TYPE_MARKET, product=self.kite.PRODUCT_MIS)

                print(order_id)
                self.quantity=self.original_quantity

        if self.short:
            if self.ltp/self.sell_price <= 0.99 and self.partial_bought is False:
                self.original_quantity = self.quantity
                partial_quantity=round(0.66*self.quantity)
                self.quantity=self.quantity-partial_quantity
                self.partial_bought=True
                order_id = self.kite.place_order(tradingsymbol=self.symbol, exchange=self.kite.EXCHANGE_NSE,
                                                 transaction_type=self.kite.TRANSACTION_TYPE_SELL,
                                                 quantity=partial_quantity,
                                                 variety=self.kite.VARIETY_REGULAR,
                                                 order_type=self.kite.ORDER_TYPE_MARKET, product=self.kite.PRODUCT_MIS)
                print(order_id)
            if self.ltp > self.short_stop_loss:
                self.partial_bought=False
                self.short=False
                order_id = self.kite.place_order(tradingsymbol=self.symbol, exchange=self.kite.EXCHANGE_NSE,
                                                 transaction_type=self.kite.TRANSACTION_TYPE_BUY,
                                                 quantity=self.quantity,
                                                 variety=self.kite.VARIETY_REGULAR,
                                                 order_type=self.kite.ORDER_TYPE_MARKET, product=self.kite.PRODUCT_MIS)
                print(order_id)
                self.quantity = self.original_quantity
