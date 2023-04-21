# Stock_Exchange_Simulator

## Preview

https://user-images.githubusercontent.com/90440729/233584453-2e0cf08f-2893-4e71-99d5-87e58d82ba06.mp4

## Goal

The goal of this project is to simulate an equity stock exchange, where one security is traded by several strategic market participants.

Constraint: Use matplotlib to create visual snapshots of the stock exchange
Results

I implemented the following features in the stock exchange:

- Market participants can submit limit and market orders, and cancel their orders at any time.
- Every time an action occurs in the limit order book (e.g., partial execution, order cancellation, etc.), it is stored in the order book data, which traders can use to build their strategies.

Then, I implemented the behavior of several market participants:

- A market maker
- A mean reversion trader
- Some noise
- My own strategy

In the visual snapshots of the limit order book, the plot at the bottom represents the evolution of the PnL of the trading algorithms over time.

## Improvements

The code becomes very slow after ~50 iterations, probably because of the order book data stored in memory. My system is also not able to handle a large number of market participants (4 market participants is already a lot).



