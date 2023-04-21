import numpy as np
import pandas as pd

ask_orders_mm = []#prix volume
bid_orders_mm = []

def strategy_MM(book):
    trader_name_mm = 'MM'
    if len(book.lob)<=100:
        pass
    else:
        if len(ask_orders_mm)>=1:
            price,vol = ask_orders_mm[0][0], ask_orders_mm[0][1]
            try:
                trader_ask_price = book.trader[trader_name_mm]['ASK'][price]
                order_id_ask = trader_ask_price[list(trader_ask_price.keys())[0]][0]
                book.cancel_order(order_id_ask)
            except KeyError: #l'ordre a été exécuté : se hedger
                pass

            ask_orders_mm.pop(0)

        elif len(bid_orders_mm)>=1:
            price,vol = bid_orders_mm[0][0], bid_orders_mm[0][1]
            try:
                trader_bid_price = book.trader[trader_name_mm]['BID'][price]
                order_id_bid = trader_bid_price[list(trader_bid_price.keys())[0]][0]
                book.cancel_order(order_id_bid)
            except KeyError: #l'ordre a été exécuté : se hedger
                pass

            bid_orders_mm.pop(0)


        else:
            book_mid = book.lob[['L1_ask_price', 'L1_ask_vol', 'L1_bid_price', 'L1_bid_vol']].apply(lambda x: (x[0]*x[1] + x[2]*x[3])/(x[1]+x[3]) if x[1]+x[3]!=0 else 0, axis=1)
            mean_window = book_mid[-100:].mean()
            std_window = book_mid[-100:].std()
            vol_ask = int(book.lob[['L1_ask_vol']][-100:].median().iloc[0])
            vol_bid = int(book.lob[['L1_bid_vol']][-100:].median().iloc[0])
            p_ask, p_bid = mean_window - std_window/np.sqrt(100), mean_window + std_window/np.sqrt(100)
            book.limit_order(trader_name_mm,'ASK', p_ask, vol_ask)
            book.limit_order(trader_name_mm,'BID', p_bid, vol_bid)
            ask_orders_mm.append([p_ask,vol_ask])
            bid_orders_mm.append([p_bid,vol_bid])


