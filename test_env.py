import copy
from datetime import datetime
import os
import random
import time
import json

from classes.base_classes import OptimizationProblem
from solvers.algorithms import Greedy, LocalSearch
from classes.helpers import apply_greedy_strategy, generate_instances
from solvers.enums import GreedyStrategy, Neighborhoods
from solvers.neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy
from classes import Box, RecPac_Solution, RectanglePacker

class TestEnvironment:
    """
    A class to manage the test environment for rectangle packing algorithms.
    """
    def __init__(self):
        # Configuration
        self.box_length = -1
        self.greedy_strategy = None
        self.neighborhood = None
        self.max_iterations = 21
        
        # Data Storage
        self.instances = []
        self.greedy_solutions = []
        self.local_search_solutions = []
        self.times_greedy = []
        self.times_local_search = []
    
    def __repr__(self):
        return (f"TestEnvironment(box_length={self.box_length}, "
                f"greedy_strategy={self.greedy_strategy}, "
                f"neighborhood={self.neighborhood}, "
                f"max_iterations={self.max_iterations})")
    
    def run(self):
        """
        Main entry point for running all tests.
        """
        self.run_greedy()
        self.run_local_search()
        self.save_solutions()
        self.create_protocol()

    def run_greedy(self):
        """
        Runs the greedy algorithm on all instances.
        """
        print("\nStarting Greedy Algorithm...")
        for i, instance_set in enumerate(self.instances):
            start_time = time.time()
            print(f"Processing Instance {i+1}/{len(self.instances)} with {len(instance_set)} rectangles...")
            
            instance_set = apply_greedy_strategy(instance_set, self.greedy_strategy)
            
            problem = RectanglePacker(instance_set, self.box_length)
            solver = Greedy(problem, RecPac_Solution, self.greedy_strategy)
            solution = solver.solve()
            
            self.times_greedy.append(time.time() - start_time)
            self.greedy_solutions.append(solution)
            
        print("\nGreedy Algorithm Completed.")
    
    def run_local_search(self):
        """
        Runs the local search algorithm on all instances.
        """
        print("\nStarting Local Search...")
        for i, instance_set in enumerate(self.instances):
            print(f"Processing Instance {i+1}/{len(self.instances)} with {len(instance_set)} rectangles...")
            
            instance_set_copy = copy.deepcopy(instance_set)
            problem = RectanglePacker(instance_set_copy, self.box_length)
            
            if self.neighborhood == Neighborhoods.GEOMETRY.value:
                start_solution, neighborhood = self.merge_geometry_based_solutions(problem, self.neighborhood, instance_set_copy, self.box_length, "")
            else:
                start_solution, neighborhood = self.get_start_solution_and_neighborhood(
                    problem, self.neighborhood, instance_set_copy, self.box_length, ""
                )
            
            solver = LocalSearch(problem, start_solution, self.max_iterations, neighborhood)
            start_time = time.time()
            solution = solver.solve()
            
            self.times_local_search.append(time.time() - start_time)
            self.local_search_solutions.append(solution)
            
        print("\nLocal Search Completed.")
    
    def merge_geometry_based_solutions(self, problem, neighborhood_name, items, container_size, rulebased_strategy):
        start_solution = RecPac_Solution()
        sub_lists, neighborhood = self.get_start_solution_and_neighborhood(problem, neighborhood_name, items, container_size, rulebased_strategy)
        for sub_list in sub_lists:
            temp_solt = self.greedy_algorithm(sub_list, container_size, GreedyStrategy.LARGEST_AREA_FIRST.value)
            for box in temp_solt.boxes:
                start_solution.add_box(box)
        return start_solution, neighborhood
    
    def get_start_solution_and_neighborhood(self, problem, neighborhood_name, items, container_size, rulebased_strategy):
        """
        Determines the starting solution and neighborhood strategy.
        """
        start_solution_map = {
            "Geometriebasiert": problem.generate_item_samples(items),
            "Regelbasiert": self.greedy_algorithm(items, container_size, GreedyStrategy.LARGEST_AREA_FIRST.value),
            "Überlappungen teilweise zulassen": problem.generate_initial_solution(items, container_size),
        }
        neighborhood_map = {
            "Geometriebasiert": GeometryBasedStrategy(problem, RecPac_Solution),
            "Regelbasiert": RuleBasedStrategy(problem, rulebased_strategy),
            "Überlappungen teilweise zulassen": OverlapStrategy(problem)
        }
        return start_solution_map[neighborhood_name], neighborhood_map[neighborhood_name]

    def greedy_algorithm(self, items, container_size, strategy_name):
        """
        Solves the problem using the selected greedy strategy.
        """
        problem = RectanglePacker(items, container_size)
        greedy_solver = Greedy(problem, RecPac_Solution, strategy_name)
        return greedy_solver.solve()
    
    def generate_instances(self, instance_count, rectangle_count, min_width, min_height, max_width, max_height):        
        """
        Generates rectangle instances for the test.
        """
        for _ in range(instance_count):
            self.instances.append(generate_instances(rectangle_count, min_width, max_width, min_height, max_height))

    def save_solutions(self):
        """
        Saves the solutions to a JSON file.
        """
        with open("test_env_solutions.json", "w") as f:
            obj = {"box_length": self.box_length, "solutions": []}
            
            def prepare_solution_data(solutions, algorithm_name):
                for solution in solutions:
                    current = {"boxes": [], "algorithm": algorithm_name}
                    for box in solution.boxes:
                        current_box = [{"x": rect.x, "y": rect.y, "w": rect.width, "h": rect.height} for rect in box.items]
                        current["boxes"].append(current_box)
                    obj["solutions"].append(current)
            
            prepare_solution_data(self.greedy_solutions, "greedy")
            prepare_solution_data(self.local_search_solutions, "local_search")
            
            json.dump(obj, f, indent=4)

    def create_protocol(self):
        """
        Creates and saves a protocol with all the test results.
        """
        if not os.path.exists("protocols"):
            os.makedirs("protocols")
        
        protocol_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_run_time": sum(self.times_greedy) + sum(self.times_local_search),
            "box_length": self.box_length,
            "greedy_strategy": self.greedy_strategy,
            "neighborhood": str(self.neighborhood.__class__.__name__) if not isinstance(self.neighborhood, int) else self.neighborhood,
            "max_iterations": self.max_iterations,
            "total_instances": len(self.instances),
            "solutions": []
        }
        
        def add_protocol_data(solutions, times, algorithm_name):
            for i, solution in enumerate(solutions):
                protocol_data["solutions"].append({
                    "algorithm": algorithm_name,
                    "instance": i + 1,
                    "num_boxes": len(solution.boxes),
                    "time": times[i]
                })
        
        add_protocol_data(self.greedy_solutions, self.times_greedy, "Greedy")
        add_protocol_data(self.local_search_solutions, self.times_local_search, "Local Search")
        
        file_name = f"protocols/protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_name, "w") as f:
            json.dump(protocol_data, f, indent=4)
        
        print(f"Protocol saved at: {file_name}")

if __name__ == "__main__":
    test_env = TestEnvironment()
    test_env.box_length = 100
    test_env.generate_instances(10, 150, 10, 15, 18, 23)
    test_env.greedy_strategy = GreedyStrategy.LARGEST_AREA_FIRST.value
    test_env.neighborhood = Neighborhoods.GEOMETRY.value
    test_env.max_iterations = 21
    test_env.run()
