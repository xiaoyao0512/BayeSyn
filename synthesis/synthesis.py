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
#import matplotlib.pyplot as plt
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


	def rewrite(self, program, index=-1):
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
		probRepOpr = 0.0
		probSwap   = 0.1
		probRepIst = 0.74
		probRmv    = 0.04#0.045
		probInsrt  = 0.04
		probRepOprs= 0.08
		
		prob = random.random() 

		if (index == -1):
			randItr = random.randint(0,len(program.qxCode)-1)
			randOp = program.qxCode[randItr]
		else:
			randItr = index
			randOp = program.qxCode[index]			
		#print 'random instr %d' %(randItr+1)
		#print gates.Gates.univGates(self.program.type2)
		if (prob <= probRepOpr):
			#print('rand instr: ', randItr)
			#print('rand qbs: ', randOp.qubits)
			#print('register: ', program.registers)
			#print 'Case 1: replace operand'
			# pick a random operand
			flag = False
			while (flag == False):
				rand1 = random.randint(0, len(randOp.qubits)-1)
				# pick a new one
				rand2 = random.randint(0,len(program.registers)-1)
				#print(index, rand1, rand2)
				if (index == -1):
					if (program.qxCode[randItr].qubits)[rand1] != program.registers[rand2]:
						flag = True
						(program.qxCode[randItr].qubits)[rand1] = program.registers[rand2]
				else:
					if (program.qxCode[index].qubits)[rand1] != program.registers[rand2]:
						flag = True
						(program.qxCode[index].qubits)[rand1] = program.registers[rand2]
				#rand2 = random.randint(0, program.numQubits-1)
				#(program.qxCode[randItr].qubits)[rand1] = rand2

			#print rand1, rand2

		elif (prob > probRepOpr and prob <= (probRepOpr+probSwap)):
			if (index == -1): 
				#print 'Case 2: Swap two instructions'
				randItr2 = random.randint(0,len(program.qxCode)-1)
				randOp2 = program.qxCode[randItr2]
				Op = gates.Operator()
				Op = randOp 
				program.qxCode[randItr] = randOp2
				program.qxCode[randItr2] = Op

		elif (prob > (probRepOpr+probSwap) and prob <= (probRepOpr+probSwap+probRepIst)):
			#print 'Case 3: replace a new instruction'
			gen = generator.Generator(program.type2, program.numQubits)
			Op = gen.generation(program.type1)
			program.registers = list(set(program.registers) | set(Op.qubits))
			if (index == -1):
				program.qxCode[randItr] = Op
			else:
				program.qxCode[index] = Op

		elif (prob > (probRepOpr+probSwap+probRepIst) and prob <= (probRepOpr+probSwap+probRepIst+probRmv)):
			#print 'Case 4: remove a random instruction'
			if (index == -1):
				program.qxCode.remove(randOp)
			else:
				program.qxCode.pop(index)

		elif (prob > (probRepOpr+probSwap+probRepIst+probRmv) and prob <= (probRepOpr+probSwap+probRepIst+probRmv+probInsrt)):
			#print 'Case 5: Insert an instruction'
			#randItr2 = random.randint(0,len(program.qxCode)-1)
			gen = generator.Generator(program.type2, program.numQubits)
			Op = gen.generation(program.type1)
			if (index == -1):
				program.qxCode.insert(randItr, Op)
			else:
				program.qxCode.insert(index, Op)

		elif (prob > (probRepOpr+probSwap+probRepIst+probRmv+probInsrt) and prob <= (probRepOpr+probSwap+probRepIst+probRmv+probInsrt+probRepOprs)):
			#print 'Case 6: replace all operands'
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
					if (index == -1):
						program.qxCode[randItr].qubits = newQubits
					else:
						program.qxCode[index].qubits = newQubits
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
		(bestCost, pairs, bestSize) = best.cost()
		costArray = []
		alphaArray = []
		print('Starting synthesis...')
		while (currErr > self.err): #iterations < self.iterations and
			newProg = copy.deepcopy(prog)
			(oldCost, oldPairs, oldSize) = prog.cost()
			self.rewrite(newProg)
			'''
			if (currErr > 2):
				self.rewrite(newProg)
			else:
				# If the error is small, use backprop to 
				# find the wrong path
				gateIndex = self.backprop(newProg, oldPairs)
				self.rewrite(newProg, gateIndex)
			
			'''
			newProg.runProgram()
			
			(newCost, newPairs, newSize) = newProg.cost()
			
			#print ('-------------------')
			#print ('OLD Program:')
			#prog.print2Screen()
			print ('OLD Cost: %f' %(oldCost))
			#print ('-------------------')
			#print ('-------------------')
			#print ('NEW Program:')
			#newProg.print2Screen()
			print ('New Cost: %f' %(newCost))
			#print ('-------------------')

			# calculate the alpha and proposal prob
			# alpha = min(1, math.exp(-self.beta*(newCost - oldCost)))
			alpha = min(1, math.exp(-self.beta*(newCost-oldCost)))
			# 8/28/2019: 
			# Potential problems with this formulus:
			# Sometimes (over 50% maybe) registers are rewrited into
			# a different totally unrelated one, causing the cost remained
			# the same for the new and old programs. In this way, 
			# alpha is always 1 and we are always accepting the new proposal.
			# Is it really good? 
			print(iterations, alpha)
			#alphaArray.append(alpha)
			rnd = random.random()
			if (rnd < alpha):
				# accept the proposal
				# otherwise, reject it
				#print 'Accepting the new proposal...'
				if (newCost != oldCost):
					prog = newProg
					oldCost = newCost
				elif (rnd < 0.05):
					prog = newProg
					oldCost = newCost						
				#prog.print2Screen()
			print('Best Cost: ', bestCost)
			if (oldCost < bestCost):
				# update the best program
				#print 'Updating the best program...'
				best = prog
				bestCost = oldCost
			iterations += 1
			currErr = bestCost
			#costArray.append(currErr)
			#print '-------------------'
			#print 'BEST Program:'
			#best.print2Screen()
			#print '-------------------'
			#print 'Error = %d' %(currErr)
			#break
		
		best.cost()	
		self.program = best
		#plt.plot(costArray)
		#plt.show()
		#file = open('alpha.txt', 'w')
		#for alpha in alphaArray:
		#	file.write("%f" %(alpha))
		#file.close()
		#print '-------------------'
		#print '-------------------'
		#self.backprop(prog, [2,3])

	def backprop(self, prog, output):
		# sometimes it is hard to get 100% correct answers
		# by stochastic synthesis. Therefore, we propose a
		# feedback directed approach to backpropogate the 
		# error and rewrite (RWT) some quantum gates along the 
		# wrong path.
		# OUTPUT: the gate which needs to be rewrited
		#print '---------------------'
		wrongPath = []
		for i in range(len(prog.qxCode)-1, -1, -1):
			length = len(prog.qxCode[i].qubits)
			for qb in range(length):
				#print '-----------------'
				#print output
				for o in output:
					if (prog.qxCode[i].qubits[qb] == o and qb != length-1):
						wrongPath.append(i)
					elif (prog.qxCode[i].qubits[qb] == o and qb == length-1):
						wrongPath.append(i)
						output.extend(prog.qxCode[i].qubits[0:length-1])
						output = list(set(output))
		# remove duplicates
		wrongPath = list(set(wrongPath))
		#print "wrong path: ", wrongPath
		return wrongPath[random.randint(0,len(wrongPath)-1)]