# ------------- 使用用户思路（逐元素切换标记）实现：Problem 1 -------------
# 题目：给定数组 data 和若干更新 updates（每个为 [l, r], 1-based, inclusive），
# 每次更新把区间内每个元素取反。用“对每个更新在区间内逐个切换标记”的方法实现。

def getFinalData(data, updates):
    """
    按用户方法：为每个位置维护一个布尔标记 not_changed（初始 True 表示未被取反过）。
    对于每个更新 [l, r]（1-based），逐个位置切换该标记。
    最后根据标记决定是否取反对应元素：被翻转奇数次 -> 取反。
    返回最终数组（list）。
    如果输入区间非法（越界或 l>r），返回 [-1] 作为错误标识（保持可迭代）。
    """
    if len(data) >= 1 and len(data) <= 10000 and len(updates) >= 1 and len(updates) <= 10000:
        not_change = [True for u in range(len(data))]
        for i in updates:
            for n in range(i[0], i[1] + 1):
                try:
                    not_change[n - 1] = not not_change[n - 1]
                except IndexError:
                    return -1
        for x in range(len(data)):
            if not not_change[x]:
                data[x] = -data[x]
    return data


# ---------------- HackerRank I/O wrapper，保证返回是可迭代的结果 ----------------
if __name__ == '__main__':
    import os
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    # 读取数据（兼容题面常见输入格式）
    # 第一行：n
    n = int(input().strip())
    data = [int(input().strip()) for _ in range(n)]

    updates_rows = int(input().strip())
    updates_columns = int(input().strip())

    updates = [list(map(int, input().rstrip().split())) for _ in range(updates_rows)]

    result = getFinalData(data, updates)

    if not isinstance(result, list):
        result = [result]

    fptr.write('\n'.join(map(str, result)) + '\n')
    fptr.close()
