# -*- coding: utf-8 -*-
import pandas as pd
import requests
from Inputs import *

timeoffset = 7 #day(s)
blockoffset = 2200*0 #block(s)
#blockoffset = blockslast-100 #block(s)
timeoffset_seconds = timeoffset*24*60*60

blocks_old = pd.read_csv("blocks.csv",dtype={'id': 'str'},index_col=0)
blocks_old = blocks_old.drop('Time_Elapsed', axis=1)
blocks_old = blocks_old.drop('Date_Time', axis=1)

blocks = requests.get(url+'blocks?offset='+str(blockoffset)).json()
blocks = pd.DataFrame(blocks['blocks'])
now = blocks['timestamp'].iloc[0]
blocks['Time_Elapsed']=now-blocks['timestamp']
last = blocks['Time_Elapsed'].iloc[99]
i=100 + blockoffset
while last <= timeoffset_seconds:
    blocks1 = requests.get(url+'blocks?offset='+str(i)).json()
    blocks1 = pd.DataFrame(blocks1['blocks'])
    blocks1['Time_Elapsed']=now-blocks1['timestamp']
    blocks=blocks.append(blocks1,ignore_index=True)
    last = blocks1['Time_Elapsed'].iloc[99]
    i=i+100

blocks['totalForged']=pd.to_numeric(blocks['totalForged'])
blocks=blocks.drop('Time_Elapsed', axis=1)
blocks=blocks.drop('confirmations', axis=1)
blocks=blocks.append(blocks_old,ignore_index=True)
blocks=blocks.sort_values('height', ascending=False)
blocks=blocks.drop_duplicates(subset='id')
blocks=blocks.drop_duplicates(subset='height')
blocks=blocks.reset_index(drop=True)
now = blocks['timestamp'].iloc[0]
blocks['Time_Elapsed']=now-blocks['timestamp']
blocks['id']=blocks['id'].apply(str)
blocks['Date_Time']=pd.to_datetime(blocks['timestamp'],unit='s',origin='5/24/2016  11:00:00')
blocks.to_csv('blocks.csv')
blockslast = i-100
