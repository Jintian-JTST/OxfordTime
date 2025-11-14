import random
import matplotlib.pyplot as plt
import numpy as np

N = 1000
trials = 500
sum_r2 = [0] * (N + 1)

for t in range(trials):
    x, y = [0], [0]
    for i in range(N):
        step = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        x.append(x[-1] + step[0])
        y.append(y[-1] + step[1])
    for i in range(N + 1):
        sum_r2[i] += x[i]**2 + y[i]**2

mean_r2 = [s / trials for s in sum_r2]

theoretical = list(range(N + 1))

# 画图
plt.figure(figsize=(8,5))
plt.plot(mean_r2, label='Simulation')
plt.plot(theoretical, '--', label='Theory ⟨r²⟩ = n')
plt.xlabel('Step number n')
plt.ylabel('Mean square displacement ⟨r²⟩')
plt.title('2D Random Walk: Mean Square Displacement')
plt.legend()
plt.savefig('random_walk.png')
