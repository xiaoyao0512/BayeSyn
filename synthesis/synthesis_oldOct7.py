"""

Quantum logic synthesis using stochatic synthesis
-- xiaoyao@usc.edu

"""

# import libraries
import random
import generator
import gates
import program
import copy
import math
import matplotlib.pyplot as plt
import sys
# synthesis class
class Synthesis:
	def __init__(self, cktLen, beta, cost, program, iterations, err):
		self.cktLen = cktLen
		self.beta   = beta
		self.cost   = cost
		self.program = program
		self.iterations = iterations
		self.err = err


	def rewrite(self, program):
		# Rewrite rules:
		# 1. Replace operand (0.817):
		#	Replace a random instruction input register
		#   with a new one
		# 2. Replace opcode (0.092):
		#    Replace a random instruction opcode with 
		#    a new one
		# 3. Replace instruction (0.045):
		#    Replace a entire random instruction with 
		#    a new one
		# 4. Swap all operands (0.045):
		#    Randomly select two qubits and 
		#    swap them if possible in the program
		# 5. Random Restart (0.001):
		#    Replace the entire program with a new one
		# (TBD) 6. Swap operand (0.00):
		#    Randomly select an instruction and 
		#    swap operands if possible
		probRepOpr = 0.5
		probRepOprs= 0.15
		probSwap   = 0.15
		probRepIst = 0.1
		probRmv    = 0.05#0.045
		probInsrt  = 0.05
		
		prob = random.random() 
		randItr = random.randint(0,len(program.qxCode)-1)
		randOp = program.qxCode[randItr]
		print 'random instr %d' %(randItr+1)
		#print gates.Gates.univGates(self.program.type2)
		if (prob <= probRepOpr):
			#print randItr
			#print randOp.qubits
			print 'Case 1: replace operand'
			# pick a random operand
			flag = False
			while (flag == False):
				rand1 = random.randint(0, len(randOp.qubits)-1)
				# pick a new one
				rand2 = random.randint(0,len(program.registers)-1)
				if (program.qxCode[randItr].qubits)[rand1] != program.registers[rand2]:
					flag = True
					(program.qxCode[randItr].qubits)[rand1] = program.registers[rand2]
				#rand2 = random.randint(0, program.numQubits-1)
				#(program.qxCode[randItr].qubits)[rand1] = rand2

			print rand1, rand2

		elif (prob > probRepOpr and prob <= (probRepOpr+probSwap)):
			print 'Case 2: Swap two instructions'
			randItr2 = random.randint(0,len(program.qxCode)-1)
			randOp2 = program.qxCode[randItr2]
			Op = gates.Operator()
			Op = randOp 
			program.qxCode[randItr] = randOp2
			program.qxCode[randItr2] = Op

		elif (prob > (probRepOpr+probSwap) and prob <= (probRepOpr+probSwap+probRepIst)):
			print 'Case 3: replace a new instruction'
			gen = generator.Generator(program.type2, program.numQubits)
			Op = gen.generation(program.type1)
			program.registers = list(set(program.registers) | set(Op.qubits))
			program.qxCode[randItr] = Op

		elif (prob > (probRepOpr+probSwap+probRepIst) and prob <= (probRepOpr+probSwap+probRepIst+probRmv)):
			print 'Case 4: remove a random instruction'
			program.qxCode.remove(randOp)

		elif (prob > (probRepOpr+probSwap+probRepIst+probRmv) and prob <= (probRepOpr+probSwap+probRepIst+probRmv+probInsrt)):
			print 'Case 5: Insert an instruction'
			#randItr2 = random.randint(0,len(program.qxCode)-1)
			gen = generator.Generator(program.type2, program.numQubits)
			Op = gen.generation(program.type1)
			program.qxCode.insert(randItr, Op)

		elif ( prob > (probRepOpr+probSwap+probRepIst+probRmv+probInsrt) and prob <= (probRepOpr+probSwap+probRepIst+probRmv+probInsrt+probRepOprs)):
			print 'Case 6: replace all operands'
			# pick a new opcode
			newQubits = []
			flag = False
			# check no duplicates; If no, start over
			while (flag == False):
				for i in program.qxCode[randItr].qubits:
					rand2 = random.randint(0,len(program.registers)-1)
					newQubits.append(program.registers[rand2])
				if (len(set(newQubits)) == len(newQubits)):
					flag = True
					program.qxCode[randItr].qubits = newQubits
				else:
					newQubits = []
		else:
			sys.exit('ERROR! You shouldn\'t reach here.\n')

	def synthesize(self):
		# P <- random program of length I
		# B <- P // Initialize the best program
		# while compute budget not exhausted do
		#     R  <- random rewrite rule
		#     P' <- R(P)
		#     alpha <- min(1, exp(-beta(C(P')-C(P))))
		#     if random_number(0,1) < alpha then
		#         P <- P' // Accept proposal
		#     else 
		#         pass    // Reject proposal
		#     endif
		#     if C(P) < C(B) then
		#         B <- P // Update the best program
		#     endif
		# endwhile
		# return B
		prog = self.program # random program generated already
		best = copy.deepcopy(prog)
		currErr = 10**31
		iterations = 0
		bestCost = best.cost()
		costArray = []
		alphaArray = []
		while (currErr > self.err): #iterations < self.iterations and
			newProg = copy.deepcopy(prog)
			self.rewrite(newProg)
			newProg.runProgram()

			oldCost = prog.cost()
			newCost = newProg.cost()
			
			print '-------------------'
			print 'OLD Program:'
			prog.print2Screen()
			print 'OLD Cost: %f' %(oldCost)
			print '-------------------'
			print '-------------------'
			print 'NEW Program:'
			newProg.print2Screen()
			print 'New Cost: %f' %(newCost)
			print '-------------------'

			# calculate the alpha and proposal prob
			# alpha = min(1, math.exp(-self.beta*(newCost - oldCost)))
			alpha = min(1, math.exp(-self.beta*(newCost / oldCost)))
			# 8/28/2019: 
			# Potential problems with this formulus:
			# Sometimes (over 50% maybe) registers are rewrited into
			# a different totally unrelated one, causing the cost remained
			# the same for the new and old programs. In this way, 
			# alpha is always 1 and we are always accepting the new proposal.
			# Is it really good? 
			print iterations, alpha
			#alphaArray.append(alpha)
			if (random.random() < alpha):
				# accept the proposal
				# otherwise, reject it
				print 'Accepting the new proposal...'
				prog = newProg
				oldCost = newCost
			if (oldCost < bestCost):
				# update the best program
				print 'Updating the best program...'
				best = prog
				bestCost = oldCost
			iterations += 1
			currErr = bestCost
			costArray.append(currErr)
			print '-------------------'
			print 'BEST Program:'
			best.print2Screen()
			print '-------------------'
			print 'Error = %f' %(currErr)
		
		best.cost()	
		self.program = best
		plt.plot(costArray)
		plt.show()
		#file = open('alpha.txt', 'w')
		#for alpha in alphaArray:
		#	file.write("%f" %(alpha))
		#file.close()