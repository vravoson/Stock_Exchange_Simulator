import os
import pygame
import numpy as np
import colorsys
import multiprocessing
import threading
import matplotlib.pyplot as plt
import time

from Stock_Exchange import order_book, trader
from Script_MM import strategy_MM
from Script_T1 import strategy_T1
from Script_T2 import strategy_T2
from Script_Vins import strategy_Vins

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

def rainbow_color_stops(n=75, end=2/3):
    return [ colorsys.hls_to_rgb(end * i/((n-1)), 0.5, 1) for i in range(n) ]

blue_grad = rainbow_color_stops()
plt.style.use('dark_background')

def play_sound():
    pygame.mixer.init()
    threading.Timer(90.0, play_sound).start()
    pygame.mixer.music.load("trading_floor.mp3")
    pygame.mixer.music.play()

def run():
    try:
        play_sound()
    except KeyboardInterrupt :
        pygame.mixer.music.stop()

    book = order_book(['MM','T1','T2','Vins'])
    market_maker = trader('MM', book)
    t1 = trader('T1',book)
    t2 = trader('T2',book)
    vins = trader('Vins',book)
    start_time = time.time()

    tamp=0
    tamp_max = 200
    fig=plt.figure()
    list_price = []
    list_price_ask = [[] for i in range(10)]
    list_price_bid = [[] for i in range(10)]
    list_pnl_1,list_pnl_2,list_pnl_3,list_pnl_vins = [],[],[],[]
    ind_news=0

    while tamp<tamp_max:
        tamp+=1
        print(tamp)
        multiprocessing.Process(target = strategy_MM(book)).start()
        multiprocessing.Process(target = strategy_T1(book)).start()
        multiprocessing.Process(target = strategy_T2(book)).start()
        multiprocessing.Process(target = strategy_Vins(book)).start()
        fig.clf()
        ax1=fig.add_subplot(3,1,1)
        ax1.barh(book.bid_price[:20] + book.ask_price[:20], book.bid_vol[:20] + list(-np.array(book.ask_vol))[:20],height=0.02, color = 'white', edgecolor='black')
        for i in range(0,len(book.bid_price[:20])):
            ax1.get_children()[i].set_color(blue_grad[i])
        for i in range(0,len(book.ask_price[:20])):
            ax1.get_children()[len(book.bid_price[:20])+i].set_color(blue_grad[-i-1])
        ax1.set_title("Vin's Stock Exchange")
        ax1.set_xticklabels([np.abs(x) for x in ax1.get_xticks()])

        ax2=fig.add_subplot(3,1,2)
        for i in range(10):
            list_price_ask[i].append(book.get_limit_ask(i))
            list_price_bid[i].append(book.get_limit_bid(i))
        list_price.append((book.get_best_ask() + book.get_best_bid())/2)
        if tamp <= 50:
            ax2.plot(range(tamp),list_price, c='white')
            for i in range(10):
                ax2.plot(range(tamp),list_price_ask[i],'k--')
                ax2.plot(range(tamp),list_price_bid[i],'k--')
            for i in range(1,10):
                ax2.fill_between(range(tamp), list_price_ask[i],list_price_ask[i-1], list_price_ask[i-1], color=blue_grad[-i-1])
                ax2.fill_between(range(tamp), list_price_bid[i],list_price_bid[i-1], list_price_bid[i-1], color=blue_grad[i])
        else:
            ax2.plot(range(tamp)[tamp-50:tamp],list_price[tamp-50:tamp], c='white')
            for i in range(10):
                ax2.plot(range(tamp)[tamp-50:tamp],list_price_ask[i][tamp-50:tamp], 'k--')
                ax2.plot(range(tamp)[tamp-50:tamp],list_price_bid[i][tamp-50:tamp], 'k--')
            for i in range(1,10):
                ax2.fill_between(range(tamp)[tamp-50:tamp], list_price_ask[i][tamp-50:tamp],list_price_ask[i-1][tamp-50:tamp], list_price_ask[i-1][tamp-50:tamp], color=blue_grad[-i-1])
                ax2.fill_between(range(tamp)[tamp-50:tamp], list_price_bid[i][tamp-50:tamp],list_price_bid[i-1][tamp-50:tamp], list_price_bid[i-1][tamp-50:tamp], color=blue_grad[i])

        ax3=fig.add_subplot(3,1,3)
        list_pnl_1.append(book.trader_stats['MM']['PnL'])
        list_pnl_2.append(book.trader_stats['T1']['PnL'])
        list_pnl_3.append(book.trader_stats['T2']['PnL'])
        list_pnl_vins.append(book.trader_stats['Vins']['PnL'])
        ax3.plot(range(tamp), list_pnl_1,'r')
        ax3.plot(range(tamp), list_pnl_2,'b')
        ax3.plot(range(tamp), list_pnl_3,'green')
        ax3.plot(range(tamp), list_pnl_vins,'white')
        ax3.set_xlabel('Time')
        ax3.set_ylabel('PnL')

        plt.pause(1e-15)

if __name__=='__main__':
    run()
    