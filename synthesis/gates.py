"""

Quantum logic synthesis using stochatic synthesis
-- xiaoyao@usc.edu

"""
import enum

# Quantum Instruction Set QX
class gateType:
	def __init__(self, type, numOp):
		self.type = type
		self.numOp = numOp

class Gates(enum.Enum):
	# format:
	# (i, j) -> i: label; j: #operands
	# Initialize qubits to 0
	qubits = (1, 1)
	# Quantum gates
	h = (2, 1)
	x = (3, 1)
	y = (4, 1)
	z = (5, 1)
	rx = (6, 1)
	ry = (7, 1)
	rz = (8, 1)
	ph = (9, 1)
	t = (10, 1)
	tdag = (11, 1)
	cnot = (12, 2)
	toffoli = (13, 3)
	swap = (14, 2)
	cphase = (15, 2)
	cr = (16, 2)
	cz = (17, 2)
	cx = (18, 2)
	prepz = (19, 1)
	# Measurement 
	measure = (20, 0)
	display = (21, 0)

	@classmethod
	def oneQubit(cls):
		return [cls.h, cls.ph, cls.t, cls.x, cls.y, cls.z]
	
	@classmethod
	def univGates(cls, type):
		if (type == 1):
			# hadamard, t, and cnot gates
			return [cls.h, cls.t, cls.cnot]
		elif (type == 2):
			# gates acting on one qubit plus cnot
			one = Gates.oneQubit()
			one.append(cls.cnot)
			return one
		#elif (type == 3):
		#	return [cls.toffoli]
		elif (type == 3):
			return [cls.h, cls.toffoli]


class Operator:
	opCount = 0
	maxQbs = 7
	def __init__(self):
		self.type = 0
		self.qubits = []
		Operator.opCount += 1