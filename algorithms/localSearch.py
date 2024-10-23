from vo import OptimizationProblem


def localSearch(problem: OptimizationProblem, startingSolution):
    currentSolution = startingSolution
    while not problem.is_neighbor_local_optimum():
        currentNeighbor = problem.generate_neighbor(currentSolution)
        if problem.is_better_solution(currentNeighbor, currentSolution):
            currentSolution = currentNeighbor
    return currentSolution