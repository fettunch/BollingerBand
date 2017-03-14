'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: fafe
@contact: 
@summary: Example tutorial code.
'''

# QSTK Imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as qdu
import QSTK.qstkutil.tsutil as tsu

import datetime as dt
import sys as sys
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv

# Third Party Imports
def main():
    
    with open('symbols.txt') as f:
        ls_symbols = f.read().splitlines()
    dt_timeofday = dt.timedelta(hours=16)
    dt_start = dt.datetime(2016, 1, 1) + dt_timeofday
    dt_end = dt.datetime(2016, 12, 31) + dt_timeofday
    ldt_timestamps = qdu.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    df_close = d_data['close']

    '''Main Function'''
    na_order = np.loadtxt('orderFromEvent.csv', dtype='i,i,i,S5,S4,f4',
                        delimiter=',', comments="#", skiprows=1)
    
    # Create two list for symbol names and allocation
    ls_order_syms = []
    lf_order_smas = []
    lf_order_bolls = []
    
    
    for order in na_order:
        ldt_timestamps.index(dt.datetime(order[0], order[1], order[2]) + dt_timeofday)
        ls_order_syms.append(order[0])
        lf_order_bolls.append(order[4])
        lf_order_smas.append(order[5])
        
        new_order =[ldt_timestamps[ldt_timestamp_idx].year, ldt_timestamps[ldt_timestamp_idx].month, ldt_timestamps[ldt_timestamp_idx].day, order[0], 'Buy', 100]
        orders.append(new_order)
        new_order =[ldt_timestamps[ldt_timestamp_idx+3].year, ldt_timestamps[ldt_timestamp_idx+3].month, ldt_timestamps[ldt_timestamp_idx+3].day, order[0], 'Sell', 100]
        orders.append(new_order)

    if(len(ls_order_syms)>0):
        print str_date
        for i in range(0, len(ls_order_syms)):
            print ls_order_syms[i]+ ",{},{}".format(lf_order_smas[i],lf_order_bolls[i])        

if __name__ == '__main__':
    main()
