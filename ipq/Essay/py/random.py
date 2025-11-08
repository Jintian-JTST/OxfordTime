import numpy as np
a=1
def generate_random_values(a):
    # 生成b个随机值，误差不超过a的5%
    values = np.random.uniform(0.95 * a, 1.05 * a, 3)

    values[-1] = a*3-values[0]-values[1]

    return values
while a!= 0:
    # 输入a和b的值
    a = float(input("请输入a的值："))
    # 生成随机值
    random_values = generate_random_values(a)

    # 输出生成的随机值1.863

    print("生成的随机值：", random_values)
    print("平均数：", np.mean(random_values))
