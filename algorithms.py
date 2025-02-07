from neighborhoods import NeighborhoodStrategy
from objects import RecPac_Solution
from problem import OptimizationProblem
import time

class Greedy:
    def __init__(self, problem: OptimizationProblem, strategy = "largest_area_first"):
        self.problem = problem
        self.strategy = strategy
    
    def solve(self):
        start_time = time.time()
        
        current_solution = RecPac_Solution() # Start with an empty solution
        # Iterate over all instances and place each one
        for instance in self.problem.rectangles:
            new_solution = self.problem.add_to_solution(current_solution, instance)
            if new_solution is not None:
                current_solution = new_solution
                
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Greedy: {elapsed_time:.6f} Sekunden")

        return current_solution


class LocalSearch:
    def __init__(self, problem: OptimizationProblem, max_iterations: int, neighborhood_strategy: NeighborhoodStrategy):
        self.problem = problem
        self.max_iterations = max_iterations
        self.neighborhood_strategy = neighborhood_strategy

    def solve(self):
        current_solution = self.problem.basic_solution()
        best_solution = current_solution
        best_value = best_solution.evaluate_solution()
        iteration = 0

        while iteration < self.max_iterations:
            # Generate a single neighbor (adjust to match your strategy's behavior)
            neighbor = self.neighborhood_strategy.generate_neighbor(current_solution)
            
            neighbor_value = neighbor.evaluate_solution()
            if neighbor_value <= best_value:
                current_solution = neighbor
                best_solution = neighbor
                best_value = neighbor_value
            else:
                # No improvement; optionally log or debug this
                pass

            iteration += 1

        return best_solution

class SimmulatedAnnealing:
    pass

class Backtracking:
    pass