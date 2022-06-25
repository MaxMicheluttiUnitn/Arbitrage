import numpy as np
import arbtoqubo as atq

dataset='example-dataset.csv'

def arbitrage_classic_solver(edges):
    "this function wraps another function that tests all possible solutions of the classical arbitrage problem to find the best one"
    solution=[]
    best_value=[0]
    last_solution=np.zeros(shape=(len(edges)),dtype=int) #choosing nothing which gains 0 is chosen as the basic solution, greedy choices could improve this algorithm
    test_all(edges,0,solution,last_solution,best_value)
    return last_solution

def process_solution(edges,solution,last_solution,best_value):
    "this function checks if a solution is valid and evaluates the solution"
    #validity checking
    #check cycle possibility
    if not atq.check_arbitrage_solution_validity(edges,solution):
        return
    #evaluation
    sum=atq.arbitrage_cycle_multiplier_calc(edges,solution)
    #comparing with best_value
    if sum>best_value[0]:
        for i in range(len(solution)):
            last_solution[i]=solution[i]
        best_value[0]=sum
    #print(sum)

def reject(edges,index,solution):
    "this function checks if a partial solution is invalid"
    #if there are more then 2 edges entering or exiting the same node the solution is invalid
    nodes={}
    for i in range(index):
        if solution[i]:
            if edges[i][0] in nodes.keys():
                nodes[edges[i][0]]+=1
                if nodes[edges[i][0]]>2:
                    return True
            else:
                nodes.update({edges[i][0]:1})
            if edges[i][1] in nodes.keys():
                nodes[edges[i][1]]+=1
            else:
                nodes.update({edges[i][1]:1})
                if nodes[edges[i][1]]>2:
                    return True
    return False

def test_all(edges,index,solution,last_solution,best_result):
    "this function tests all possible solutions to find the best one"
    if index==len(edges):#accept
        process_solution(edges,solution,last_solution,best_result)
    else:
        if reject(edges,index,solution):#reject
            return
        else:
            solcopy=solution[:]
            solcopy.append(0)
            solcopy.append(0)
            test_all(edges,index+2,solcopy,last_solution,best_result)
            solcopy=solution[:]
            solcopy.append(0)
            solcopy.append(1)
            test_all(edges,index+2,solcopy,last_solution,best_result)
            solcopy=solution[:]
            solcopy.append(1)
            solcopy.append(0)
            test_all(edges,index+2,solcopy,last_solution,best_result)


def QUBO_classical_solver(qubo, edges):
    solution=[]
    best_value=[0]
    last_solution=np.zeros(shape=(len(edges)),dtype=int) #choosing nothing which gains 0 is chosen as the basic solution, greedy choices could improve this algorithm
    QUBO_test_all(qubo,edges,0,solution,last_solution,best_value)
    return last_solution
                
def QUBO_test_all(qubo,edges,index,partial_solution,best_solution,best_value):
    if index==len(qubo):#accept
        QUBO_process_solution(qubo,edges,partial_solution,best_solution,best_value)
    else:
        if index>0 and QUBO_reject(edges,index,partial_solution):#reject
            return
        else:
            solcopy=partial_solution[:]
            solcopy.append(0)
            solcopy.append(0)
            QUBO_test_all(qubo,edges,index+2,solcopy,best_solution,best_value)
            solcopy=partial_solution[:]
            solcopy.append(0)
            solcopy.append(1)
            QUBO_test_all(qubo,edges,index+2,solcopy,best_solution,best_value)
            solcopy=partial_solution[:]
            solcopy.append(1)
            solcopy.append(0)
            QUBO_test_all(qubo,edges,index+2,solcopy,best_solution,best_value)
            solcopy=partial_solution[:]
            solcopy.append(1)
            solcopy.append(1)
            QUBO_test_all(qubo,edges,index+2,solcopy,best_solution,best_value)

def QUBO_process_solution(qubo,edges,solution,best_sol,best_v):
    #if(not atq.check_constraint_satisfaction(edges,solution)):
        #return
    sol_v=atq.QUBO_energy_calc(qubo,solution)
    if(sol_v<best_v):
        for i in range(len(solution)):
            best_sol[i]=solution[i]
        best_v[0]=sol_v
    return

def QUBO_reject(edges,index,tmp_solution):
    #use commented code if solving a specific arbitrage problem in qubo format
    #tmp_edges=edges[:index]
    #return not atq.check_tmp_constraint_satisfaction(tmp_edges,tmp_solution)
    return False

def main():
    "main function for classical_arb_solver_v2.py"
    edg,a,b=atq.get_problem_from_dataset(dataset)
    edg_small=atq.leaf_cut(edg)
    edg_subset=atq.make_subset(edg_small,35)
    edg_subset_log=atq.logarithm_on_all(edg_subset)
    solution=arbitrage_classic_solver(edg_subset_log)
    print(edg_subset_log)
    print(solution)
    gain=atq.arbitrage_cycle_multiplier_calc(edg_subset_log,solution)
    print(gain," -> ",2.0**gain)

if __name__ == '__main__':
    main()
