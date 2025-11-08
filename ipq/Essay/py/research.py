import numpy as np
from scipy.optimize import curve_fit

# 提供的数据
x_data = np.array([4.28, 3.92, 3.50, 3.13, 2.41])
y_data = np.array([0.935, 0.921, 1.020, 1.050, 1.269])

# 已知的常数
I = 0.000655
F = 0.7246647

# 定义拟合函数
def fit_function(x, k1):
    return 4 * np.pi / np.sqrt(4 * (F * (x / 100) / I - (k1 * (x / 100) ** 2 / I) ** 2))

# 使用最小二乘法进行拟合
params, covariance = curve_fit(fit_function, x_data, y_data)

# 获取最佳拟合参数
best_k1 = params[0]

print("最佳拟合参数 k1:", best_k1)
