"""

Quantum logic synthesis using stochatic synthesis
-- xiaoyao@usc.edu

"""

import gates
import random

class Generator:
	def __init__(self, type, totalBits):
		# type chooses which universal set should be used
		# We use 1
		self.type = type
		self.totalBits = totalBits

	def random(self):
		Op = gates.Operator()
		universal = gates.Gates.univGates(self.type)
		#print universal
		idx = random.randint(0, len(universal)-1)
		gate = universal[idx].value
		#print universal[idx]
		#print gate
		Op.type = universal[idx]#gate.type
		valid = False
		# make sure that qubits are different
		while not valid:
			if (gate[1] == 1):
				Op.qubits = [random.randint(0, self.totalBits-1)]
			elif (gate[1] == 2):
				q1 = random.randint(0, self.totalBits-1)
				q2 = random.randint(0, self.totalBits-1) # gates.Operator.maxQbs
				if (q1 == q2):
					continue
				Op.qubits = [q1, q2]
			elif (gate[1] == 3):
				q1 = random.randint(0, self.totalBits-1)
				q2 = random.randint(0, self.totalBits-1)
				q3 = random.randint(0, self.totalBits-1)
				if (q1 == q2) or (q1 == q3) or (q2 == q3):
					continue 
				Op.qubits = [q1, q2, q3]
			else:
				sys.exit('ERROR!')
			valid = True
		return Op

	def generation(self, type):
		if (type == 1):
			return self.random()