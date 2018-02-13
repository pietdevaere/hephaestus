#!/usr/bin/python3
import matplotlib.pyplot as plt
import pickle
import sys

class Time:
	zeroTime = None

	def __init__(self, epoch):
		self.epoch = float(epoch)

	def __float__(self):
		if Time.zeroTime:
			return float(self.epoch - Time.zeroTime)
		else:
			return float(self.epoch)

	def __repr__(self):
		return str(float(self))

	def __eq__(self, other):
		if other == None:
			return False
		return float(self) == float(other)

	def __lt__(self, other):
		return float(self) < float(other)

file_path = sys.argv[1]
figure = pickle.load(open(file_path, 'rb'))

plt.show(block=True)
