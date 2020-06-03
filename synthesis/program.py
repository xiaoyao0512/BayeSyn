"""

Quantum logic synthesis using stochatic synthesis
-- xiaoyao@usc.edu

"""

import generator
import gates
import sys
import os
import random
from subprocess import check_output
import re

# states for a quantum circuit:
# input-output examples
class State:
	def __init__(self):
		self.input = []
		self.output = 0

class Program:
	def __init__(self, type1, type2, type3, type4, numArgs, inBits, outBits, length, cktName, appName, times1, times2, numAncilla, numQubits):
		# type chooses which generation method is used
		# we use 1 (random)
		# type1: randomly generate gates
		# type2: which gate set to choose
		# type3: (1) randomly generate input-output/states
		#        (2) Hedamard gates Hxn
		# type4: choose an input set
		self.type1 = type1
		self.type2 = type2
		self.type3 = type3
		self.type4 = type4
		self.numArgs = numArgs
		# keep track of the number of bits required 
		# for inputs and output
		# for example, 3bit adder: inBits=[3,3], outBits=4
		self.inBits = inBits
		self.outBits = outBits
		# the number of generated quamtum instructions
		self.length = length
		# The difference betwwen instructions and qxCode
		# qxCode only contain logic part,
		# which is the same for different inputs
		# list instructions is the placeholder for the current
		# input + logic gates
		self.instructions = []
		self.qxCode = []
		# circuit name and application name
		# applications are expected to be written in C
		self.cktName = cktName
		self.appName = appName
		# indicate the file to be running is up2date
		self.printFile = False
		# store input-output examples from the app
		# a list of states
		self.states = []
		# store golden results from Q Code
		self.golden = []
		# times1: #input-output pairs from apps
		# times2: #times to run the Q circuit
		self.times1 = times1
		self.times2 = times2
		# the number of required ancilla qubits
		self.numAncilla = numAncilla
		# the number of input qubits
		# numQubits = ancilla + inbits
		self.numQubits = numQubits
		# this is used to keep track of live registers
		self.registers = []
		self.file = 0

	def compile(self):
		os.system('gcc %s' % (self.appName))

	def genStates(self):
		self.compile()
		if (self.type4 == 1):
			# randomly generate input-output examples
			for i in range(self.times1):
				args = []
				state = State()
				for i in range(self.numArgs):
					num = 2**self.inBits[i]#((gates.Operator.maxQbs-self.numAncilla)/self.numArgs)
					args.append(random.randint(0, num-1))
				results = check_output('./a.out %s' % (' '.join(map(str, args))), shell=True)
				#print args
				#print('lol')
				#print(float(results))
				state.input = args
				state.output = float(results)
				self.states.append(state)
		elif (self.type4 == 2):
			# If input size is not large, generate a full set of inputs
			if (self.numArgs == 2):
				for i in range(2**self.inBits[0]):
					for j in range(2**self.inBits[1]):
						state = State()
						args = [i, j]
						#print args
						results = check_output('./a.out %s' % (' '.join(map(str, args))), shell=True)
						#print(results)
						state.input = [i, j]
						state.output = float(results)
						self.states.append(state)
			else: 
				sys.exit('ERROR! Does not support such numArgs.\n')
		else:
			sys.exit('ERROR! You should specify type3. Now we only support random generation (type3=1)\n')

	def genGates(self):
		# generate one quantum instruction/operator/gate 
		# randomly (type1=1) w/o initialization and measurement
		# type2 chooses a gate set to use
		self.golden = []
		self.registers = []
		total = self.numAncilla
		for num in self.inBits:
			total += num
		gen = generator.Generator(self.type2, total)
		for i in range(self.length):
			Op = gen.generation(self.type1)
			self.registers = list(set(self.registers) | set(Op.qubits))
			self.qxCode.append(Op)

	def initialization(self, input):
		# generate quantum input circuits / initialization
		# input: a list of numbers
		# make sure file is not up2date
		self.printFile = False
		Op = gates.Operator()
		Op.type = gates.Gates.qubits
		assert len(self.instructions) == 0, 'It has old instructions.'
		self.instructions.append(Op)
		qb_idx = 0
		#num = (gates.Operator.maxQbs-self.numAncilla)/self.numArgs
		if (self.type3 == 1):
			# apply X to appropriate input gates
			# to initialize to 1 instead of 0
			for argIndex in range(len(input)):
				#print bin(arg)[2:]
				#x = bin(arg)[2:]
				#print arg
				#print x
				#print '---------------'
				#while arg != 0:
				arg = input[argIndex]
				num = self.inBits[argIndex]
				for i in range(num):
					bit = arg & 0b1
					#print bit
					if bit == 1:
						# apply X gate
						Op = gates.Operator()
						Op.type = gates.Gates.x
						Op.qubits.append(qb_idx)
						self.instructions.append(Op)
					arg >>= 1
					qb_idx += 1
				#print '******************'
			# input circuits:
			# first bit in input[0] -----
			# second bit in input[0] -----
			# ...
			# first bit in input[1] -----
			# second bit in input[1] -----
		elif (self.type3 == 2):
			# apply hedamard gates instead of in-out examples
			qb_idx = 0
			for arg in input:
				Op = gates.Operator()
				Op.type = gates.Gates.h
				Op.qubits.append(qb_idx)
				self.instructions.append(Op)
				qb_idx += 1			

	def measurement(self):
		# measure partial qubits
		# only works in single-output quantum circuit
		for i in range(self.outBits):
			Op = gates.Operator()
			Op.type = gates.Gates.measure
			Op.qubits.append(i)
			self.instructions.append(Op)

	def genQXCode(self, input):
		# include initialization & measurement
		self.initialization(input)
		self.genGates()
		self.measurement()

	def print2File(self):
		assert self.printFile == False, 'File is incorrect.'
		file = open(self.cktName, "w")
		Op = self.instructions.pop(0)
		#$file.write("%s %d\n" % (Op.type.name, gates.Operator.maxQbs))
		# instead of using maximum number of qubits,
		# we should use input bits + ancilla
		total = self.numAncilla
		for num in self.inBits:
			total += num
		file.write("%s %d\n" % (Op.type.name, total))#gates.Operator.maxQbs))
		for i in self.instructions:
			file.write("%s " % (i.type.name))
			for qb_idx in range(len(i.qubits)):
				if (qb_idx == len(i.qubits) - 1):
					file.write("q%d" % (i.qubits[qb_idx]))
				else:
					file.write("q%d, " % (i.qubits[qb_idx])) 
			file.write("\n")
		file.write("\ndisplay\n")
		file.close()
		self.printFile = True
		#os.system('cat %s' %(self.cktName))

	def print2Screen(self):
		file = open(self.cktName, "w")
		for i in self.qxCode:
			file.write("%s " % (i.type.name))
			for qb_idx in range(len(i.qubits)):
				if (qb_idx == len(i.qubits) - 1):
					file.write("q%d\t" % (i.qubits[qb_idx]))
				else:
					file.write("q%d, " % (i.qubits[qb_idx])) 
			for qb_idx in range(len(i.qubits)):
				if (qb_idx == len(i.qubits) - 1):
					file.write("%d" % (i.qubits[qb_idx]))
				else:
					file.write("%d, " % (i.qubits[qb_idx])) 			

			file.write("\n")
		file.write("\ndisplay\n")
		file.close()
		os.system('cat %s' %(self.cktName))

	def prepBeforeRun(self):
		# prepare qxcode and states before runnning the code
		self.genStates()
		#print self.states[2].input
		self.genGates()

	def runProgram(self):
		#os.system('rm temp 2> /dev/null') # first delete the file
		assert len(self.qxCode) != 0
		assert len(self.states) != 0
		# before running the program, clear golden results left.
		self.golden = []
		#print "numStates = ", len(self.states)
		for state in self.states:
			#pass
			# make sure we have the new Quantum circuit
			# run several times (times2) to generate results
			# times1 is the number of states in self.states

			# for each state, we will have different initialization
			# meaning different input patterns driven into quantum circuits (qxCode)
			self.initialization(state.input)
			self.instructions.extend(self.qxCode)
			self.measurement()
			self.print2File()
			if not self.printFile:
				sys.exit('ERROR! File is not up-to-date!')
			else:
				# run it using QX simulator many times
				# store results into a file called "temp"	
				# print(self.times2)
				for i in range(self.times2):	
					command = ['./qx-simulator-old', self.cktName]
					self.file = check_output(command)
				# have to clear this list
				# otherwise, instructions will be accumulated
				# print(self.file)
				self.instructions = []
				#print state
				self.storeResults()
		assert len(self.states) == len(self.golden), 'Ops, something\'s wrong'

	def storeResults(self):
		# read golden results from temp (Q.C.)
		lines = 0
		value = 0
		self.file = str(self.file, 'utf-8')
		#print(self.file)
		for line in self.file.split('\n'):
			# regex to extract measurement outcome
			regexp = re.compile(r'measurement register')
			if regexp.search(line):
				# now we find the outcome
				# store it into self.golden 
				#print line
				lst = line.split('|')
				#print lst
				result = ("".join(lst[len(lst)-1-self.outBits:len(lst)-1])).replace(" ", "")
				#print("result = ", result)
				#print "len = ", len(lst[len(lst)-1-self.outBits:len(lst)-1])
				#print "int = ", int(result, 2)
				lines += 1
				value += int(result, 2)
				if (lines % self.times2 == 0):
					self.golden.append(value / self.times2)
					value = 0

		#print self.golden
		#fp.close()
		#os.system('rm temp')
		#print len(self.golden)

	def cost(self):
		assert len(self.states) == len(self.golden), 'Ops, you have to run the program.'
		assert len(self.golden) != 0
		assert len(self.states) != 0
		diff = 0
		size = len(self.golden)
		sze = 0
		pairs = []
		for idx in range(size):
			#print self.states[idx]
			#print type(self.states[idx].output)
			cst = self.states[idx].output - self.golden[idx]
			diff += abs(cst)
			if (cst != 0):
				#print "Failed testcases: ", self.states[idx].input
				#print "results: ", self.states[idx].output, ", expected: ", self.golden[idx]
				sze += 1
				n1 = int(self.golden[idx])
				n2 = int(self.states[idx].output)
				for i in range(self.outBits):
					x = n1 & 1
					y = n2 & 1
					if (x != y):
						pairs.append(i)
					n1 = n1 >> 1
					n2 = n2 >> 1
		#print diff, ": There are %d number of failed testcases." %(sze)
		return (diff, list(set(pairs)), sze)