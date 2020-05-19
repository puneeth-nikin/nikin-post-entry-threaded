import numpy as np
import pandas as pd
import talib as ta
from kiteconnect import KiteConnect


kite = KiteConnect(api_key='7lwrah449p8wk3i0')
kite.set_access_token('CWTBON7bsTuqaaZEIS3F4L1YazQKMKbv')


class Grinder:
    def __init__(self, df_data):

        self.df_data = df_data
        self.df_data = self.df_data.sort_index()
        self.df_data = self.df_data[['open', 'high', 'low', 'close']]
        self.df_emas_high = pd.DataFrame()
        self.df_emas_low = pd.DataFrame()
        for i in range(2, 11):
            ema_period = 'ema' + str(i)
            self.df_emas_high[ema_period] = ta.EMA(self.df_data['high'], timeperiod=i)
            self.df_emas_low[ema_period] = ta.EMA(self.df_data['low'], timeperiod=i)
        self.np_emas_high = np.array(self.df_emas_high)
        self.np_emas_low = np.array(self.df_emas_low)
        self.np_hl = np.array(self.df_data[['high', 'low']])
        self.np_highs = self.np_hl[:, 0]
        self.np_lows = self.np_hl[:, 1]
        self.sq_np_highs = self.np_highs ** 2
        self.sq_np_lows = self.np_lows ** 2
        self.adder_highs = np.zeros(shape=(np.shape(self.np_emas_high)[0], 9))
        self.holder_highs = self.np_highs
        self.adder_lows = np.zeros(shape=(np.shape(self.np_emas_low)[0], 9))
        self.holder_lows = self.np_lows
        self.sq_adder_highs = np.zeros(shape=(np.shape(self.np_emas_high)[0], 9))
        self.sq_holder_highs = self.sq_np_highs
        self.sq_adder_lows = np.zeros(shape=(np.shape(self.np_emas_low)[0], 9))
        self.sq_holder_lows = self.sq_np_lows
        self.standard_deviation_highs = np.zeros(shape=(np.shape(self.np_emas_high)[0], 9))
        self.standard_deviation_lows = np.zeros(shape=(np.shape(self.np_emas_low)[0], 9))
        self.standard_deviation_highs_original = np.zeros(shape=(np.shape(self.np_emas_high)[0], 9))
        self.standard_deviation_lows_original = np.zeros(shape=(np.shape(self.np_emas_low)[0], 9))
        self.percent_standard_deviation_highs = np.zeros(shape=(np.shape(self.np_emas_high)[0], 9))
        self.percent_standard_deviation_lows = np.zeros(shape=(np.shape(self.np_emas_low)[0], 9))
        self.no_of_data_points = np.arange(2, 11)
        self.standard_deviation_mean_highs = np.empty(shape=(9, 1))
        self.standard_deviation_median_highs = np.empty(shape=(9, 1))
        self.percent_standard_deviation_mean_highs = np.empty(shape=(9, 1))
        self.standard_deviation_mean_lows = np.empty(shape=(9, 1))
        self.standard_deviation_median_lows = np.empty(shape=(9, 1))
        self.percent_standard_deviation_mean_lows = np.empty(shape=(9, 1))
        self.diff_std_dev=None
        self.percent_diff_std_dev = None
        self.percent_diff_std_dev_mean = None
        self.std_dev_low_multiplier = None
        self.std_dev_high_multiplier = None
        self.std_dev_diff_multiplier = None
        self.np_emas=np.array([self.np_emas_high[-1,:],self.np_emas_low[-1,:]])


    def standard_deviation_calculator(self):
        for i in range(2, 11):

            self.holder_highs = np.roll(self.np_highs, i - 1) + self.holder_highs
            self.adder_highs[:, i - 2] = self.holder_highs

            self.sq_holder_highs = np.roll(self.sq_np_highs, i - 1) + self.sq_holder_highs
            self.sq_adder_highs[:, i - 2] = self.sq_holder_highs

            self.holder_lows = np.roll(self.np_lows, i - 1) + self.holder_lows
            self.adder_lows[:, i - 2] = self.holder_lows

            self.sq_holder_lows = np.roll(self.sq_np_lows, i - 1) + self.sq_holder_lows
            self.sq_adder_lows[:, i - 2] = self.sq_holder_lows

        self.standard_deviation_highs_original=self.standard_deviation_highs = (((self.no_of_data_points * (self.np_emas_high ** 2)) + self.sq_adder_highs - (
                    2 * self.np_emas_high * self.adder_highs)) / (self.no_of_data_points - 1)) ** 0.5

        self.standard_deviation_highs = self.standard_deviation_highs[40:, :]
        self.percent_standard_deviation_highs = (self.standard_deviation_highs / self.np_emas_high[40:, :]) * 100

        self.standard_deviation_mean_highs = np.mean(self.standard_deviation_highs, axis=0)
        self.percent_standard_deviation_mean_highs = np.mean(self.percent_standard_deviation_highs, axis=0)

        self.standard_deviation_lows_original=self.standard_deviation_lows = (((self.no_of_data_points * (self.np_emas_low ** 2)) + self.sq_adder_lows - (
                2 * self.np_emas_low * self.adder_lows)) / (self.no_of_data_points - 1)) ** 0.5

        self.standard_deviation_lows=self.standard_deviation_lows[40:,:]
        self.percent_standard_deviation_lows=(self.standard_deviation_lows/self.np_emas_low[40:,:])*100
        self.percent_standard_deviation_mean_lows=np.mean(self.percent_standard_deviation_lows, axis=0)
        self.diff_std_dev=abs(self.standard_deviation_highs-self.standard_deviation_lows)
        self.percent_diff_std_dev=(self.diff_std_dev/self.np_emas_low[40:,:])*100
        self.percent_diff_std_dev_mean=np.mean(self.percent_diff_std_dev, axis=0)