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
import os
import sys as sys

import numpy as np
import pandas as pd
import csv

#prjPath = "C:/Users/fafe/workspace/BollingerBand/"
prjPath = os.path.dirname(os.path.abspath(__file__)) + '/'
analysisPath = ""

# Third Party Imports
def main(mkt, str_buy_indicator, str_boll_threshold, str_sell_offeset, stop_loss):
    
    global analysisPath 
    analysisPath = prjPath + mkt + "/analysis/"

    os.chdir(prjPath)
    
    with open(prjPath+'symbols' + mkt + '.txt') as f:
        ls_symbols = f.read().splitlines()
        
    dt_timeofday = dt.timedelta(hours=16)
    dt_start = dt.datetime(2017, 2, 15) + dt_timeofday
    dt_end = dt.datetime(2017, 12, 29) + dt_timeofday
    ldt_timestamps = qdu.getNYSEdays(dt_start, dt_end, dt_timeofday)
    #c_dataobj = da.DataAccess(mkt + 'Yahoo')
    #sls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    #ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    #d_data = dict(zip(ls_keys, ldf_data))
    #df_close = d_data['close']
    c_dataobj = da.DataAccess(mkt + 'Yahoo', cachestalltime=0)
    #global df_close
    #df_close = c_dataobj.get_data(ldt_timestamps, ls_symbols, "close")
    #df_close = df_close.fillna(method='ffill')
    #df_close = df_close.fillna(method='bfill')
    
    #global df_open
    #df_open = c_dataobj.get_data(ldt_timestamps, ls_symbols, "open")
    #df_open = df_open.fillna(method='ffill')
    #df_open = df_open.fillna(method='bfill')
    
    buy_indicator = np.float32(str_buy_indicator) 
    boll_threshold =np.float32(str_boll_threshold)
    sell_offeset = int(str_sell_offeset)
    
    '''Main Function'''
    ls_files = os.listdir(analysisPath)
    
    orders = []
    new_order = []

    for file_name in ls_files:
        if file_name.startswith("analysis") == False:
            continue
        str_date = file_name[9:17]
        dt_date = dt.datetime.strptime(str_date, "%Y%m%d")     
        analysis_row = np.loadtxt(analysisPath + file_name, dtype='S8,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4',
                            delimiter=',', comments="#", skiprows=1)
    
        # Sorting the portfolio by BOLLINGER value
        analysis_row = sorted(analysis_row, key=lambda x: x[10])
            
        # Create two list for symbol names and allocation
        #ls_order_syms = [] lf_order_smas = [] lf_order_macd = [] lf_order_bolls = []
        
        ldt_timestamp_idx = ldt_timestamps.index(dt_date + dt_timeofday) + 1
        
        for row in analysis_row:
            if row[4] >= buy_indicator and row[7]<= boll_threshold :
                #ls_order_syms.append(row[0]) #lf_order_bolls.append(row[7]) #lf_order_macd.append(row[10]) #lf_order_smas.append(row[4])
                
                #new_order =[ldt_timestamps[ldt_timestamp_idx].year, ldt_timestamps[ldt_timestamp_idx].month, ldt_timestamps[ldt_timestamp_idx].day, row[0], 'Buy', int(1000/df_open.iloc[ldt_timestamp_idx, ls_symbols.index(row[0])])]
                new_order =[ldt_timestamps[ldt_timestamp_idx].year, ldt_timestamps[ldt_timestamp_idx].month, ldt_timestamps[ldt_timestamp_idx].day, row[0], 'Buy', 1000]
                orders.append(new_order)
                
                #if(stop_loss == 0):
                new_order =[ldt_timestamps[ldt_timestamp_idx+sell_offeset].year, ldt_timestamps[ldt_timestamp_idx+sell_offeset].month, ldt_timestamps[ldt_timestamp_idx+sell_offeset].day, row[0], 'Sell', 1000]
                    #new_order =[ldt_timestamps[ldt_timestamp_idx+sell_offeset].year, ldt_timestamps[ldt_timestamp_idx+sell_offeset].month, ldt_timestamps[ldt_timestamp_idx+sell_offeset].day, row[0], 'Sell', int(1000/df_open.iloc[ldt_timestamp_idx, ls_symbols.index(row[0])])]
                #else:
                #    new_order = stop_loss_order(stop_loss, ldt_timestamps, ldt_timestamp_idx, sell_offeset, ls_symbols.index(row[0]), row[0])
                    
                orders.append(new_order)
                
    write_order(orders)
                #write_denorm_order(orders, ls_symbols)

        #if(len(ls_order_syms)>0):
            #print str_date
            #for i in range(0, len(ls_order_syms)):
                #print ls_order_syms[i]+ ",{},{}".format(lf_order_smas[i],lf_order_bolls[i])        
    print 'order generated!'
                
def write_order(orders):
    #writer = csv.writer(open('orderFromEvent_'+sys.argv[1]+'_'+sys.argv[2]+'_'+sys.argv[3]+'.csv', 'wb'), delimiter=',')
    orderFromEvent = csv.writer(open(analysisPath + 'orderFromEvent.csv', "wb"), delimiter=',')
    orderFromEventCum = csv.writer(open(analysisPath + 'orderFromEventCum.csv', "ab"), delimiter=',')
    for index in range(len(orders)):
        row_to_enter = [ orders[index][0],orders[index][1],orders[index][2],orders[index][3],orders[index][4],orders[index][5]]
        orderFromEvent.writerow(row_to_enter)
        orderFromEventCum.writerow(row_to_enter)

def write_denorm_order(orders, ls_symbols):
    
    writer = csv.writer(open(analysisPath + '/orderDenormalizerFromEvent.csv', 'wb'), delimiter=',')
    sym_in_portfolio = pd.DataFrame(dt.date(1999,1,1),ls_symbols,columns=('buy_date','sell_date'))
    for index in range(len(orders)):
        #if orders[index][4] == 'Buy' and ( (orders[index][3] in sym_in_portfolio and dt.datetime(orders[index][0],orders[index][1],orders[index][2]) > sym_in_portfolio[orders[index][3]][1]) or orders[index][3] not in sym_in_portfolio) :
        if orders[index][4] == 'Buy' and dt.date(orders[index][0],orders[index][1],orders[index][2]) > sym_in_portfolio.loc[orders[index][3] ,'sell_date'] :
            
            sym_in_portfolio.loc[orders[index][3] ,'buy_date'] = dt.date(orders[index][0],orders[index][1],orders[index][2]) 
            sym_in_portfolio.loc[orders[index][3] ,'sell_date'] = dt.date(orders[index+1][0],orders[index+1][1],orders[index+1][2]) 
            
            row_to_enter = [ orders[index][0],orders[index][1],orders[index][2],orders[index][3],orders[index][4],orders[index][5]]
            writer.writerow(row_to_enter)
            row_to_enter = [ orders[index+1][0],orders[index+1][1],orders[index+1][2],orders[index+1][3],orders[index+1][4],orders[index+1][5]]
            writer.writerow(row_to_enter)
        else:
            continue

#def stop_loss_order(stop_loss, ldt_timestamps, ldt_timestamp_idx, sell_offeset, symbol_index, symbol):
    
#    init_rtn = df_open.iloc[ldt_timestamp_idx, symbol_index]
#    stop_loss_rtn=0
#    stop_loss_daily_rtn=0
#    for i in range(0, sell_offeset):
#        temp_rtn = (df_close.iloc[ldt_timestamp_idx+i, symbol_index] - init_rtn) / init_rtn
#        if (temp_rtn < stop_loss_daily_rtn):
#            stop_loss_daily_rtn=temp_rtn 
#            stop_loss_rtn = [ldt_timestamps[ldt_timestamp_idx+i].year, ldt_timestamps[ldt_timestamp_idx+i].month, ldt_timestamps[ldt_timestamp_idx+i].day, symbol, 'Sell', int(1000/df_open.iloc[ldt_timestamp_idx, symbol_index])]
#    
#    if (stop_loss_daily_rtn < (stop_loss)/100):
#        return stop_loss_rtn
#    else:
#        return [ldt_timestamps[ldt_timestamp_idx+sell_offeset].year, ldt_timestamps[ldt_timestamp_idx+sell_offeset].month, ldt_timestamps[ldt_timestamp_idx+sell_offeset].day, symbol, 'Sell', int(1000/df_open.iloc[ldt_timestamp_idx, symbol_index])]

    
if __name__ == '__main__':
    print "generating order..."
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], 0)