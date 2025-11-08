import numpy as np
import matplotlib.pyplot as plt

# 给定的常数
C = 0.088
k = 16.0e-3
I = 0.070e-3
m = 36.0e-3
V = 5.00e-6
R = 25.7e-3
F = 0.30411

# 计算 r1 和 r2
r1 = k * R**2 / I
r2 = F * R / I

# 定义函数
def theta(t):
    return C * np.exp(-r1 / 2 * t) * np.cos(np.sqrt(4 * r2 - r1**2) / 2 * t)

# 生成时间数据
t_values = np.linspace(0, 5, 1000)

# 计算 theta 对应的角度数据
theta_values = theta(t_values)

# 将角度转换为度数
theta_values_deg = np.degrees(theta_values)

# 设置图片比例为宽度:高度 = 12:6
plt.figure(figsize=(4, 3))

# 绘制图形
plt.plot(t_values, theta_values_deg, color='black')
plt.xlabel('Time (s)')
plt.ylabel('Theta (degrees)')
plt.title('Theta vs Time')

# 设置纵坐标范围为正负7度
plt.ylim(-7, 7)

plt.grid(True)
plt.show()
