import numpy as np

# =======First 4

k = 0.5
I = 0.000655
F = 0.7246667
a = 5

data = np.array([
    [3.13, 1.050],
    [2.41, 1.269],
    [1.50, 1.537],
    [1.05, 1.863]
])

def function1(x):
    return 2 * np.pi / np.sqrt((F * (x / 100) / I)*
                               ((1 - 
                                2 * (k * (x / 100) ** 2 / I) * 
                                (a * np.pi / 180))) / 
                                
                                (np.exp(
                                    -2 * (k * (x / 100) ** 2 / I) * (a * np.pi / 180)))
                                )

def function2(x):
    return 4 * np.pi / np.sqrt(4 * (F * (x / 100) / I) - (k * (x / 100) ** 2 / I) ** 2)

predicted_values1 = np.array([function1(x) for x in data[:, 0]])
predicted_values2 = np.array([function2(x) for x in data[:, 0]])
residuals1 = data[:, 1] - predicted_values1
residuals2 = data[:, 1] - predicted_values2

variance1 = np.var(residuals1)
variance2 = np.var(residuals2)

print("Variance of squared model:", variance1)
print("Varience of proportional model:", variance2)
