import numpy as np

#np.random.seed(0)
T = 1000
sigma = 0.02  # “波动强度”
returns = np.random.normal(0, sigma, T)
price = 100 * np.exp(np.cumsum(returns))  # 随机游走（类布朗）

realized_vol = returns.std() * np.sqrt(252)  # 年化波动(粗略)
print("Annualized vol:", realized_vol)
