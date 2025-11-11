# pure_python_inverse.py
from typing import List

def minor(matrix: List[List[float]], i: int, j: int) -> List[List[float]]:
    return [row[:j] + row[j+1:] for r_idx, row in enumerate(matrix) if r_idx != i]

def determinant(matrix: List[List[float]]) -> float:
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square.")
    det = 0.0
    for c in range(n):
        det += ((-1) ** c) * matrix[0][c] * determinant(minor(matrix, 0, c))
    return det

def cofactor_matrix(matrix: List[List[float]]) -> List[List[float]]:
    n = len(matrix)
    cof = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            m = determinant(minor(matrix, i, j))
            cof[i][j] = ((-1) ** (i + j)) * m
    return cof

def transpose(matrix: List[List[float]]) -> List[List[float]]:
    n = len(matrix)
    return [[matrix[j][i] for j in range(n)] for i in range(n)]

def inverse_matrix(matrix: List[List[float]]) -> List[List[float]]:
    det = determinant(matrix)
    if abs(det) < 1e-12:
        raise ValueError("Matrix is singular (det ~ 0).")
    adj = transpose(cofactor_matrix(matrix))
    n = len(matrix)
    return [[adj[i][j] / det for j in range(n)] for i in range(n)]



print("Enter rows; each row elements separated by spaces. End input with an empty line.")
matrix: List[List[float]] = []
while True:
    line = input().strip()
    if line == "":
        break
    row = [float(x) for x in line.split()]
    matrix.append(row)

if not matrix:
    print("No input.")
else:
    if any(len(row) != len(matrix) for row in matrix):
        print("Not a square matrix.")
    else:
        inv = inverse_matrix(matrix)
        print("Inverse matrix:")
        for r in inv:
            print(" ".join(f"{val:.6g}" for val in r))
