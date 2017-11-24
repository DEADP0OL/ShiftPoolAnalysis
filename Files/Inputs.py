# -*- coding: utf-8 -*-
import pandas as pd
import datetime
import os

url = 'https://wallet.shiftnrg.org/api/' #main api url
timespan = 56 #day(s)
offset = 0 #day(s)
minbalance = 100 #shift
minpayout = 1 #shift

#minbalance = minbalance*100000000
#minpayout = minpayout*100000000
offset_seconds = offset*24*60*60
timespan_seconds = timespan*24*60*60

end_pay = pd.to_datetime('today')
start_pay = end_pay- datetime.timedelta(seconds=timespan_seconds)

end_earn = end_pay- datetime.timedelta(seconds=offset_seconds)
start_earn = start_pay- datetime.timedelta(seconds=offset_seconds)