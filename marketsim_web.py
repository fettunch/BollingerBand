# Import core libraries
from sys import argv
from os.path import exists
import csv

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import numpy as np

def main(cash):
    
    #script, start_portval, ifile, ofile = argv
    #ifile = "orderFromEvent.csv"
    ifile = "orderFromEvent.csv"
    start_portval = cash
    ofile = "values.csv"
    
    order_list = []
    # Start with symbols as Set to allow capturing unique values
    ls_symbols = set([])
    
    # Read Orders from input file
    if not exists(ifile):
        print "Input file does not exist"
        exit()
    input_file = csv.reader(open(ifile, 'rU'), delimiter=',')
    order_count = 0
    for input_row in input_file:
        order_date = dt.datetime(int(input_row[0]), int(input_row[1]), int(input_row[2]),16,0,0)
        order_symbol = input_row[3]
        ls_symbols.add(order_symbol)
        order_type = input_row[4]
        order_qty = int(input_row[5])
        in_row = [order_date, order_symbol, order_type, order_qty]
        order_list.append(in_row)
        order_count += 1 
    # Sort Orders on date    
    order_list.sort()
    
    # Convert symbols from Set to List to allow indexed access
    ls_symbols = list(ls_symbols)
    
    dt_start = order_list[0][0]
    dt_end = order_list[-1][0]
    
    dt_timeofday = dt.timedelta(hours=16)
    # Get a list of trading days between the start and the end.    
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    
    # Reading just the close prices    
    df_close = c_dataobj.get_data(ldt_timestamps, ls_symbols, "close")
    df_close = df_close.fillna(method='ffill')
    df_close = df_close.fillna(method='bfill')
    
    df_open = c_dataobj.get_data(ldt_timestamps, ls_symbols, "open")
    df_open = df_open.fillna(method='ffill')
    df_open = df_open.fillna(method='bfill')
    
    daily_port_val = []
    daily_port_qty = np.zeros([1,len(ls_symbols)])
    cash_in_hand = float(start_portval)
    day_count = len(ldt_timestamps)
    daily_mtm = float(start_portval)
    
    i = 0
    a = 0
    while i < day_count:
        #order_val = 0
        daily_row = np.zeros([1,len(ls_symbols)])
        if i > 0:
            daily_row[0,:] = daily_port_qty[i-1]
            daily_port_qty = np.append(daily_port_qty, daily_row, axis=0)    
        if ldt_timestamps[i] == order_list[a][0]:
            while a < order_count: 
                if ldt_timestamps[i] == order_list[a][0]:
                    # Get position of symbol in List to update quantity in appropriate column in numpy array 
                    x = ls_symbols.index(order_list[a][1])
                    # Get appropriate adjusted closing price from panda dataframe based on symbol position
                    #order_val = df_close.iloc[i, x] * order_list[a][3]
                    if order_list[a][2] == 'Buy':
                        cash_in_hand -= df_open.iloc[i, x] * order_list[a][3]
                        daily_port_qty[i,x] += order_list[a][3]
                    else: # Order type is Sell
                        cash_in_hand += df_close.iloc[i, x] * order_list[a][3]              
                        daily_port_qty[i,x] -= order_list[a][3]                    
                    #print order_list[a][0], order_list[a][1], x, df_close.iloc[i, x], daily_port_qty[i]
                    a += 1
                else:
                    break 
    
        # Multiple portfolio quantity with daily adjusted close to get daily portfolio mtm                
        daily_mtm = np.dot(daily_port_qty[i,:], df_close.iloc[i, :])
        daily_row = [ldt_timestamps[i],cash_in_hand, daily_mtm]
        daily_port_val.append(daily_row)
        i += 1
        
    # Write Portfolio values to output file
    
    ofile  = open(ofile, "wb")
    writer = csv.writer(ofile, delimiter=',')
    x = 0
    while x < day_count:
       out_row = daily_port_val[x]
       writer.writerow(out_row)
       x += 1
    ofile.close()       
    
    return cash_in_hand

if __name__ == '__main__':
    cash_in_hand =  main(2469.42)
    print 'cash return: ' + str(cash_in_hand)