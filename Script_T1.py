import numpy as np
import pandas as pd

#market_maker pur ?
def strategy_T1(book):
    trader_name_t1 = 'T1'
    if len(book.lob)<=10:
        p = np.random.normal(10,2)
        book.limit_order(trader_name_t1,'ASK', p-1, 50)
        book.limit_order(trader_name_t1,'ASK', p-0.1, 100)
        book.limit_order(trader_name_t1,'BID', p+0.1, 100)
        book.limit_order(trader_name_t1,'BID',p+1,50)
    else:
        book_mid = book.lob[['L1_ask_price', 'L1_ask_vol', 'L1_bid_price', 'L1_bid_vol']].apply(lambda x: (x[0]*x[1] + x[2]*x[3])/(x[1]+x[3]) if x[1]+x[3]!=0 else 0, axis=1)
        mean_window = book_mid[-100:].mean()
        std_window = book_mid[-100:].std()
        vol_ask = int(book.lob[['L1_ask_vol']][-100:].median().iloc[0])
        vol_bid = int(book.lob[['L1_bid_vol']][-100:].median().iloc[0])
        p_ask, p_bid = mean_window - std_window/np.sqrt(100), mean_window + std_window/np.sqrt(100)
        book.limit_order(trader_name_t1,'ASK', p_ask, vol_ask)
        book.limit_order(trader_name_t1, 'BID', p_bid, vol_bid)


