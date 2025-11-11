import math
import numpy as np

def normalise(v:list[float]) -> list[float]:
    norm = np.sqrt(sum(i**2 for i in v))
    if norm == 0:
        raise ValueError("Cannot normalise the zero vector.")
    return [i / norm for i in v]

def dot(u:list[float], v:list[float]) -> list[float]:
    if len(u) == len(v):
        sum = 0
        for i in range(len(u)):
            sum+=u[i]*v[i]
        return sum
    raise ValueError("Vectors must be of the same dimension.")

def minus(u:list[float], v:list[float]) -> list[float]:
    if len(u) == len(v):
        return [u[i]-v[i] for i in range(len(u))]
    raise ValueError("Vectors must be of the same dimension.")

def scale(v:list[float], scalar:float) -> list[float]:
    return [scalar * i for i in v]

vec1 = [float(x) for x in input("Enter the 1st vector (space-separated values): ").split()]
vec2 = [float(x) for x in input("Enter the 2nd vector (space-separated values): ").split()]
vec3 = [float(x) for x in input("Enter the 3rd vector (space-separated values): ").split()]
if len(vec1) != len(vec2) or len(vec1) != len(vec3):
    raise ValueError("All vectors must have the same dimension.")

print('e1 =', normalise(vec1))
print('e2 =', normalise(minus(vec2, scale(normalise(vec1), dot(vec2, normalise(vec1))))))
print('e3 =', 
      normalise(
          minus(
              minus(
                    vec3, 
                    scale(normalise(vec1), dot(vec3, normalise(vec1)))
              ),
              scale(normalise(vec2),
                    dot(vec3,normalise(vec2))
    ))))

