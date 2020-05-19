from kiteconnect import KiteConnect
import pandas as pd
import numpy as np
import talib as ta
import statistics

access_token='wRN7tG9IKSLFhmveBm59R8gmFML8oKwh'
api_key='7lwrah449p8wk3i0'
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token=access_token)

df_comp = pd.read_json('full_list.json')
dict_list_comp = df_comp.to_dict(orient='records')
dict_comp_wr={}
for i in dict_list_comp:
    oversold_sum=0
    undersold_sum=0
    df_data = pd.DataFrame(
        kite.historical_data(instrument_token=i['instrument_token'], from_date='2018-08-30',to_date='2018-09-10', interval='5minute'))
    df_data['wr']=ta.WILLR(df_data['high'], df_data['low'],df_data['close'], timeperiod=40)
    np_data=df_data['wr'].tolist()
    i['mean_price']=statistics.mean(df_data['close'].tolist())
    for j in np_data:
        if j>-20:
            oversold_sum=oversold_sum+abs(j+20)
        elif j<-80:
            undersold_sum=undersold_sum+abs(j+80)

    dict_comp_wr[i['symbol']]=oversold_sum/undersold_sum
new_tradables=[]
for key, value in dict_comp_wr.items():  # for name, age in list.items():  (for Python 3.x)
    if value >= 2.5:
        for k in dict_list_comp:
            if k['symbol']==key and k['margin']>5:
                k['quantity']=round((5000/(k['mean_price']))*k['margin'])
                k['long']=True
                k['short']=False
                new_tradables.append(k)

    if value<=0.4:
        for k in dict_list_comp:
            if k['symbol']==key and k['margin']>5:
                k['quantity']=round((5000/(k['mean_price']))*k['margin'])
                k['long']=False
                k['short']=True
                new_tradables.append(k)
df_new_list=pd.DataFrame(new_tradables)
print(df_new_list)
df_new_list.to_csv('tradables_new.csv')