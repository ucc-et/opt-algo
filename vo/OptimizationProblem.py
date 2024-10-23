class OptimizationProblem:
    def generate_neighbor(self, solution):
        raise NotImplementedError
    
    def is_neigbor_local_optimum(self, neighbor):
        raise NotImplementedError
    
    def is_better_solution(self, solution1, solution2):
        raise NotImplementedError
    