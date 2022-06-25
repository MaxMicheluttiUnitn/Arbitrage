import numpy as np
import csv
#import requests as req
import math
#from os.path import exists
import random
import copy
#import requests, json


def read_csv_dataset(file):
    "this unction reads a csv dataset and initializes the arbitrage problem"
    valuta_to_codice=dict()
    edges=[]
    codice_to_valuta=[]
    with open(file, newline='') as csvfile:
        reader=csv.DictReader(csvfile)
        for row in reader:
            x=row['symbol'].split('-')
            num=x[0]
            denom=x[1]
            if not (num in valuta_to_codice.keys()):#aggiungo num al dizionario delle valute
                valuta_to_codice.update({num: len(valuta_to_codice)})
                codice_to_valuta.append(num)
            if not (denom in valuta_to_codice.keys()):#aggiungo denom al dizionario delle valute
                valuta_to_codice.update({denom: len(valuta_to_codice)})
                codice_to_valuta.append(denom)
            value=float(row['open'])# have to fix the string so that it can be parsed into a real number
            edges.append([valuta_to_codice[num],valuta_to_codice[denom],value])
            edges.append([valuta_to_codice[denom],valuta_to_codice[num],1.0/value])
    return valuta_to_codice, codice_to_valuta, edges


def read_csv(input_file_name):
    "this function reads the csv file from investing.com and initializes the variables of the problem"
    valuta_to_codice=dict()
    edges=[]
    codice_to_valuta=[]
    with open(input_file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:#popolo dizionario delle valute
            x=row['ï»¿"Simbolo"'].split('/')
            num=x[0] #stringa che rappresenta una valuta
            denom=x[1] #stringa che rappresenta una valuta
            if not (num in valuta_to_codice.keys()):#aggiungo num al dizionario delle valute
                valuta_to_codice.update({num: len(valuta_to_codice)})
                codice_to_valuta.append(num)
            if not (denom in valuta_to_codice.keys()):#aggiungo denom al dizionario delle valute
                valuta_to_codice.update({denom: len(valuta_to_codice)})
                codice_to_valuta.append(denom)
    with open(input_file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:#popolo tabella del valore di scambio
            x=row['ï»¿"Simbolo"'].split('/')#row['ï»¿"Simbolo"'] has the format "VA1/VA2" and means that if i give 1 VA1 i receive row["Denaro"] VA2  
            num=x[0]#gets the numerator of the exchange
            denom=x[1]#gets the denominator of the exchange
            value=float((row['Denaro'].replace('.','')).replace(',','.'))# have to fix the string so that it can be parsed into a real number
            edges.append([valuta_to_codice[num],valuta_to_codice[denom],value])
            edges.append([valuta_to_codice[denom],valuta_to_codice[num],1.0/value])
    return valuta_to_codice, codice_to_valuta, edges

def logarithm_on_all(edges):
    "this function takes in input a list of weighted edges and applies the logarithm in base 2 to every weight"
    res=copy.deepcopy(edges)
    for i in range(len(res)):
        res[i][2]=math.log2(res[i][2])
    return res

def invert_sign_matrix(matrix):
    "this function takes in input a square matrix and changes the sign of every cell of the matrix"
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i][j]=-matrix[i][j]
    return matrix

def make_arbitrage_qubo(edges,M1=10,M2=10):
    "this funcion takes in input the list of the graph's edges and computes the qubo matrix"
    edges = logarithm_on_all(edges)
    qubo= np.zeros(shape=(len(edges),len(edges)), dtype=float)
    #definizione di score del percorso
    for i in range(len(edges)):
        qubo[i][i]=edges[i][2]
    #colleziono i nodi
    node_ids=get_node_ids(edges)
    #print(len(edges))
    #primo constraint (controllato, funziona a meraviglia)
    #convenzione: non esistono edge del tipo [x,x]
    qubo_part1= np.zeros(shape=(len(edges),len(edges)), dtype=float)
    qubo_part2= np.zeros(shape=(len(edges),len(edges)), dtype=float)
    for v in node_ids:#for i in v
        tmp=np.zeros(shape=(len(edges),len(edges)), dtype=int)
        for j in range(len(edges)):
            if v==edges[j][0]:
                tmp[j][j]=1
            if v==edges[j][1]:
                tmp[j][j]=-1
        for i in range(len(edges)):
            for j in range(len(edges)):
                if i!=j:
                    tmp[i][j]=2*tmp[i][i]*tmp[j][j]
                    #tmp[j][i]=2*tmp[i][i]*tmp[j][j]
        for i in range(len(edges)):
            tmp[i][i]*=tmp[i][i]
        #print(tmp)
        for i in range(len(edges)):
            for j in range(len(edges)):
                qubo[i][j]+=tmp[i][j]*(-M1)
                qubo_part1[i][j]+=tmp[i][j]
    #secondo constraint
    #print("second")
    '''for v in node_ids:#for i in v
        tmp=np.zeros(shape=(len(edges),len(edges)), dtype=int)
        for i in range(len(edges)):
            if v==edges[i][0]:
                #tmp[i][i]+=1
                for j in range(len(edges)):
                    if v==edges[j][0] and i!=j:
                        tmp[i][j]+=1
                        tmp[j][i]+=1
                        tmp[i][i]-=1
                #print(tmp)'''
    for v in node_ids:#for i in v
        tmp=np.zeros(shape=(len(edges),len(edges)), dtype=int)
        #conto=0
        for i in range(len(edges)):
            if edges[i][0]==v:
                #conto+=1
                for j in range(len(edges)):
                    if edges[j][0]==v and i!=j:
                        tmp[i][j]+=1
                        tmp[j][i]+=1
        '''for i in range(len(edges)):
            if edges[i][0]==v:
                tmp[i][i]=1-conto'''
        #print(tmp)
        for i in range(len(edges)):
            for j in range(len(edges)):
                qubo[i][j]+=tmp[i][j]*(-M2)
                qubo_part2[i][j]+=tmp[i][j]
    #setting to 0 everything under the diagonal
    for i in range(len(qubo)):
        for j in range(0,i):
            qubo[i][j]=0

    #print("M1:\n",qubo_part1)
    #print("M2:\n",qubo_part2)
    #fine secondo constraint
    qubo=invert_sign_matrix(qubo)
    return qubo

def test_values():
    "this function initializes the edge list with test values"
    edges =[[0,1,2.0],[1,0,0.5],[0,2,4.0],[2,0,0.25],[1,2,3.0],[2,1,1.0/3.0],[3,0,0.1],[0,3,10.0],[1,3,2.0],[3,1,0.5]]
    valtocod={"EUR":0,"GBP":1,"USD":2,"CAD":3}
    codtoval=["EUR","GBP","USD","CAD"]
    return valtocod,codtoval,edges

def get_qubo(edges=[],M1=10,M2=10):
    "this function reads the input and computes the qubo matrix for the arbitrage problem"
    # codtoval: lista che associa a ogni id una stringa col nome della valuta
    # valtocod: dizionario che associa a ogni stringa il relativo id
    # edges: lista di tutti i vertici del grafo con relativo peso
    #edges=test_values()
    if edges==[]:
        valtocod, codtoval, edges= read_csv('cambio_valute.csv')
    qubo = make_arbitrage_qubo(edges,M1,M2)
    return qubo

def arbitrage_cycle_multiplier_calc(edges,solution):
    "this function computes the score of a solution"
    sum=0
    for i in range(len(solution)):
        if solution[i]:
            sum+=edges[i][2]
    return sum

def QUBO_energy_calc(qubo,solution):
    x=np.atleast_2d(solution)
    x_t=np.matrix.transpose(x)
    tmp=np.matmul(x,qubo)
    tmp=np.matmul(tmp,x_t)
    return tmp[0][0]

def get_problem_from_dataset(dataset):
    "this function builds the problem from a specific csv dataset"
    valtocod, codtoval, edges= read_csv_dataset(dataset)
    return edges,valtocod,codtoval

def get_problem():
    "this function builds the problem from the csv file"
    valtocod, codtoval, edges= read_csv('cambio_valute.csv')
    return edges,valtocod,codtoval

def computeConstrFromResearch(edges, param=1.6):
    max_edge=0
    for edge in edges:
        if max_edge<edge[2]:
            max_edge=edge[2]
    m1=max_edge/param
    prob_size=len(edges)
    m2=m1*1.005
    #print(m1," ",m2)
    return m1,m1

def leaf_cut(edges):
    new_edges=list(edges)
    while(contains_leaf(new_edges)):
        new_edges=leaves_cutting(new_edges)
    return new_edges

def contains_leaf(edges):
    node_ids={}
    for e in edges:
        if not (e[0] in node_ids.keys()):
            node_ids.update({e[0]:1})
        else:
            node_ids[e[0]]+=1
        if not (e[1] in node_ids.keys()):
            node_ids.update({e[1]:1})
        else:
            node_ids[e[1]]+=1
    for i in node_ids.keys():
        if node_ids[i]<=2:
            return True
    return False

def leaves_cutting(edges):
    "this function reduces the size of the problem by eliminating all leaf nodes"
    node_ids={}
    for e in edges:
        if not (e[0] in node_ids.keys()):
            node_ids.update({e[0]:1})
        else:
            node_ids[e[0]]+=1
        if not (e[1] in node_ids.keys()):
            node_ids.update({e[1]:1})
        else:
            node_ids[e[1]]+=1
    keep=[]
    for i in node_ids.keys():
        if node_ids[i]>2:#if there exists less then 2 connections with the rest of the graph, the node is a leaf and can be ignored
            keep.append(i)
    #print(edge_matrix)
    new_edges=[]
    for e in edges:
        if e[0] in keep and e[1] in keep:
            new_edges.append([e[0],e[1],e[2]])
    #print(new_edges)
    return new_edges


def check_arbitrage_solution_validity(edges,solution,print_error=False):
    "this function checks if a solution for the arbitrage problem is valid returning a boolean"
    if len(solution)!=len(edges):
        if print_error:
            print("Invalid solution: Solution is incomplete or too big")
        return False
    nodes={}
    edge_taken=[]
    for i in range(len(edges)):
        if solution[i]:
            if edges[i][0] in nodes.keys():
                nodes[edges[i][0]]+=1
            else:
                nodes.update({edges[i][0]:1})
            if edges[i][1] in nodes.keys():
                nodes[edges[i][1]]+=1
            else:
                nodes.update({edges[i][1]:1})
            edge_taken.append(edges[i])
    if len(edge_taken)<2:#if less than 2 edges were taken the solution is invalid
        if print_error:
            print("Invalid solution: Too few edges")
        return False
    for j in nodes.values():
        #if j%2!=0:
        if j!=0 and j!=2:#if there is a node with an odd number of edges in the solution, the solution is invalid
            if print_error:
                print("Invalid solution: Node with invalid number of edges in the solution")
            return False
    cycle=[edge_taken[0]]
    cylen=len(edge_taken)
    while cycle[0][0]!=cycle[-1][1]:
        found=False
        for e in edge_taken:
            if e[0]==cycle[-1][1]:
                cycle.append(e)
                edge_taken.remove(e)
                found=True
                break
        if not found:#if it is impossible to finish the cycle the solution is invalid
            if print_error:
                print("Invalid solution: Can't build full cycle")
            return False
    if len(cycle)<cylen:#if some edges are not in the cycle it means i have multiple cycles so the solution is invalid
        if print_error:
            print("Invalid solution: Multiple Cycles")
        return False
    #if everything is ok with the solution i can return True
    return True

def check_tmp_constraint_satisfaction(edges,solution):
    "this function checks if the constraints defined in the paper are satisfied by a non completely built solution"
    node_ids=get_node_ids(edges)
    entring={}
    exiting={}
    #init counters
    for node in node_ids:
        entring.update({node:0})
        exiting.update({node:0})
    #calc counters
    for i in range(len(solution)):
        if(solution[i]):
            edge=edges[i]
            exiting[edge[0]]+=1
            entring[edge[1]]+=1
    #constraint 2:
    #print(solution)
    #print(entring)
    #print(exiting)
    for i in node_ids:
        if entring[i]>1:
            return False
        if exiting[i]>1:
            return False
    return True

def check_constraint_satisfaction(edges,solution):
    "this function checks if the constraints defined in the paper are satisfied by a solution"
    node_ids=get_node_ids(edges)
    entring={}
    exiting={}
    #init counters
    for node in node_ids:
        entring.update({node:0})
        exiting.update({node:0})
    #calc counters
    for i in range(len(solution)):
        if(solution[i]):
            edge=edges[i]
            exiting[edge[0]]+=1
            entring[edge[1]]+=1
    #checking counters
    #constraint 1:
    for i in node_ids:
        if entring[i]!=exiting[i]:
            return False
    #constraint 2:
    for i in node_ids:
        if entring[i]>1:
            return False
    return True

def is_all_zeros(solution):
    "this function checks if a solution is the empty solution"
    for i in solution:
        if i!=0:
            return False
    return True

def remove_backward_nodes(solution):
    "this function takes in input a solution that could have a useless cycle (x -> y -> x) and removes it from the solution"
    i=0
    while i<len(solution):
        if solution[i]==1 and solution[i+1]==1:
            solution[i]=0
            solution[i+1]=0
        i+=2

def get_node_ids(edges):
    "gets the ids of all nodes in the graph describing the problem"
    node_ids=[]
    for e in edges:
        if not e[0] in node_ids:
            node_ids.append(e[0])
        if not e[1] in node_ids:
            node_ids.append(e[1])
    return node_ids

def less_connected_node(edges):
    node_ids={}
    for e in edges:
        if not (e[0] in node_ids.keys()):
            node_ids.update({e[0]:1})
        else:
            node_ids[e[0]]+=1
        if not (e[1] in node_ids.keys()):
            node_ids.update({e[1]:1})
        else:
            node_ids[e[1]]+=1
    min_conn=np.Infinity
    res=-1
    for id in node_ids.keys():
        if node_ids[id]<min_conn:
            min_conn=node_ids[id]
            res=id
    return res

def remove_lcn(edges,max_size):
    new_edges=list(edges)
    while len(new_edges)>max_size:
        id_n=less_connected_node(new_edges)
        new_edges=remove_node(new_edges,id_n)
        new_edges=leaf_cut(new_edges)
    return new_edges

def remove_node(edges,id):
    new_edges=[]
    nodes=get_node_ids(edges)
    nodes.remove(id)
    for e in edges:
        if (e[0] in nodes) and (e[1] in nodes):
            new_edges.append(e)
    return new_edges

def remove_random_node(edges):
    "takes a subset of the problem removing one nodes from the graph"
    nodes=get_node_ids(edges)
    new_edges=[]
    if len(nodes)>1:
        random.shuffle(nodes)
        nodes=nodes[:-1]
        for e in edges:
            if (e[0] in nodes) and (e[1] in nodes):
                new_edges.append(e)
    return new_edges

def make_subset(edges, max_size):
    "takes a subset of the problem removing nodes from the graph until the problem's size is less than max_size"
    new_edges=list(edges)
    while len(new_edges)>max_size:
        new_edges=remove_random_node(new_edges)
        new_edges=leaf_cut(new_edges)
    return new_edges

def find_best_cycle(solution,edges):
    "this function takes a multiple cycle solution and extracts the best cycle correcting the solution"
    edg_subset=[]
    for i in range(len(solution)):
        if solution[i]:
            edg_subset.append(edges[i])
    node_ids=get_node_ids(edg_subset)
    best_cycle=None
    best_value=-1000
    while len(node_ids)>0:
        cycle=[node_ids[0]]
        cycle_value=0
        while(cycle[0]!=cycle[-1] or len(cycle)<2):
            for e in edg_subset:
                if e[0]==cycle[-1]:
                    cycle.append(e[1])
                    cycle_value+=e[2]
                    node_ids.remove(e[1])
        #print(cycle)
        if cycle_value>best_value:
            best_value=cycle_value
            best_cycle=list(cycle)
    for i in range(len(solution)):
        solution[i]=0
    if best_cycle==None:
        return []
    for i in range(len(best_cycle)-1):
        for j in range(len(edges)):
            if edges[j][0]==best_cycle[i] and edges[j][1]==best_cycle[i+1]:
                solution[j]=1
    return solution
        

        

def natural_solution(edges, solution, valtocod,codtoval) -> list:
    "this function translates the solution in an array of strings describing the solution in a natural way"
    nodes={}
    edge_taken=[]
    for i in range(len(edges)):
        if solution[i]:
            if edges[i][0] in nodes.keys():
                nodes[edges[i][0]]+=1
            else:
                nodes.update({edges[i][0]:1})
            if edges[i][1] in nodes.keys():
                nodes[edges[i][1]]+=1
            else:
                nodes.update({edges[i][1]:1})
            edge_taken.append(edges[i])
    nat_sol=[]
    cycle=[edge_taken[0]]
    while cycle[0][0]!=cycle[-1][1]:
        found=False
        for e in edge_taken:
            if e[0]==cycle[-1][1]:
                cycle.append(e)
                edge_taken.remove(e)
                found=True
                break
    nat_sol.append(cycle[0][0])
    for e in cycle:
        nat_sol.append(e[1])
    for i in range(len(nat_sol)):
        nat_sol[i]=codtoval[nat_sol[i]]
    return nat_sol


def main():
    "main function for this arbtoqubo_v2"
    print("This file is used as a module to build and evaluate arbitrage problems and QUBO matrix")

if __name__=='__main__':
    #read_all_datasets(datetime.now())
    main()
