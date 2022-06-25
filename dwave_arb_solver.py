import arbtoqubo as atq
import math
import numpy as np
import csv
import requests as req
import math
from os.path import exists
import dimod
import pandas
from dwave.system.composites import EmbeddingComposite
from dwave.system.samplers import DWaveSampler

dataset='example-dataset.csv'
apikey="your API key"


def make_bqm_from_qubo_matrix(qubo):
    "this function translates the qubo matrix in a form readable for dimod.BinaryQuadraticModel"
    bqm={}
    for i in range(len(qubo)):
        for j in range(i,len(qubo)):
            bqm.update({(i,j):qubo[i][j]})
    return bqm

def convert_response_to_numpy(response):
    "converts dwave response to numpy table"
    #print(response)
    panda=response.to_pandas_dataframe(sample_column=True)
    array=panda.to_numpy()
    return array
            
def solve(qubo,api_key,sampler=None,read_number=1000):
    "this function solves a qubo problem through the dwave sampler"
    bqm=make_bqm_from_qubo_matrix(qubo)
    if sampler == None:
        dwavesampler=DWaveSampler(token=api_key)
        #print(dwavesampler.properties['topology'])
        sampler = EmbeddingComposite(dwavesampler)
    bqm = dimod.BinaryQuadraticModel.from_qubo(bqm)
    response = sampler.sample(bqm, num_reads=read_number, label="Arbitrage")
    #print(response)
    return response
    #return [subsets[i] for i in sample if sample[i]]

def find_best_valid_solution(edges,table,checks=30):
    "finds the best solution between the lowest 'checks' energy states provided by the dwave machine"
    i=0
    best_solution=None
    best_nrg=0
    best_occurs=0
    best_score=0
    for row in table:
        #if row[2]>1:
        if i>checks:
            break
        sol=[]
        for k in row[0].keys():
            sol.append(row[0][k])
        #atq.remove_backward_nodes(sol)
        #print(sol)
        if atq.check_constraint_satisfaction(edges,sol):
            best_solution=sol
            best_nrg=row[1]
            best_occurs=row[2]
            return best_solution, best_nrg, best_occurs
        i+=1
    return None,None,None
        

def main():
    "main function for the dwave_arb_solver module"
    print("Getting Problem...")
    edg,valtocod,codtoval=atq.get_problem_from_dataset(dataset)
    edg_small=atq.make_subset(edg,200)
    print(len(edg_small))
    edg_log=atq.logarithm_on_all(edg_small)
    print("Building QUBO...")
    m1,m2=atq.computeConstrFromResearch(edg_log)
    qubo=atq.get_qubo(edg_small,m1,m2)
    print("Getting results...")
    res=solve(qubo,apikey)
    print("Parsing results...")
    table=convert_response_to_numpy(res)
    print("Checking results...")
    sol,nrg,ocs=find_best_valid_solution(edg_small,table)
    if(sol!=None):
        print(sol)
        print(nrg)
        print(ocs)
        print(atq.natural_solution(edg_small,sol,valtocod,codtoval))
        edg_log=atq.logarithm_on_all(edg_small)
        score=atq.arbitrage_cycle_multiplier_calc(edg_log,sol)
        print(score," -> ",2**score)
    else:
        print("No valid solution was found")


if __name__ == '__main__':
    main()
