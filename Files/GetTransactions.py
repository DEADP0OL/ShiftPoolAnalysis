# -*- coding: utf-8 -*-
import pandas as pd
import requests
from Inputs import *

maxload = 5000
blocks = pd.read_csv("blocks.csv",dtype={'id': 'str'},index_col=0)
payblocks = blocks[blocks['totalAmount'] > 0]
transactions_old = pd.read_csv("transactions.csv",dtype={'id': 'str','blockId':'str'},index_col=0)
payblocks = payblocks[~payblocks['id'].isin(transactions_old['blockId'])].dropna()

if len(payblocks)>0:
    id = payblocks['id'].iloc[0]
    #transid = transactions_old['blockId'].iloc[0]
    transactions = requests.get(url+'transactions?blockId='+id).json()
    transactions = pd.DataFrame(transactions['transactions'])
    
    if len(payblocks)>1:
        for x in range(1, len(payblocks)):
            id1 = payblocks['id'].iloc[x]
            try:
                transactions1 = requests.get(url+'transactions?blockId='+id1).json()
                transactions1 = pd.DataFrame(transactions1['transactions'])
                transactions=transactions.append(transactions1,ignore_index=True)
                if x > maxload:
                    break
            except:
                break
    
    transactions['Date_Time']=pd.to_datetime(transactions['timestamp'],unit='s',origin='5/24/2016  11:00:00')
    transactions['Count']=1
    transactions['id']=transactions['id'].apply(str)
    transactions['blockId']=transactions['blockId'].apply(str)
    transactions=transactions.drop('confirmations', axis=1)
    transactions=transactions.append(transactions_old,ignore_index=True)
    transactions=transactions.sort_values('height', ascending=False)
    transactions=transactions.reset_index(drop=True)
    
    transactions.to_csv('transactions.csv')
    print(len(payblocks)-maxload)