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
import time as t
import sys as sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import shutil

#prjPath="C:/Users/fafe/workspace/BollingerBand/"
prjPath=os.path.dirname(os.path.abspath(__file__)) + '/'
analysisPath=""
archivePath=""

ls_symbols=[]

# Third Party Imports
def analysis(mkt, dt_date):
    
    plot_chart = False
    '''Main Function'''

    #ls_symbols = ["G"]

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Start and End date of the charts
    #dt_start = dt.datetime.strptime(sys.argv[1], "%Y/%m/%d") + dt.timedelta(hours=16)
    dt_start = dt.datetime(2016, 1, 1) + dt_timeofday
    dt_end = dt_date #dt.datetime.strptime(datestr, "%Y/%m/%d") + dt_timeofday

    # Get a list of trading days between the start and the end.
    ldt_timestamps = qdu.getNYSEdays(dt_start, dt_end, dt_timeofday, mkt)
    dt_start = qdu.getNYSEoffset(dt_end, -199, mkt)
    ldt_timestamps = qdu.getNYSEdays(dt_start, dt_end, dt_timeofday, mkt)
    
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess(mkt + 'Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Copying close price into separate dataframe to find rets
    df_close = d_data['close']
    df_actual_close = d_data['actual_close']
    
    #SMA
    df_sma50 = pd.rolling_mean(d_data['actual_close'], 50)
    df_sma200 = pd.rolling_mean(d_data['actual_close'], 200)
    
    #Bollinger Bands
    df_mean = pd.rolling_mean(d_data['actual_close'], 20)
    df_std = pd.rolling_std(d_data['actual_close'], 20)
    upper_bband = df_mean + (2 * df_std)
    lower_bband = df_mean - (2 * df_std) 
    df_bollinger = (df_actual_close - df_mean) / (2 * df_std)
    
    #MACD
    emaslow = pd.ewma(d_data['actual_close'], span=26)
    emafast = pd.ewma(d_data['actual_close'], span=12)
    macd = emafast - emaslow
    ema9 = pd.ewma(macd, span=9)
    
    str_date = dt.datetime.strftime(dt_end, "%Y%m%d")
    f = open(analysisPath + 'analysis-' +  str_date + '.csv','w')
    f.write('symbol,close,sma50,sma200,sma50/sma200,upper_bband,lower_bband,bollinger,macd,ema9,macd-ema9\n')
    #print df_close.tail()
    #print df_mean.tail()
    #print df_std.tail()
    #print df_bollinger.tail()
    # Plotting the prices with x-axis=timestamps
    
    for ls_symbol in ls_symbols:
        #print ls_symbol
        #print ls_symbol + ",{},{},{},{}".format(df_close[ls_symbol][dt_end],df_sma50[ls_symbol][dt_end],df_sma200[ls_symbol][dt_end], df_bollinger[ls_symbol][dt_end])
        f.write(ls_symbol + ",{},{},{},{},{},{},{},{},{},{}".format(df_close[ls_symbol][dt_end],df_sma50[ls_symbol][dt_end],df_sma200[ls_symbol][dt_end],df_sma50[ls_symbol][dt_end]/df_sma200[ls_symbol][dt_end],upper_bband[ls_symbol][dt_end],lower_bband[ls_symbol][dt_end],df_bollinger[ls_symbol][dt_end],macd[ls_symbol][dt_end],ema9[ls_symbol][dt_end],macd[ls_symbol][dt_end]-ema9[ls_symbol][dt_end])+'\n') 
        
        #print df_bollinger[ls_symbol].tail(1)
        if plot_chart:
            if df_bollinger[ls_symbol].tail(1) <= -0.75:
                plt.clf()
                plt.subplot(211)
                plt.plot(ldt_timestamps, df_close[ls_symbol], label=ls_symbol)
                plt.legend()
                plt.ylabel('Price')
                plt.xlabel('Date')
                plt.xticks(size='xx-small')
                plt.xlim(ldt_timestamps[0], ldt_timestamps[-1])
                plt.subplot(212)
                plt.plot(ldt_timestamps, df_bollinger[ls_symbol], label=ls_symbol+'-Bollinger')
                plt.axhline(1.0, color='r')
                plt.axhline(-1.0, color='r')
                plt.legend()
                plt.ylabel('Bollinger')
                plt.xlabel('Date')
                plt.xticks(size='xx-small')
                plt.xlim(ldt_timestamps[0], ldt_timestamps[-1])
                plt.savefig(ls_symbol+'.pdf', format='pdf')

    f.close()

def main(mkt, start_year, start_month, start_day, end_year, end_month, end_day):
    
    global analysisPath
    analysisPath=prjPath + mkt + "/analysis/"
    global archivePath
    archivePath=analysisPath+"/archive"

    os.chdir(prjPath)
    files = os.listdir(analysisPath)
    
    for f in files:
        if (f.startswith("analysis")):
            shutil.copy(analysisPath+f, archivePath)
            os.remove(analysisPath+f)
    
    # List of symbols
    with open(prjPath+'symbols' + mkt + '.txt') as f:
        global ls_symbols
        ls_symbols = f.read().splitlines()
    #fo = open("symbols.txt", "r+")
    #str = fo.readline();
    #fo.close()

    dt_timeofday = dt.timedelta(hours=16)
    dt_start = dt.datetime(start_year, start_month, start_day) + dt_timeofday
    dt_end = dt.datetime(end_year, end_month, end_day) + dt_timeofday
    ldt_timestamps = qdu.getNYSEdays(dt_start, dt_end, dt_timeofday, mkt)
    
    print mkt
    print dt_start
    print dt_end
    print t.localtime()
    
    for timestamp in ldt_timestamps:
        print "generating analysis: " + dt.datetime.strftime(timestamp, "%Y-%m-%d")
        analysis(mkt, timestamp)
        print dt.datetime.strftime(timestamp, "%Y-%m-%d") + " done"

    
if __name__ == '__main__':
    start_y= int(sys.argv[1])
    start_m= int(sys.argv[2])
    start_d= int(sys.argv[3])
    if (len(sys.argv) == 5):
        end_y= int(sys.argv[1])
        end_m= int(sys.argv[2])
        end_d= int(sys.argv[3])
        stockMkt = sys.argv[4]
    else:
        end_y= int(sys.argv[4])
        end_m= int(sys.argv[5])
        end_d= int(sys.argv[6])
        stockMkt = sys.argv[7]
    
    main(stockMkt, start_y, start_m, start_d, end_y, end_m, end_d)