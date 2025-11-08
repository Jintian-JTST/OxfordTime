import numpy as np
import matplotlib.pyplot as plt

C = 0.088
k = 16.0e-3
I = 0.070e-3
m = 36.0e-3
V = 5.00e-6
R = 25.7e-3
F = 0.30411

r1 = k * R**2 / I
r2 = F * R / I

# def
def theta(t):
    return C * np.exp(-r1 / 2 * t) * np.cos(np.sqrt(4 * r2 - r1**2) / 2 * t)


t_values = np.linspace(0, 5, 1000)
theta_values = theta(t_values)

theta_values_deg = np.degrees(theta_values)
plt.figure(figsize=(4, 3))
plt.plot(t_values, theta_values_deg, color='black')
plt.xlabel('Time (s)')
plt.ylabel('Theta (degrees)')
plt.title('Theta vs Time')

plt.ylim(-7, 7)

plt.grid(True)
plt.show()
