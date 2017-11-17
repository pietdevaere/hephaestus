#!/usr/bin/python3
import matplotlib.pyplot as plt
import pickle
import sys

file_path = sys.argv[1]
figure = pickle.load(open(file_path, 'rb'))

plt.show(block=True)
