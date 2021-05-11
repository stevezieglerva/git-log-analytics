import heapq


class TopX():
	"""
	Class that maintains the top N values in an array. Tuples can used to maintain the a list of top word frequencies (Ex: (5743, "the") and (473, "is")).
	"""
	def __init__(self, topn):
		self.__topn = topn
		self.values = []

	def add(self, item):
		self.values.append(item)
		self.values = heapq.nlargest(self.__topn, self.values )


	
