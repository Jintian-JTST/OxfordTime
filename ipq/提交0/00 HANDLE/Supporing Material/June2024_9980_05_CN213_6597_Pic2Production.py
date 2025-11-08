import numpy as np
import matplotlib.pyplot as plt


I = 0.000655
F = 0.7246667
a = 5
k_values = [0, 0.05, 0.5, 1, 2, 2.5]
#==============================
def function(x,k):
    return 2 * np.pi / np.sqrt((F * (x / 100) / I)*((1 - 2 * (k * (x / 100) ** 2 / I) * (a * np.pi / 180))) / (np.exp(
                                    -2 * (k * (x / 100) ** 2 / I) * (a * np.pi / 180))))

x_values = np.linspace(0, 9, 100)
colors = ['black', 'red', 'green', 'blue', 'purple', 'orange']

for i, k_value in enumerate(k_values):
    y_values = [function(x, k_value) for x in x_values]
    plt.plot(x_values, y_values, label=f'k = {k_value}', color=colors[i])

plt.title('Effect of Different k Values on Function')
plt.xlabel('R (cm)')
plt.ylabel('T (s)')

plt.show()
