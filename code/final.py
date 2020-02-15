import sys
import numpy as np
from os import system
from itertools import chain, combinations

#file input and petrinet dot file generation
def get_input():
	#Code to process the input file and return a list list
	file = open(sys.argv[1], "r")
	data = iter(file.read().split())
	out = open("petrinet.dot", 'w')
	out.write("digraph M {\nrankdir = LR;\n")
	#number of places and tranistion
	place = int(next(data))
	transition = int(next(data))
	for i in range(transition):
		out.write("t" + str(i+1) + "[shape=box]\n")
				
	#create input matrix
	TP = np.zeros((transition, place), dtype=np.int)
	PT = np.zeros((place, transition), dtype=np.int)
	
	while True:
		try:
			a = next(data)
			b = next(data)
			out.write(a + "->" + b + "\n")
			if a[0] == 'p' or a[0] == 'P':
				PT[int(a[1]) - 1,int(b[1]) - 1] = int(1)
			elif a[0] == 't' or a[0] == 'T':
				TP[int(a[1]) - 1,int(b[1]) - 1] = int(1)
			else:
				pass
		except StopIteration:
			break
	out.close()
	return place, transition, TP, PT

#token input
def get_token(place):
	out = open("petrinet.dot", 'a')
	token_input = raw_input("Please enter token position in form of places separated by space: ")
	print "Token position:", token_input
	token = [0] * place
	data = iter(token_input.split())
	while True:
		try:
			a = next(data)
			out.write(a + '[color="#FF0000", style=filled]\n')
			token[int(a[1]) - 1] = int(a[1])
		except StopIteration:
			break
	out.write("}")
	out.close()
	return token

#to get all combination of token position
def powerset_generator(i):
	new =  np.setdiff1d(i, [0])
	powerset = set();
	for subset in chain.from_iterable(combinations(new, r) for r in range(len(new)+1)):
		if len(subset) > 0 :
			powerset.add(subset)
	return powerset

#to get enabled transition
def enabled(token, TP, PT):
	tokenset = np.array([token])
	enabledtran = [[]]
	post = []
	tran = PT[0].size
	place = TP[0].size
	for i in powerset_generator(token):	#get all token position combination
		pre = [0] * tran
		for j in i:
			#all transition from place j-1
			k = PT[j - 1]
			#for each transition
			for count in range(tran):
				flag = 1
				if(k[count] == 1):
					#for all preplace
					for check in range(place):
						#if any pre-place is empty
						if PT[check][count] == 1 and (check + 1) not in i:
							flag = 0
							break
					#if all pre-place is covered
					if flag == 1:
						pre[count] = 1
		for j in range(tran):
			if pre[j] == 1:
				flag = 1;
				for k in range(place):
					#if no transition
					if(TP[j][k] == 0):
						pass
					#if valid post place transition
					elif(TP[j][k] == 1 and token[k] == 0):
						pass
					#if transition to self state
					elif(TP[j][k] == 1 and token[k] != 0 and PT[k][j] == 1):
						pass
					else:
						#tranistion not enabled
						flag = 0
						break
				if flag == 1:
					if int(j+1) not in post:
						post.append(int(j + 1))
	return post

#firing of tranisition to get new token state
def fire(token, tran, TP, PT):
	newtoken = [0] * len(token)
	for i in range(len(token)):
		if(token[i] != 0):
			flag = 1
			if PT[i][tran-1] == 1:
				for k in range(len(token)):
					if TP[tran-1][k] == 1:
						flag = 0
						newtoken[k] = k+1
			if flag == 1:
				newtoken[i] = i + 1
	return newtoken

def statespace_generation(TP, PT, place):
	states = []
	for i in range(place):
		states.append(i+1)
	print "statespace:"
	output = [[], [[-1]], []];
	single = [[]]
	for i in powerset_generator(states):
		work = []
		newwork = [0] * place
		for  j in i:
				newwork[j - 1] = j
		if newwork not in output[0]:
			output[0].append(newwork)
			single.append(newwork)
			work.append(newwork)
			while len(work):
			#take first node..
				first, work = work[0], work[1:]
				enabledtran = enabled(first, TP,PT)
				if len(enabledtran) == 0:
					single.append(first)
				for tran in enabledtran:
					if newwork in single:
						single.remove(newwork)
					newtoken = fire(first, tran, TP,PT)
					if newtoken not in output[0]:
						output[0].append(newtoken)
						work.append(newtoken)
					output[1].append([first, tran, newtoken])
	single.remove([])
	output.append(single)
	return output
	#output format: nodes processed, edges (source, transition, sink), inital token

def reachability_generation(TP,PT, place):
	token = get_token(place)
	#output format: nodes processed, edges (source, transition, sink), inital token
	output = [[token], [[-1]], [token]];
	# nodes to be processed
	work = [token]
	while len(work):
		#take first node..
		first, work = work[0], work[1:]
		enabledtran = enabled(first, TP,PT)
		if(len(enabledtran) == 0):
			for i in first:
				if sum(PT[i-1]) != 0:
					dead = ""
					for i in first:
						if i != 0:
							dead += " p" + str(i)
					print "Deadlock at: [", dead, "]"
					break
		for tran in enabledtran:
			newtoken = fire(first, tran, TP,PT)
			if newtoken not in output[0]:
				output[0].append(newtoken)
				work.append(newtoken)
			output[1].append([first, tran, newtoken])
	return output


def dot_file_output(output, file):
	out = open(file, 'w')
	out.write("digraph M {\n")
	if len(output) == 4:
		for single in output[3]:
			if single == []:
				pass
			node = ""
			for i in range(len(single)):
				if single[i] != 0:
					node += " p"+ str(single[i])
			out.write('"' + node +'" []\n')
		
	for transition in output[1]:
		source = ""
		sink = ""
		if(len(transition) == 3):
			for i in range(len(transition[0])):
				if transition[0][i] != 0:
					source += " p"+ str(transition[0][i])
				if transition[2][i] != 0:
					sink += " p"+ str(transition[2][i])
			#out.write('"' + str(transition[0]) + '"->"' + str(transition[2]) + '"[label = "t' + str(transition[1]) + '"]\n')
			out.write('"' + source + '"->"' + sink + '"[label = "t' + str(transition[1]) + '"]\n')
	out.write("}")
	out.close()

#input function call
[place, tranisition, TP, PT] = get_input()
output2 = statespace_generation(TP, PT, place)
dot_file_output(output2, "statespace.dot")

output1 = reachability_generation(TP, PT, place)
dot_file_output(output1, "reachability.dot")
#ouptut pdf generation
print "Output file generated."
system("dot -Tpdf petrinet.dot > petrinet.pdf")
system("dot -Tpdf reachability.dot > reachability.pdf")
system("dot -Tpdf statespace.dot > statespace.pdf")
