import numpy as np

def read_matrix_from_input():
    print("Enter rows; each row elements separated by spaces. End input with an empty line.")
    rows = []
    while True:
        line = input().strip()
        if line == "":
            break
        rows.append([float(x) for x in line.split()])
    return np.array(rows, dtype=float)

if __name__ == "__main__":
    A = read_matrix_from_input()
    if A.size == 0:
        print("No input.")
    else:
        if A.shape[0] != A.shape[1]:
            print("Matrix must be square.")
        else:
            det = np.linalg.det(A)
            if abs(det) < 1e-12:
                print("Matrix is singular (det ~ 0).")
            else:
                Ainv = np.linalg.inv(A)
                print("Inverse matrix:")
                np.set_printoptions(precision=6, suppress=True)
                print(Ainv)
                print(f"Determinant: {det}")