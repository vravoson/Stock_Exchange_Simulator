import time
import numpy as np
import pandas as pd
import random as rd

col_names = []
for limit in range(1,11):
    col_names+=[f'L{limit}_ask_price',
                f'L{limit}_ask_vol',
                f'L{limit}_bid_price',
                f'L{limit}_bid_vol']

class order_book:

    def __init__(self, trader_names):
        self.ask_price, self.ask_vol = [],[]
        self.bid_price, self.bid_vol = [],[]
        self.ask_seq, self.bid_seq = [],[]
        self.trader = {}
        self.trader_stats = {}
        for trader in trader_names:
            self.trader[trader] = {'ASK':{}, 'BID':{}} #ask -> price -> vol -> id (name_price_vol_datetime_eventtype)
            self.trader_stats[trader] = {'PnL':0, 'Inventory':0, 'Position':0, 'Turnover':0}
        self.lob = pd.DataFrame(columns = col_names+['datetime','trader','event','order_id'])
        self.lob.loc[0] = [0]*(len(col_names)+1) + ['','','']

    def reinit(self, trader_names):
        self.ask_price, self.ask_vol = [],[]
        self.bid_price, self.bid_vol = [],[]
        self.ask_seq, self.bid_seq = [],[]
        self.trader = {}
        self.trader_stats = {}
        for trader in trader_names:
            self.trader[trader] = {'ASK':{}, 'BID':{}} #ask -> prix -> vol -> id (name_prix_vol_datetime_eventtype)
            self.trader_stats[trader] = {'PnL':0, 'Inventory':0, 'Position':0, 'Turnover':0}
        self.lob = pd.DataFrame(columns = col_names+['datetime','trader','event','order_id'])
        self.lob.loc[0] = [0 for i in range(len(col_names)+1)] + ['','','']


    def remember_lob(self, trader, datetime, event, order_id):
        [t, dir, p, v, time, e] = order_id.split('_')
        price_vol_update = [0]*len(col_names)
        for i in range(min(len(col_names),len(self.ask_price))):
            if 4*i < len(col_names):
                price_vol_update[4*i] = self.ask_price[i]
            if 4*i+1 < len(col_names):
                price_vol_update[4*i+1] = np.sum(self.ask_vol[i])
        for i in range(min(len(col_names),len(self.bid_price))):
            if 4*i+2 < len(col_names):
                price_vol_update[4*i+2] = self.bid_price[i]
            if 4*i+3 < len(col_names):
                price_vol_update[4*i+3] = np.sum(self.bid_vol[i])

        self.lob.loc[self.lob.index.max()+1] = price_vol_update + [datetime, trader, event, order_id]
        self.lob = self.lob.iloc[-1000:]

    def get_lob(self):
        return self.lob.iloc[-1:]

    def get_best_ask(self):
        if len(self.ask_price) == 0:
            return None
        else:
            return self.ask_price[0]

    def get_limit_ask(self,i):
        if len(self.ask_price) == 0:
            return 0
        elif i>=len(self.ask_price):
            return self.get_limit_ask(i-1)
        else:
            return self.ask_price[i]

    def get_limit_bid(self,i):
        if len(self.bid_price) == 0:
            return 0
        elif i>= len(self.bid_price):
            return self.get_limit_bid(i-1)
        else:
            return self.bid_price[i]

    def get_best_bid(self):
        if len(self.bid_price) == 0:
            return None
        else:
            return self.bid_price[0]

    def cancel_order(self,order_id, remember = True):
        [trader, direction, price, vol, datetime,event] = order_id.split('_')
        price = float(price)
        vol = float(vol)

        try:
            list_id = self.trader[trader][direction][price][vol]
            if len(list_id)>1:
                self.trader[trader][direction][price][vol].remove(order_id)
            else:
                del self.trader[trader][direction][price][vol]
                if len(self.trader[trader][direction][price])==0:
                    del self.trader[trader][direction][price]

        except KeyError:
            pass


        if direction == 'ASK': #annulation d'un ordre limite d'achat
            try:
                ind = [i for i in range(len(self.ask_price)) if self.ask_price[i] == price][0]
                self.trader_stats[trader]['Position'] += vol*price
                if len(self.ask_seq[ind])==1:
                    self.ask_price.pop(ind)
                    self.ask_vol.pop(ind)
                    if order_id in self.ask_seq[ind]:
                        self.ask_seq[ind].remove(order_id)
                        self.ask_seq.remove([])
                else:
                    self.ask_vol[ind] -= vol
                    if order_id in self.ask_seq[ind]:
                        self.ask_seq[ind].remove(order_id)
            except IndexError:
                pass

        else:
            try:
                ind = [i for i in range(len(self.bid_price)) if self.bid_price[i] == price][0]
                self.trader_stats[trader]['Position'] -= vol*price
                if len(self.bid_seq[ind])==1:
                    self.bid_price.pop(ind)
                    self.bid_vol.pop(ind)
                    if order_id in self.bid_seq[ind]:
                        self.bid_seq[ind].remove(order_id)
                        self.bid_seq.remove([])

                else:
                    self.bid_vol[ind] -= vol
                    if order_id in self.bid_seq[ind]:
                        self.bid_seq[ind].remove(order_id)
            except IndexError:
                pass

        if remember:
            self.remember_lob(trader, time.time(), 'Cancel', order_id)

    def partial_execution(self,trader,vol,order_id): #trader qui exécute un volume vol < v d'un order id
        [t ,dir, p, v, datetime, event] = order_id.split('_')
        p = float(p)
        v = float(v)

        if dir == 'BID':
            try:
                ind_book = [i for i in range(len(self.bid_price)) if self.bid_price[i] == p][0]
                self.bid_vol[ind_book] -= vol
                self.bid_seq[ind_book].remove(order_id)
                self.bid_seq[ind_book] = ['_'.join([t, dir, str(p), str(v-vol), datetime,event])] + self.bid_seq[ind_book]
                self.trader_stats[t]['Turnover'] += p*vol
                self.trader_stats[t]['Inventory'] -= vol
                self.trader_stats[t]['Position'] += p*vol
                self.trader_stats[t]['PnL'] += p*vol
                self.trader_stats[trader]['Turnover'] += p*vol
                self.trader_stats[trader]['Inventory'] += vol
                self.trader_stats[trader]['Position'] -= p*vol
                self.trader_stats[trader]['PnL'] -= p*vol
            except IndexError:
                pass

        elif dir == 'ASK':
            try:
                ind_book = self.ask_price.index(p)
                self.ask_vol[ind_book] -= vol
                self.ask_seq[ind_book].remove(order_id)
                self.ask_seq[ind_book] = ['_'.join([t, dir, str(p), str(v-vol), datetime,event])] + self.ask_seq[ind_book]
                self.trader_stats[t]['Turnover'] += p*vol
                self.trader_stats[t]['Inventory'] += vol
                self.trader_stats[t]['Position'] -= p*vol
                self.trader_stats[t]['PnL'] -= p*vol
                self.trader_stats[trader]['Turnover'] += p*vol
                self.trader_stats[trader]['Inventory'] -= vol
                self.trader_stats[trader]['Position'] += p*vol
                self.trader_stats[trader]['PnL'] += p*vol
            except IndexError:
                pass

        try:
            self.trader[t][dir][p][v-vol]
            self.trader[t][dir][p][v-vol].append('_'.join([t, dir, str(p), str(v-vol), datetime,event]))
            del self.trader[t][dir][p][v]

        except KeyError:
            try:
                self.trader[t][dir][p]
                self.trader[t][dir][p][v-vol] =['_'.join([t, dir, str(p), str(v-vol), datetime,event])]
                try:
                    self.trader[t][dir][p][v]
                    del self.trader[t][dir][p][v]
                except KeyError:
                    pass
            except KeyError:
                self.trader[t][dir][p] = {v-vol : ['_'.join([t, dir, str(p), str(v-vol), datetime,event])]}

        self.remember_lob(t, time.time(), 'Partially Filled', order_id)

    def market_order(self, trader, direction, volume):
        if direction == 'ASK': #ordre de marché à l'achat, qui attaque donc le bid
            bid_depth = sum(self.bid_vol)
            vol = min(bid_depth, volume) #volume réellement exécutable
            if vol == 0:
                pass
            else:
                while vol>0 and len(self.bid_seq)>0:
                    for order_id in self.bid_seq[0]:
                        [t, dir, p, v, datetime, event] = order_id.split('_')
                        p,v = float(p), float(v)
                        if vol >= v:
                            vol -= v
                            self.trader_stats[t]['Turnover'] += p*v
                            self.trader_stats[t]['Inventory'] -= v
                            #self.trader_stats[t]['Position'] += p*v
                            self.trader_stats[t]['PnL'] += p*v
                            self.trader_stats[trader]['Turnover'] += p*v
                            self.trader_stats[trader]['Inventory'] += v
                            self.trader_stats[trader]['Position'] -= p*v
                            self.trader_stats[trader]['PnL'] -= p*v
                            self.cancel_order(order_id, remember = False)
                            self.remember_lob(t, time.time(), 'Filled', order_id)
                            if vol==0:
                                break
                        else: # v > vol : j'exécute vol restant : exécuter partiellement l'ordre
                            self.partial_execution(trader,vol,order_id)
                            vol=0
                            break

        elif direction == 'BID': #ordre de marché à l'vente, qui attaque donc l'ask
            ask_depth = sum(self.ask_vol)
            vol = min(volume, ask_depth)
            while vol > 0 and len(self.ask_seq)>0:
                for order_id in self.ask_seq[0]:
                    [t, dir, p, v, datetime, event] = order_id.split('_')
                    p,v = float(p), float(v)
                    if vol >= v:
                        vol -= v
                        self.trader_stats[t]['Turnover'] += p*v
                        self.trader_stats[t]['Inventory'] += v
                        # self.trader_stats[t]['Position'] -= p*v
                        self.trader_stats[t]['PnL'] -= p*v
                        self.trader_stats[trader]['Turnover'] += p*v
                        self.trader_stats[trader]['Inventory'] -= v
                        self.trader_stats[trader]['Position'] += p*v
                        self.trader_stats[trader]['PnL'] += p*v
                        self.cancel_order(order_id, remember = True)

                        self.remember_lob(t, time.time(), 'Filled', order_id)
                        if vol==0:
                            break
                    else: # v > vol : j'exécute vol restant : exécuter partiellement l'ordre
                        self.partial_execution(trader,vol,order_id)
                        vol=0
                        break


    def limit_order(self, trader, direction, price, vol):
        datetime = str(time.time())
        order_id = '_'.join([trader ,direction, str(price), str(vol), datetime, 'NEWO'])
        try:
            dico_vol = self.trader[trader][direction][price]
            if vol in dico_vol.keys():
                self.trader[trader][direction][price][vol].append(order_id)
            else:
                self.trader[trader][direction][price][vol] = [order_id]

        except KeyError:
            self.trader[trader][direction][price] = {}
            self.trader[trader][direction][price][vol] = [order_id]

        if direction == 'ASK':#ordre limite à l'achat
            self.trader_stats[trader]['Position'] -= vol*price
            if len(self.ask_price)==0:
                self.ask_price.append(price)
                self.ask_vol.append(vol)
                self.ask_seq.append([order_id])

            else:
                if price > self.ask_price[0]:
                    self.ask_price = [price]+self.ask_price
                    self.ask_vol = [vol]+self.ask_vol
                    self.ask_seq = [[order_id]]+self.ask_seq
                elif price < self.ask_price[-1]:
                    self.ask_price.append(price)
                    self.ask_vol.append(vol)
                    self.ask_seq.append([order_id])
                else:
                    for i in range(0,len(self.ask_price)-1):
                        if price < self.ask_price[i] and price > self.ask_price[i+1]:
                            self.ask_price = self.ask_price[:i+1]+[price]+self.ask_price[i+1:]
                            self.ask_vol = self.ask_vol[:i+1]+[vol]+self.ask_vol[i+1:]
                            self.ask_seq = self.ask_seq[:i+1]+[[order_id]]+self.ask_seq[i+1:]
                        elif price == self.ask_price[i]:
                            self.ask_vol[i] += vol
                            self.ask_seq[i].append(order_id)
                    if price == self.ask_price[-1]:
                        self.ask_vol[-1] += vol
                        self.ask_seq[-1].append(order_id)

            self.remember_lob(trader, time.time(), 'New Order', order_id)

            if (len(self.bid_price) > 0) and (price >= self.bid_price[0]):
                vol_executable = sum([self.bid_vol[i] for i in range(len(self.bid_price)) if price >= self.bid_price[i]])
                ind_order = [i for i in range(len(self.ask_price)) if self.ask_price[i] == price][0]
                if vol <= vol_executable:
                    self.cancel_order(order_id, remember = False)
                elif vol > vol_executable :#book,trader
                    self.ask_vol[ind_order] -= vol_executable
                    self.ask_seq[ind_order].remove(order_id)
                    order_id_bis = '_'.join([trader ,direction, str(price), str(vol-vol_executable), datetime, 'NEWO'])
                    self.ask_seq[ind_order] = [order_id_bis] + self.ask_seq[ind_order]
                    try:
                        dico_vol = self.trader[trader][direction][price]
                        if vol in dico_vol.keys():
                            self.trader[trader][direction][price][vol].append(order_id_bis)
                        else:
                            self.trader[trader][direction][price][vol] = [order_id_bis]

                    except KeyError:
                        self.trader[trader][direction][price] = {}
                        self.trader[trader][direction][price][vol] = [order_id_bis]
                self.market_order(trader, direction, min(vol_executable, vol))

        if direction == 'BID':#ordre limite à la vente
            self.trader_stats[trader]['Position'] += vol*price
            if len(self.bid_price)==0:
                self.bid_price.append(price)
                self.bid_vol.append(vol)
                self.bid_seq.append([order_id])

            else:
                if price < self.bid_price[0]:
                    self.bid_price = [price]+self.bid_price
                    self.bid_vol = [vol]+self.bid_vol
                    self.bid_seq = [[order_id]]+self.bid_seq
                elif price > self.bid_price[-1]:
                    self.bid_price.append(price)
                    self.bid_vol.append(vol)
                    self.bid_seq.append([order_id])
                else:
                    for i in range(0,len(self.bid_price)-1):
                        if price > self.bid_price[i] and price < self.bid_price[i+1]:
                            self.bid_price = self.bid_price[:i+1]+[price]+self.bid_price[i+1:]
                            self.bid_vol = self.bid_vol[:i+1]+[vol]+self.bid_vol[i+1:]
                            self.bid_seq = self.bid_seq[:i+1]+[[order_id]]+self.bid_seq[i+1:]
                        elif price == self.bid_price[i]:
                            self.bid_vol[i] += vol
                            self.bid_seq[i].append(order_id)
                    if price == self.bid_price[-1]:
                        self.bid_vol[-1] += vol
                        self.bid_seq[-1].append(order_id)

            self.remember_lob(trader, time.time(), 'New Order', order_id)


            if (len(self.ask_price) > 0) and (price <= self.ask_price[0]):
                vol_executable = sum([self.ask_vol[i] for i in range(len(self.ask_price)) if price <= self.ask_price[i]])
                ind_order = self.bid_price.index(price)

                if vol < vol_executable:
                    pass
                    #self.cancel_order(order_id, remember = False)
                else:#book,trader
                    self.bid_vol[ind_order] -= vol_executable
                    self.bid_seq[ind_order].remove(order_id)
                    order_id_bis = '_'.join([trader ,direction, str(price), str(vol-vol_executable), datetime, 'NEWO'])
                    self.bid_seq[ind_order] = [order_id_bis] + self.bid_seq[ind_order]
                    try:
                        dico_vol = self.trader[trader][direction][price]
                        if vol in dico_vol.keys():
                            self.trader[trader][direction][price][vol].append(order_id_bis)
                        else:
                            self.trader[trader][direction][price][vol] = [order_id_bis]

                    except KeyError:
                        self.trader[trader][direction][price] = {}
                        self.trader[trader][direction][price][vol] = [order_id_bis]

                self.market_order(trader, direction, min(vol_executable, vol))


class trader():

    def __init__(self,name,book):
        self.name = name
        self.book = book.trader[name]
        self.stats = book.trader_stats[name]
        self.inventory = book.trader_stats[name]['Inventory']
        self.PnL = book.trader_stats[name]['PnL']
        self.position = book.trader_stats[name]['Position']

    def send_limit_order(self, direction, price, volume):
        self.book.limit_order(self.name, direction, price, volume)

    def cancel_order(self, order_id):
        self.book.cancel_order(order_id, remember = True)

    def send_marker_order(self, direction, volume):
        self.book.market_order(self.name, direction, volume)





