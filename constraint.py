from math import ceil
import classical_arb_solver as classic
import dwave_arb_solver as quantum
import numpy as np
import arbtoqubo as atq
import csv
import dwave.cloud.exceptions
from datetime import datetime
from random import random

#the input dataset 
DATASET='2017-7-forex.csv' 
#the number of reads of the annealer
DEFAULT_READ_NUMBER=1000
#a valid API key for dwave leap service
API_KEY="your API key"

def getSolutionAtLine(table,line):
    row=table[line]
    quantum_sol=[]
    dict=row[0]
    for k in dict.keys():
        quantum_sol.append(dict[k])
    return quantum_sol

def find_best_constr_quantum_random(edges):
    m1=random()*10+35 #random number between 40 and 50
    m2=m1-1
    m1High=100
    m2High=101
    m1Low=1
    while(m2<m1):
        m2=m1+(m1*1.01-m1)*random()
    iterations=0
    while(iterations!=20):
        qubo=atq.make_arbitrage_qubo(edges,m1,m2)
        print("QUBO DONE")
        print(edges[0])
        try:
            res=quantum.solve(qubo,API_KEY,read_number=DEFAULT_READ_NUMBER)
        except :
            break
        table=quantum.convert_response_to_numpy(res)
        best_sol_found=getSolutionAtLine(table,0)
        if(atq.check_constraint_satisfaction(edges,best_sol_found)):
            m1High=m1
            m2High=m2
        else:
            m1Low=m1
            #m2Low=m2
        m1=m1Low+(m1High-m1Low)*random()
        m2=min(m1+(m1*1.1-m1)*random(),m2High)
        iterations+=1
        print(iterations," : ",m1,m2)
    print(m1,m2)


def find_best_constr_classic_random(edges):
    m1=random()*10+40 #random number between 40 and 50
    m2=random()*10+40
    m1High=100
    m2High=100
    m1Low=1
    while(m2<m1):
        m2=m1+(m2High-m1)*random()
    print(m1," ",m2)
    #m2Low=1
    iterations=0
    print("Problem size: "+str(len(edges)))
    while(iterations!=20):
        qubo=atq.make_arbitrage_qubo(edges,m1,m2)
        print("QUBO DONE")
        solution=classic.QUBO_classical_solver(qubo,edges)
        print(solution)
        if(atq.check_constraint_satisfaction(edges,solution)):
            m1High=m1
            m2High=m2
        else:
            m1Low=m1
            #m2Low=m2
        m1=m1Low+(m1High-m1Low)*random()
        m2=m1+(m2High-m1)*random()
        print("Calculating new m1 and m2")
        while(m2<m1):
            m2=min(m2High,m1+(m1*1.1-m1)*random())
        iterations+=1
        print(m1,m2)
        print("iteration ",iterations," done")
    print(m1,m2)

def find_best_constr_quantum_prop(edges):
    m1=50.5
    m1High=100
    m1Low=1
    iterations=0
    while(iterations!=20):
        qubo=atq.make_arbitrage_qubo(edges,m1,m1*2)
        print("QUBO DONE")
        try:
            res=quantum.solve(qubo,API_KEY,read_number=DEFAULT_READ_NUMBER)
        except :
                break
        table=quantum.convert_response_to_numpy(res)
        best_sol_found=getSolutionAtLine(table,0)
        if(atq.check_constraint_satisfaction(edges,best_sol_found)):
            m1High=m1
            m1=(m1High+m1Low)/2
        else:
            m1Low=m1
            m1=(m1High+m1Low)/2
        iterations+=1
        print(m1,m1*2)
    print(m1,m1*2)

def find_best_constr_classic_prop(edges):
    m1=50.5
    m1High=100
    m1Low=1
    iterations=0
    print("Problem size: "+str(len(edges)))
    while(iterations!=20):
        qubo=atq.make_arbitrage_qubo(edges,m1,m1*2)
        print("QUBO DONE")
        solution=classic.QUBO_classical_solver(qubo,edges)
        print(solution)
        if(atq.check_constraint_satisfaction(edges,solution)):
            m1High=m1
            m1=(m1High+m1Low)/2
        else:
            m1Low=m1
            m1=(m1High+m1Low)/2
        iterations+=1
        print(m1,m1*2)
    print(m1,m1*2)


def find_best_constr_quantum_equal(edges):
    m1=50.5
    m1High=100
    m1Low=1
    iterations=0
    while(iterations!=20):
        qubo=atq.make_arbitrage_qubo(edges,m1,m1)
        print("QUBO DONE")
        try:
            res=quantum.solve(qubo,API_KEY,read_number=DEFAULT_READ_NUMBER)
        except :
                break
        table=quantum.convert_response_to_numpy(res)
        best_sol_found=getSolutionAtLine(table,0)
        if(atq.check_constraint_satisfaction(edges,best_sol_found)):
            m1High=m1
            m1=(m1High+m1Low)/2
        else:
            m1Low=m1
            m1=(m1High+m1Low)/2
        iterations+=1
        print(m1,m1)
    print(m1,m1)

def find_best_constr_classic_equal(edges):
    m1=50.5
    m1High=100
    m1Low=1
    iterations=0
    print("Problem size: "+str(len(edges)))
    while(iterations!=20):
        qubo=atq.make_arbitrage_qubo(edges,m1,m1)
        print("QUBO DONE")
        solution=classic.QUBO_classical_solver(qubo,edges)
        print(solution)
        if(atq.check_constraint_satisfaction(edges,solution)):
            m1High=m1
            m1=(m1High+m1Low)/2
        else:
            m1Low=m1
            m1=(m1High+m1Low)/2
        iterations+=1
        print(m1,m1)
    print(m1,m1)

def main():
    edges,valtocod,codtoval=atq.get_problem_from_dataset(DATASET)
    edges=atq.leaf_cut(edges)
    #print(len(edges))
    edges=atq.remove_lcn(edges,36)
    print(edges)
    print(atq.logarithm_on_all(edges))
    print(len(edges))
    print(max(edges))
    #change the name of this function to change the type of research to be done
    find_best_constr_quantum_equal(edges)

if __name__=="__main__":
    main()
