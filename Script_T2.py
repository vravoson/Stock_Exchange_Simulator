import numpy as np
import pandas as pd

#market_maker pur ?
def strategy_T2(book):
    trader_name_t2 = 'T2'
    p = np.random.normal(10,1.5)
    line = np.linspace(0.1,1,10)
    for i in range(len(line)):
        book.limit_order(trader_name_t2,'ASK', p-line[i], int(20/line[i])+1)
        book.limit_order(trader_name_t2,'BID',p+line[i], int(20/line[i])+1)