# Import core libraries
import csv

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import numpy as np
import os
import marketsim_web
import order_generator
import shutil
import csv

#analysis.main(2015, 1, 1, 2016, 8, 31)

shutil.rmtree('test',True)
os.mkdir('test')
os.chdir('test')

ofile  = open('run.csv', "wb")
writer = csv.writer(ofile, delimiter=',')

cash = 10000
buy_indicator = 1#0.95
while buy_indicator <= 1:#1.05 :
    for sell_offest in range(4,15):
        boll_threshold = -0.95
        while boll_threshold >= -0.95:#-1.0:
            stop_loss = 0
            while stop_loss >= -6:
            
                os.mkdir(str(buy_indicator) + '_' + str(sell_offest) + '_' + str(boll_threshold) + '_' + str(stop_loss))
                os.chdir(str(buy_indicator) + '_' + str(sell_offest) + '_' + str(boll_threshold) + '_' + str(stop_loss))
                
                order_generator.main(1, boll_threshold, sell_offest, stop_loss)
                cash_in_hand = marketsim_web.main(cash)
                
                writer.writerow([buy_indicator,sell_offest,boll_threshold,stop_loss,cash_in_hand])
                os.chdir('../')
                stop_loss -= 1.5
                
            boll_threshold += -0.05
    buy_indicator += 0.05  

ofile.close()
print 'end'