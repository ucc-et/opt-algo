"""
    Author: Ugurtan Can Cetin
    M.Nr: 2249982
    Task: 
    the Rectangle Packing Problem
    - with the Algorithms local Search and Greedy. 
    - Possible Neighborhood generations (Local Search): 
        - Geometry based
        - rule based
        - allow (partial) overlapping
    - Possible Choosing Strategy (Greedy)
        - my choice (but two needed)

"""

class OptimizationProblem:
    def generate_neighbor(self, solution):
        raise NotImplementedError
    
def metStoppingCriteria():
    """
        Check if Local Optimum has been found, and there is no other
    """
    raise NotImplementedError

def neighborIsLocalOptimum(newNeighbor, previousSolution):
    """
        Compare Local Optima
    """
    raise NotImplementedError

def localSearch(problemType: OptimizationProblem, startingSolution):
    currentSolution = startingSolution
    while not metStoppingCriteria():
        currentNeighbor = problemType.getNeighbor(currentSolution)
        if neighborIsLocalOptimum(currentNeighbor, currentSolution):
            currentSolution = currentNeighbor
    return currentSolution
