import numpy as np
import matplotlib.pyplot as plt

# 给定的参数
I = 0.000655
F = 0.7246667
a = 5

# 不同的 k 值
k_values = [0, 0.05, 0.5, 1, 2, 2.5]

# 定义理论拟合曲线
def function(x,k):
    return 2 * np.pi / np.sqrt((F * (x / 100) / I)*((1 - 2 * (k * (x / 100) ** 2 / I) * (a * np.pi / 180))) / (np.exp(
                                    -2 * (k * (x / 100) ** 2 / I) * (a * np.pi / 180))))


# 绘制不同 k 值下的曲线
x_values = np.linspace(0, 9, 100)
colors = ['black', 'red', 'green', 'blue', 'purple', 'orange']

for i, k_value in enumerate(k_values):
    y_values = [function(x, k_value) for x in x_values]
    plt.plot(x_values, y_values, label=f'k = {k_value}', color=colors[i])

# 设置图形的标题和坐标轴标签
plt.title('Effect of Different k Values on Function')
plt.xlabel('R (cm)')
plt.ylabel('T (s)')

# 显示图形
plt.show()
