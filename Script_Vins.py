import pandas as pd
import numpy as np

def strategy_Vins(book):
    if len(book.lob)>=10:
        ask,bid = book.get_best_ask(),book.get_best_bid()
        if ask is not None and bid is not None:
            vol_ask, vol_bid = book.lob.L1_ask_vol.iloc[-1],book.lob.L1_bid_vol.iloc[-1]
            book.market_order('Vins','BID', vol_ask)
            book.market_order('Vins','ASK', vol_bid)
        else:
            pass

