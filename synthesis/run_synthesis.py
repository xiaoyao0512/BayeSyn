"""

Quantum logic synthesis using stochatic synthesis
-- xiaoyao@usc.edu

"""
import program
import synthesis
import time
from bayes_opt import BayesianOptimization


def black_box_function(beta):
	syn.beta = beta
	startTime = time.time()
	syn.synthesize()
	endTime = time.time()
	return endTime - startTime

def BO_wrapper():
	# Bounded region of parameter space
	pbounds = {'beta': (1, 5)}

	optimizer = BayesianOptimization(
	    f=black_box_function,
	    pbounds=pbounds,
	    random_state=1,
	)

	optimizer.maximize(
	    init_points=5,
	    n_iter=7,
	)

	print(optimizer.max)

# main function
def main(BO_flag=0):
	cktLen = 10
	prog = program.Program(
		type1=1, 
		type2=3, 
		type3=1, 
		type4=2,
		numArgs=2, 
		length=cktLen, 
		inBits=[1, 1],
		outBits=2,
		cktName="test.qc", 
		appName="adder.c", 
		times1=3,
		times2=5,
		numAncilla=1,
		numQubits=3
		)
	prog.prepBeforeRun()
	#print('2222')
	prog.runProgram()
	#print('3333')
	#prog.genStates()
	#prog.storeResults()
	#print len(prog.qxCode)
	#print prog.instructions
	global syn
	syn = synthesis.Synthesis(
			cktLen=cktLen,
			beta=3, #2
			cost=100, 
			program=prog,
			iterations=50000,
			err=0.1
		)
	# If you want to use BO to automatically 
	# find the beta, turn on the flag;
	# But it is very time-consuming.
	# If you want to just take a glimpse at the results,
	# turn off the flag and it only runs synthesis once.
	if (BO_flag):
		BO_wrapper()	
	else:
		syn.synthesize()

if __name__ == '__main__':
	main(BO_flag=0)
