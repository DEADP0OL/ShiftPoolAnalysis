# -*- coding: utf-8 -*-
import pandas as pd
import requests
from Inputs import *

forgers = requests.get(url+'delegates?orderBy=vote').json()
forgers = pd.DataFrame(forgers['delegates'])
forgers['vote']=pd.to_numeric(forgers['vote'])

forgers.to_csv('forgers.csv')

delegate = forgers['address'].iloc[0]
delegatekey = forgers['publicKey'].iloc[0]
voters = requests.get(url+'delegates/voters?publicKey='+delegatekey).json()
voters = pd.DataFrame(voters['accounts'])
voters['delegate']=delegate

if len(forgers)>1:
    for x in range(1, len(forgers)):
        delegate = forgers['address'].iloc[x]
        delegatekey = forgers['publicKey'].iloc[x]
        voters1 = requests.get(url+'delegates/voters?publicKey='+delegatekey).json()
        voters1 = pd.DataFrame(voters1['accounts'])
        voters1['delegate']=delegate
        voters=voters.append(voters1,ignore_index=True)

voters['balance']=pd.to_numeric(voters['balance'])
voters=voters[voters['balance']>0]

voters.to_csv('voters.csv')