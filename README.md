# Stock_Exchange_Simulator

## Preview

https://user-images.githubusercontent.com/90440729/233584453-2e0cf08f-2893-4e71-99d5-87e58d82ba06.mp4

## Goal

The goal of this project is to simulate an equity stock exchange, at the microstructure level, where one security is traded by several strategic market participants.

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

In the visual snapshots of the limit order book:
- The plot at the top represents the 10 bid/ask limits of the limit order book.
- The plot in the middle represents the midprice, as well as the prices at each of the 10 bid/ask limits of the limit order book.
- The plot at the bottom represents the evolution of the PnL of the trading algorithms over time.

## Future Work

- The code slows down significantly after around 50 iterations, most likely due to the large amount of order book data being stored in memory and the accumulation of non-executed limit orders in the book.
- My system is also unable to handle a large number of market participants, as it becomes very slow with more than five algorithmic traders (especially if they submit a lot of orders).
- The visual stock exchange platform could be improved with additional features such as titles and a legend.



