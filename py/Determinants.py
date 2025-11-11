import numpy as np

input_matrix = []
while (one_line_matrix := input("Entering a matrix, nothing to end:")) != "":
    input_matrix.append(one_line_matrix.split())

print(f"The determinant of the matrix is: {np.linalg.det(np.array(input_matrix, dtype=float))}")