
import copy
import math
import random
import time
import sys

from rectangle_packer_classes.helpers import quick_copy

from .types import OptimizationProblem, Solution, Neighborhood

# """"""""FOR DEBUGGING""""""""
#   import cProfile
#
# Before algorithm run: 
#   profile = cProfile.Profile()
#   profiler.enable()
#
# After algorithm run:
#   profiler.disable()  # Profiling stoppen
#   profiler.print_stats(sort="tottime")  # Ergebnisse ausgeben


class Greedy:
    """
    Greedy algorithm for solving OptimizationProblems
    
    Attributes:
        problem (OptimizationProblem): optimization problem instance that will be solved
        solution_type (type): type of the solution that will be generated for the optimization problem
    """
    def __init__(self, problem: OptimizationProblem, solution_type: type, apply_greedy_strategy, strategy, in_test_env: bool):
        self.problem = problem
        self.solution_type = solution_type
        self.problem.items = apply_greedy_strategy(self.problem.items, strategy)
        self.runs_ins_test_environment = in_test_env

    def solve(self):
        """
    	Solves a optimization problem using a greedy approach. It iteratively selected the next best option according to the chosen strategy
        Returns:
            Solution: Solution object containing the items applied to the problem
        """
        start_time = time.time()

        current_solution = self.solution_type()
        
        interim_solutions = []
        
        # iteratively add each item to the solution in greedy order (order already applied)
        for item in self.problem.items:
            # attempt to add the item to the current solution state
            new_solution = self.problem.add_to_solution(current_solution, item)
            if new_solution is not None:
                # update current solution if the item was successfully added
                current_solution = new_solution
                if not self.runs_ins_test_environment:
                    interim_solutions.append(quick_copy(current_solution))

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Greedy: {elapsed_time:.6f} Sekunden")

        return current_solution, interim_solutions


class LocalSearch:
    """
    Local Search algorithm for solving an optimization problem.
    
    Attributes:
        problem (OptimizationProblem): The optimization problem instance.
        start_solution (Solution): Initial solution to start the search from.
        max_iterations (int): Maximum number of iterations to perform.
        neighborhood (Neighborhood): Neighborhood structure to generate neighboring solutions.
    """
    def __init__(self, problem: OptimizationProblem, start_solution: Solution, max_iterations: int,
                 neighborhood: Neighborhood, in_test_env: bool):
        self.problem = problem
        self.start_solution = start_solution
        self.max_iterations = max_iterations
        self.neighborhood = neighborhood
        self.runs_ins_test_environment = in_test_env

    def solve(self):
        """
        Solves the optimization problem using a Local Search approach.
        
        The algorithm explores the solution space by moving to neighboring solutions 
        that offer an improvement or maintain the current quality.
        
        Returns:
            Solution: The best solution found during the search process.
        """
        start_time = time.time()
        
        interim_solutions = [quick_copy(self.start_solution)] if not self.runs_ins_test_environment else []

        # intiialize the current and best solutions
        current_solution = self.start_solution
        best_solution = current_solution
        best_value = best_solution.evaluate_solution()
        iteration = 0

        # perform local search for specified number of iterations
        while iteration <= self.max_iterations:
            # generate neighbor solution
            neighbor = self.neighborhood.generate_neighbor(current_solution, interim_solutions)
            neighbor_value = neighbor.evaluate_solution()

            # accept the neighbor if it is better or equal to current solution (side steps allowed )
            if neighbor_value <= best_value and not current_solution.are_solutions_equal(neighbor):
                current_solution = neighbor
                best_solution = neighbor
                best_value = neighbor_value
                if not self.runs_ins_test_environment:
                    interim_solutions.append(quick_copy(current_solution))

            # move to the next iteration
            iteration += 1

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit LocalSearch: {elapsed_time:.6f} Sekunden")

        return best_solution, interim_solutions


class SimulatedAnnealing:
    """
    Simulated Annealing algorithm for solving an optimization problem.
    
    Attributes:
        problem (OptimizationProblem): The optimization problem instance.
        start_solution (Solution): Initial solution to start the search from.
        initial_temperature (float): Starting temperature for the annealing process.
        end_temperature (float): Final temperature for the annealing process.
        cooling_rate (float): Rate at which the temperature decreases.
        iterations_per_temp (int): Number of iterations per temperature step.
        neighborhood_strategy (Neighborhood): Neighborhood structure to generate neighboring solutions.
        max_time (float): Maximum time allowed for the algorithm.
    """
    def __init__(self, problem: OptimizationProblem, start_solution: Solution,
                 initial_temperature: float, end_temperature: float, cooling_rate: float,
                 iterations_per_temp: int, neighborhood_strategy: Neighborhood, max_time: float = 10.0, in_test_env: bool = False):
        self.problem = problem
        self.start_solution = start_solution
        self.initial_temperature = initial_temperature
        self.end_temperature = end_temperature
        self.cooling_rate = cooling_rate
        self.iterations_per_temp = iterations_per_temp
        self.neighborhood_strategy = neighborhood_strategy
        self.runs_ins_test_environment = in_test_env
        self.max_time = max_time

    def solve(self):
        """
        Solves the optimization problem using the Simulated Annealing approach.
        
        The algorithm explores the solution space by moving to neighboring solutions 
        with a probability that decreases over time, allowing occasional worse moves
        to escape local optima.
        
        Returns:
            Solution: The best solution found during the search process.
        """
        start_time = time.time()
        
        interim_solutions = []

        # Initiliaze the current and best solutions
        current_solution = self.start_solution
        best_solution = current_solution
        best_value = best_solution.evaluate_solution()
        temperature = self.initial_temperature

        # perform the annealing process until the temperature drops below the threshold
        while temperature > self.end_temperature:
            # perform multiple iteartions at the current temperature level
            for _ in range(self.iterations_per_temp):
                elapsed_time = time.time()-start_time
                # terminate if maximum allowed time is exceeded
                if (elapsed_time >= self.max_time):
                    return best_solution
                
                # generate a neighboring solution
                neighbor = self.neighborhood_strategy.generate_neighbor(current_solution, interim_solutions)
                neighbor_value = neighbor.evaluate_solution()

                # calculate change in objective value
                delta = neighbor_value - best_value

                # accept neighbor if it improves the solution or its with a certain probability
                if delta <= 0 or random.uniform(0, 1) < math.exp(-delta / temperature):
                    current_solution = neighbor
                    if not self.runs_ins_test_environment:
                        interim_solutions.append(quick_copy(neighbor))
                    # update the best solution if the neighbor is better
                    if neighbor_value < best_value:
                        best_solution = neighbor
                        best_value = neighbor_value

            # cool down the temperature according to the cooling rate
            temperature *= self.cooling_rate

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Simulated Annealing: {elapsed_time:.6f} Sekunden")

        return best_solution, interim_solutions


class Backtracking:
    """
    Backtracking algorithm for solving an optimization problem.
    
    Attributes:
        problem (OptimizationProblem): The optimization problem instance.
        solution_type (type): Type of the solution used in the problem.
    """
    def __init__(self, problem: OptimizationProblem, solution_type: type, in_test_env: bool):
        self.problem = problem
        self.solution_type = solution_type
        self.interim_solutions = []
        self.runs_ins_test_environment = in_test_env
        sys.setrecursionlimit(10 ** 6)

    def solve(self):
        """
        Solves the optimization problem using a Backtracking approach.
        
        The algorithm explores the solution space by making decisions 
        incrementally and backtracks whenever a partial solution is invalid 
        or a better solution can be found by exploring other branches.
        
        Returns:
            Solution: The first complete and valid solution found.
        """
        start_time = time.time()
        self.interim_solutions = []

        # intitialize an empty solution
        current_solution = self.solution_type()

        # start the recursive backtracking process
        result = self._backtrack(current_solution, 0)

        copy_interim = self.interim_solutions

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Backtracking: {elapsed_time:.6f} Sekunden")

        return result, copy_interim

    def _backtrack(self, current_solution: Solution, index: int):
        """
        Recursive helper method for the Backtracking algorithm.
        
        It incrementally builds the solution by exploring one decision at a time 
        and recursively backtracks if the current partial solution is not feasible.
        
        Args:
            current_solution (Solution): The current partial solution state.
            index (int): Index of the item to be considered in the current step.
        
        Returns:
            Solution: The first complete and valid solution found, or None if no solution is found.
        """
        # base case: if all items are processed, return the current solution
        if index >= len(self.problem.items):
            return current_solution
        
        # get the next item to be placed in the solution
        item = self.problem.items[index]
        
        # attempt to add item to current solution
        new_solution = self.problem.add_to_solution(current_solution, item)

        # if item was successfully added, continue with the next item
        if new_solution is not None:
            if not self.runs_ins_test_environment:
                self.interim_solutions.append(quick_copy(new_solution))
            result = self._backtrack(new_solution, index + 1)
            if result is not None:
                return result # return the first valid complete solution found

        # backtrack if no valid solution is found
        return None
