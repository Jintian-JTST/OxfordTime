import numpy as np
import matplotlib.pyplot as plt


T = 200
sigma = 0.02

returns = np.random.normal(0, sigma, T)
price = 100 * np.exp(np.cumsum(returns))

cash = 10000
position = 0
entry_price = None

lookback = 5
stop_loss = 0.9
buy_size = 50
sell_size = 50

equity = []

for t in range(lookback, T):
    today_price = price[t]
    past_price = price[t - lookback]

    # ---- 买入：分批 ----
    if cash >= buy_size * today_price and today_price > past_price:
        position += buy_size
        cash -= buy_size * today_price

        if entry_price is None:
            entry_price = today_price
        else:
            entry_price = (entry_price * (position - buy_size) + buy_size * today_price) / position

        print(t, "买入", buy_size, "@", round(today_price, 2))

    # ---- 止损卖出：分批 ----
    if position >= sell_size and today_price < entry_price * stop_loss:
        position -= sell_size
        cash += sell_size * today_price
        print(t, "止损卖出", sell_size, "@", round(today_price, 2))

        if position == 0:
            entry_price = None

    equity.append(cash + position * today_price)

print("\n最终资产:", round(equity[-1], 2))

plt.plot(price)
plt.title("Price")
plt.show()

plt.plot(equity)
plt.title("Portfolio Value")
plt.show()
