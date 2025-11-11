import numpy as np

n = int(input("Enter the dimension of the square matrix: "))
A = []
for i in range(n):
    row = input(f"Enter row {i+1} (space-separated): ").strip().split()
    if len(row) != n:
        raise ValueError("Row length must equal matrix dimension.")
    A.append([float(x) for x in row])
A = np.array(A, dtype=float)

b = []
for i in range(n):
    val = float(input(f"Enter RHS value for row {i+1}: "))
    b.append(val)
b = np.array(b, dtype=float)

try:
    A_inv = np.linalg.inv(A)
except np.linalg.LinAlgError:
    print("Matrix is singular (non-invertible). No unique solution exists.")
    exit()

x = A_inv.dot(b)

print("\nInverse matrix A⁻¹:")
print(A_inv)

print("\nSolution vector x = A⁻¹ b:")
for i, xi in enumerate(x, start=1):
    print(f"x{i} = {xi:.10g}")
