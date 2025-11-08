import numpy as np
import matplotlib.pyplot as plt
k = 0.5
I = 0.000655
F = 0.7246667
a = 5
# 定义函数
def function1(x):
    return 2 * np.pi / np.sqrt((F * (x / 100) / I)*((1 - 2 * (k * (x / 100) ** 2 / I) * (a * np.pi / 180))) / (np.exp( -2 * (k * (x / 100) ** 2 / I) * (a * np.pi / 180))))
def function2(x):
    return 4 * np.pi / np.sqrt(4 * (F * (x / 100) / I) - (k * (x / 100) ** 2 / I) ** 2)
# 给定的数据点
points_blue = [(2.41, 1.269), (4.28, 0.935), (3.92, 0.921), (3.13, 1.050), (1.05, 1.864), (1.50, 1.538), (5.76, 0.834), (7.67, 0.974),(7.96,1.203)]
points_red = [(3.5, 0.450), (5.00, 1.859)]
# 绘制函数曲线
x_values = np.linspace(0, 9, 100)
y_values1 = function1(x_values)
y_values2 = function2(x_values)
# 绘制数据点
x_blue, y_blue = zip(*points_blue)
x_red, y_red = zip(*points_red)
plt.plot(x_values, y_values1, label='Proportional model', color='purple')
plt.plot(x_values, y_values2, label='Square model', color='green', linestyle='dashed')
plt.scatter(x_blue, y_blue, color='blue', label='Blue Points')
plt.scatter(x_red, y_red, color='red', label='Red Points')
# 设置图形的标题和坐标轴标签坐标轴范围
plt.xlabel('R (cm)')
plt.ylabel('T (s)')
plt.xlim(0, 9)
plt.ylim(0, 3)
# 显示图形
plt.show()
