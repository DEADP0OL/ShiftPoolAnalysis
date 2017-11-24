# -*- coding: utf-8 -*-
import pandas as pd
import requests
from Inputs import *

blocks = pd.read_csv("blocks.csv",dtype={'id': 'str'},index_col=0,parse_dates=['Date_Time'])
transactions = pd.read_csv("transactions.csv",dtype={'id': 'str','blockId':'str'},index_col=0,parse_dates=['Date_Time'])
voters = pd.read_csv("voters.csv",index_col=0)
forgers = pd.read_csv("forgers.csv",index_col=0)
#pools = pd.read_csv("pools.csv",index_col=0)

earningblocks=blocks.loc[(blocks['Date_Time']>start_earn)&(blocks['Date_Time']<=end_earn)]
earnings = earningblocks[['generatorId','generatorPublicKey','totalForged']].groupby(['generatorId','generatorPublicKey'],as_index=False).sum()

#payouts = transactions[['senderId','recipientId','amount','Count']].groupby(['senderId','recipientId'],as_index=False).agg({'amount':'sum','Count':'sum'})
#payouts = pd.merge(voters, payouts, left_on=['delegate','address'], right_on = ['senderId','recipientId'],  how='left')
transactions = transactions.loc[(transactions['Date_Time']>start_pay)&(transactions['Date_Time']<=end_pay)]
payouts = pd.merge(voters, transactions, left_on=['delegate','address'], right_on = ['senderId','recipientId'],  how='left')

payoutcount = transactions[['senderId','recipientId','Count']].groupby(['senderId','recipientId'],as_index=False).agg({'Count':'sum'})
payoutcount.rename(columns={'Count':'Paycount'}, inplace=True)
payouts = pd.merge(payouts, payoutcount, on=['senderId','recipientId'],  how='left')

voters['votes']=1
voterweights = voters[['address','balance','votes']].groupby('address').agg({'balance':'mean','votes':'sum'})
voterweights = voterweights.reset_index()
voters = voters.drop('votes', 1)

voters_all=pd.merge(voters,voterweights[['address','votes']],on='address',how='left')
voters_all['voter']=voters_all['address']

alldata=pd.merge(forgers,earnings[['generatorId','totalForged']], left_on='address',right_on='generatorId',how='left')
alldata=pd.merge(alldata,voters_all[['voter','balance','votes','delegate']], left_on='address',right_on='delegate',how='left')
alldata=pd.merge(alldata,payouts[['senderId','recipientId','amount','Count','Date_Time','id','Paycount']], left_on=['delegate','voter'],right_on=['senderId','recipientId'],how='left')
voters_all = voters_all.drop('voter', 1)
alldata = alldata.drop(['generatorId','senderId','delegate'], 1)
alldata['amount']=alldata['amount']#.fillna(0)
alldata['Vote_Weight_Percent']=alldata['balance']/alldata['vote']
alldata['Voter_Forged_Portion']=alldata['Vote_Weight_Percent']*alldata['totalForged']
alldata['Voter_Payout']=alldata['amount']/(alldata['Voter_Forged_Portion']/alldata['Paycount'])
alldata['Payout_Mean']=alldata['Voter_Payout']#.fillna(0)
alldata['Payout_Median']=alldata['Voter_Payout']#.fillna(0)
alldata['Payout_Std']=alldata['Voter_Payout']#.fillna(0)
alldata.rename(columns={'amount':'Payout','username':'Delegate','Count':'Payout_Count'}, inplace=True)
alldata['totalForged']=alldata['totalForged']/100000000
alldata['Payout']=alldata['Payout']/100000000
alldata['balance']=alldata['balance']/100000000
alldata['balance_paid']=alldata['balance']*alldata['Payout']/alldata['Payout']
alldata['vote']=alldata['vote']/100000000
alldata['Voter_Forged_Portion']=alldata['Voter_Forged_Portion']/100000000

summary=alldata
#summary=alldata.loc[alldata['balance']>minbalance]
#summary=alldata[alldata['Voter_Payout']>minpayout]
summary=summary.sort_values('Voter_Payout',ascending=False)

cols = ['Delegate','voter','rank','productivity','address','vote','totalForged','Payout','Payout_Mean','Payout_Median','Payout_Std','Payout_Count','balance_paid']
aggs = {'address':'first',
        'rank':'first',
        'productivity':'first',
        'vote':'first',
        'totalForged':'first',
        'Payout':'sum',
        'Payout_Mean':'mean',
        'Payout_Median':'median',
        'Payout_Std':'mean',
        'Payout_Count':'sum',
        'balance_paid':'mean'}
analysis = summary[cols].groupby(['Delegate','voter'],as_index=False).agg(aggs).sort_values('Payout_Mean', ascending=False)
cols = ['Delegate','rank','productivity','address','vote','totalForged','Payout','Payout_Mean','Payout_Median','Payout_Std','Payout_Count','balance_paid']
aggs = {'address':'first',
        'rank':'first',
        'productivity':'first',
        'vote':'first',
        'totalForged':'first',
        'Payout':'sum',
        'Payout_Mean':'mean',
        'Payout_Median':'median',
        'Payout_Std':'std',
        'Payout_Count':'sum',
        'balance_paid':'sum'}
analysis = analysis[cols].groupby('Delegate',as_index=False).agg(aggs).sort_values('Payout_Mean', ascending=False)
analysis['Payout_Percent']=analysis['Payout_Median']*analysis['balance_paid']/analysis['vote']
#analysis.rename(columns={'Payout_Median':'Payout_Effective'}, inplace=True)

#alldata=pd.merge(alldata,analysis[['Delegate','Payout_Effective']],on='Delegate', how='left')

alldata['Payout_Mean'] = alldata['Delegate'].map(analysis.set_index('Delegate')['Payout_Mean'])
alldata['Payout_Median'] = alldata['Delegate'].map(analysis.set_index('Delegate')['Payout_Median'])
alldata['Payout_Std'] = alldata['Delegate'].map(analysis.set_index('Delegate')['Payout_Std'])
alldata['Payout_Percent'] = alldata['Delegate'].map(analysis.set_index('Delegate')['Payout_Percent'])


alldata.to_csv('results.csv')
analysis.to_csv('analysis.csv')