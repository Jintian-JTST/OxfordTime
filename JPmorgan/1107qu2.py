# ------------- Problem 2: Team Efficiency Sum ----------------

def getTotalEfficiency(skill):
    """
    Pair up players so that all pairs have the same total skill.
    Return the sum of (a_i * a_j) for all pairs, or -1 if impossible.
    """
    skill.sort()
    n = len(skill)
    total_sum = skill[0] + skill[-1]  # expected sum for all pairs
    total_eff = 0

    for i in range(n // 2):
        if skill[i] + skill[n - 1 - i] != total_sum:
            return -1
        total_eff += skill[i] * skill[n - 1 - i]

    return total_eff


# ---------- HackerRank-style I/O wrapper ----------
if __name__ == '__main__':
    import os
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())
    skill = list(map(int, input().rstrip().split()))

    result = getTotalEfficiency(skill)
    fptr.write(str(result) + '\n')
    fptr.close()
