import pandas as pd

with open('y1990.dat', 'r') as f:
    lines = f.readlines()
    data = [line.strip().split() for line in lines]

print(data[0])
print(len(data[0]))
print(data[1])
print(len(data[1]))