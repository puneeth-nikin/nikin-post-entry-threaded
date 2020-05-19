import threading
import time

import pandas as pd
from kiteconnect import KiteConnect

import stockclass as sc
import pre_entry as pe


class Marination:
    def __init__(self, from_date, to_date, access_token, api_key):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token=access_token)
        self.from_date = from_date
        self.to_date = to_date
        self.api_key = api_key
        self.access_token = access_token
        self.holder_of_subscription_classes = {}
        self.holder_of_subscription_classes_entry = {}
        self.df_tradables = pd.read_csv('tradables.csv')
        self.dict_trabables = self.df_tradables.to_dict(orient='records')
        for x in self.dict_trabables:
            x['class'] = pe.PreEntry(x, api_key=self.api_key, access_token=self.access_token)
            self.holder_of_subscription_classes_entry[x['instrument_token']] = x['class']
        self.positions = self.dict_trabables
        self.position_reader()


    def ticks_handler(self, ticks):
        threads = []
        for tick in ticks:
            thread = threading.Thread(target=self.thread_ticks(tick))
            threads.append(thread)
            thread.start()
        for t in threads:
            t.join()


    def position_reader(self):
        threads = []
        for x in self.positions:
            thread = threading.Thread(target=self.thread_positions(x))
            threads.append(thread)
            thread.start()
        for t in threads:
            t.join()


    def thread_ticks(self, tick):
        self.holder_of_subscription_classes[tick['instrument_token']].long = self.holder_of_subscription_classes_entry[
            tick['instrument_token']].long_position
        self.holder_of_subscription_classes[tick['instrument_token']].short = self.holder_of_subscription_classes_entry[
            tick['instrument_token']].short_position

        self.holder_of_subscription_classes_entry[tick['instrument_token']].buy_price = \
            self.holder_of_subscription_classes_entry[tick['instrument_token']].buy_price
        self.holder_of_subscription_classes_entry[tick['instrument_token']].sell_price = \
            self.holder_of_subscription_classes_entry[tick['instrument_token']].sell_price

        self.holder_of_subscription_classes_entry[tick['instrument_token']].long_position, \
        self.holder_of_subscription_classes_entry[tick['instrument_token']].short_position = \
            self.holder_of_subscription_classes[tick['instrument_token']].tick_handler(tick)

        self.holder_of_subscription_classes_entry[tick['instrument_token']].entry(
            self.holder_of_subscription_classes[tick['instrument_token']].hist_data,
            self.holder_of_subscription_classes[tick['instrument_token']].std_dev_holder.np_emas, tick)


    def thread_positions(self, x):
        df_data = pd.DataFrame(
            self.kite.historical_data(instrument_token=x['instrument_token'], from_date=self.from_date,
                                      to_date=self.to_date,
                                      interval='5minute'))
        df_data = df_data.set_index(pd.to_datetime(df_data['date']))
        df_data = df_data.drop('date', axis=1)
        df_data = df_data.drop('volume', axis=1)
        df_data = df_data.sort_index()

        x['data'] = df_data
        x['class'] = sc.Stock(x, 5000, api_key=self.api_key, access_token=self.access_token)
        self.holder_of_subscription_classes[x['instrument_token']] = x['class']
        self.holder_of_subscription_classes[x['instrument_token']].quantity = 3
