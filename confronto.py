import classical_arb_solver as classic
import dwave_arb_solver as quantum
import numpy as np
import arbtoqubo as atq
import csv
import dwave.cloud.exceptions
from datetime import datetime

#the maximum size of the computable problem, do not change 
MAXSIZE=40
#the default number of reads of the annealer
DEFAULT_READ_NUMBER=1000
#number of quantum solutions printed on output file
SOLUTIONS_CHECKS=30
#the dataset you want to use
DATASET='example-dataset.csv'
#the name of the output file
OUTPUTFILE='output.csv'
#the API key for the dwave leap service
API_KEY="your API key"

def print_on_file_best_solutions(edges,table,valtocod,codtoval):
    "this function prints on file the edges taken by a solution provided by a dwave machine"
    i=0
    for row in table:
        if i>30:
            break
        with open('tmp_output'+str(i)+'.txt', 'w') as f:
            sol=[]
            dict=row[0]
            for k in dict.keys():
                sol.append(dict[k])
                if dict[k]:
                    f.write(str(edges[k]))
                    f.write(",\n")
            f.write("\n")
            f.write(str(sol))
            print(str(i)," done")
        i+=1


def output_on_csv(classic_sol,table,edges,valtocod,codtoval,outputfile):
    "this function outputs the results of the problem on a csv file"
    size=str(len(edges))
    header = ['solver', 'cycle', 'cycle score', 'cycle profit', 'problem size']
    data=[]
    if all(v == 0 for v in classic_sol):
        print("No solution possible")
        return
    classic_adv=atq.arbitrage_cycle_multiplier_calc(edges,classic_sol)
    classic_row=['classic',atq.natural_solution(edges,classic_sol,valtocod,codtoval),classic_adv,2**classic_adv,len(edges)]
    data.append(list(classic_row))
    i=0
    #print(edges)
    #print(table)
    for row in table:
        #print(row)
        if i>=30:
            break
        i+=1
        quantum_sol=[]
        dict=row[0]
        for k in dict.keys():
            quantum_sol.append(dict[k])
        #print(quantum_sol)
        atq.remove_backward_nodes(quantum_sol)
        multiple=False
        if not atq.check_constraint_satisfaction(edges,quantum_sol):
            #print(edges)
            #print(quantum_sol)
            quantum_row=['quantum '+str(i),"Constr. not satisfied",0,0,len(edges)]
            data.append(quantum_row[:])
            continue
        if not atq.check_arbitrage_solution_validity(edges,quantum_sol,False):
            quantum_sol=atq.find_best_cycle(quantum_sol,edges)
            multiple=True
        if atq.check_arbitrage_solution_validity(edges,quantum_sol,False):
            inverse=False
            quantum_adv=atq.arbitrage_cycle_multiplier_calc(edges,quantum_sol)
            if quantum_adv<0:
                quantum_adv=-quantum_adv
                inverse=True
            #print(quantum_adv)
            nat_sol=atq.natural_solution(edges,quantum_sol,valtocod,codtoval)
            if inverse:
                nat_sol.reverse()
                nat_sol.append("reversed")
            if multiple:
                nat_sol.append("multiple")
            quantum_row=['quantum '+str(i),nat_sol,quantum_adv,2**quantum_adv,len(edges)]
            data.append(quantum_row[:])
        else:
            if atq.is_all_zeros(quantum_sol):
                quantum_row=['quantum '+str(i),"[] (do nothing)",0,1,len(edges)]
                data.append
            else:
                print("Strange Solution Found! : ")
                print(quantum_sol)
            
    #print(data)
    try:
        with open(outputfile, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)
    except IOError as err:
        print("Unable to output on csv file, output on terminal instead!")
        print(header)
        for x in data:
            print(x)
        
def doQuantum(edg_subset,api_key,useConstr=True, param=1.7):
    start=datetime.now()
    print(str(datetime.now())+" : Building QUBO Problem...")
    if (useConstr):
        m1,m2= atq.computeConstrFromResearch(atq.logarithm_on_all(edg_subset),param)
    else:
        m1,m2=20,20
    print(str(datetime.now())+" : Using m1 ",m1," and m2 ",m2)
    qubo=atq.get_qubo(edg_subset,m1,m2)
    #print(qubo)
    #edg_subset=atq.logarithm_on_all(edg_subset)
    print(str(datetime.now())+" : QUBO Problem built in "+time_passed_to_string(start)+" seconds")
    start=datetime.now()
    print(str(datetime.now())+" : Solving Quantum through d-wave machine...")
    try:
        res=quantum.solve(qubo,api_key,read_number=DEFAULT_READ_NUMBER)
        print(str(datetime.now())+" : Quantum results got in "+time_passed_to_string(start)+" seconds")
        start=datetime.now()
        print(str(datetime.now())+" : Parsing results...")
        table=quantum.convert_response_to_numpy(res)
        print(str(datetime.now())+" : Results parsed in "+time_passed_to_string(start)+" seconds")
        start=datetime.now()
        return table
    except dwave.cloud.exceptions.SolverFailureError as ex:
        print(str(datetime.now())+" : Impossible to get data from dwave machine:")
        print(ex)
        raise ex

def doClassic(edg_log):
    start=datetime.now()
    print(str(datetime.now())+" : Solving classic...")
    if(len(edg_log)<41):
        classic_solution=classic.arbitrage_classic_solver(edg_log)
    else:
        classic_solution=[]
        for i in range(len(edg_log)):
            classic_solution.append(0)
    print(str(datetime.now())+" : Solved classic in "+time_passed_to_string(start)+" seconds")
    return classic_solution

def time_passed_to_string(start_time):
    return str((datetime.now()-start_time).total_seconds())


def main():
    total_start=start=datetime.now()
    #initializing problem
    print(str(datetime.now())+" : Getting problem...")
    edges,valtocod,codtoval=atq.get_problem_from_dataset(DATASET)
    #print(len(edges))
    edg_small=atq.leaf_cut(edges)
    #print("Problem size:"+str(len(edg_small)))
    #return
    #edg_subset=atq.make_subset(edg_small,MAXSIZE)
    edg_subset=atq.remove_lcn(edg_small,MAXSIZE)
    print(str(datetime.now())+" : Problem size is "+str(len(edg_subset)))
    edg_log=atq.logarithm_on_all(edg_subset)
    print(str(datetime.now())+" : Problem built in "+time_passed_to_string(start)+" seconds")
    #solving problem
    classic_solution=doClassic(edg_log)
    try:
        table=doQuantum(edg_subset, API_KEY)
        #outputting results
        print(str(datetime.now())+" : Outputting results...")
        output_on_csv(classic_solution,table,edg_log,valtocod,codtoval,OUTPUTFILE)
        print(str(datetime.now())+" : Results outputted in "+time_passed_to_string(start)+" seconds")
        print(str(datetime.now())+" : All done in "+time_passed_to_string(total_start)+" seconds")
    except dwave.cloud.exceptions.SolverFailureError as ex:
        print(str(datetime.now())+" : Exception raised after "+time_passed_to_string(total_start)+" seconds")

if __name__ =='__main__':
    main()
