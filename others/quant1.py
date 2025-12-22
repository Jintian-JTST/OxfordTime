import numpy as np
import matplotlib.pyplot as plt

# ===== 1. 模拟一个市场 =====
np.random.seed(0)

T = 200
sigma = 0.02

returns = np.random.normal(0, sigma, T)
price = 100 * np.exp(np.cumsum(returns))

# ===== 2. 初始化交易者 =====
cash = 10000          # 现金
position = 0          # 持仓（股数）
entry_price = None    # 买入价

lookback = 5          # 看过去 5 天
stop_loss = 0.9       # 跌到买入价的 90% 就卖

# ===== 3. 交易循环 =====
for t in range(lookback, T):
    today_price = price[t]
    past_price = price[t - lookback]

    # --- 买入规则：最近在涨 + 还没买 ---
    if position == 0 and today_price > past_price:
        position = cash / today_price
        cash = 0
        entry_price = today_price
        print(f"买入 @ {today_price:.2f}")

    # --- 卖出规则：触发止损 ---
    if position > 0 and today_price < entry_price * stop_loss:
        cash = position * today_price
        position = 0
        entry_price = None
        print(f"止损卖出 @ {today_price:.2f}")

# ===== 4. 最终结果 =====
final_value = cash + position * price[-1]
profit = final_value - 10000

print("\n最终资产:", round(final_value, 2))
print("赚 / 亏:", round(profit, 2))

# ===== 5. 画价格图 =====
plt.plot(price)
plt.title("Simulated Price")
plt.xlabel("Time")
plt.ylabel("Price")
plt.show()
