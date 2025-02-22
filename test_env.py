import copy
import json
import time
from datetime import datetime
import os

from base_classes.algorithms import Greedy, LocalSearch, Backtracking, SimulatedAnnealing
from rectangle_packer_classes.helpers import apply_greedy_strategy, generate_instances, GreedyStrategy, Neighborhoods, merge_geometry_based_solutions, get_neighborhood_and_start_solution, quick_copy
from rectangle_packer_classes.problem_classes import Box, RecPac_Solution, RectanglePacker

class TestEnvironment:
    """
    A class to manage the test environment for optimization algorithms.
    """
    def __init__(self):
        self.box_length = -1
        self.max_iterations = 21
        self.instances = []
        
        self.greedy_solutions = []
        self.local_search_solutions = []
        self.backtracking_solutions = []
        self.sim_annealing_solutions = []
        
        self.times_greedy = []
        self.times_local_search = []
        self.times_backtracking = []
        self.times_sim_annealing = []

    def run(self):
        """
        Main entry point for running all tests.
        Runs Greedy with all strategies, Local Search with all neighborhoods, 
        and Backtracking & Simulated Annealing once.
        """
        print("\nRunning All Tests...")
        
        # Run Greedy with all strategies
        self.run_greedy()
        
        # Run Local Search with all neighborhoods
        self.run_local_search()
        
        # Run Backtracking
        self.run_backtracking()
        
        # Run Simulated Annealing
        self.run_simulated_annealing()
        
        # Save all solutions and create protocol
        self.save_solutions()
        self.create_protocol()
        
        self.extract_solutions_for_viewer()

    def run_greedy(self):
        """
        Runs the greedy algorithm with all strategies on all instances.
        """
        print("\nStarting Greedy Algorithm...")
        for strategy in GreedyStrategy:
            for i, instance_set in enumerate(self.instances):
                start_time = time.time()
                instance_set_copy = copy.deepcopy(instance_set)
                instance_set_copy = apply_greedy_strategy(instance_set_copy, strategy.value)
                
                problem = RectanglePacker(instance_set_copy, self.box_length)
                solver = Greedy(problem, RecPac_Solution, apply_greedy_strategy, strategy.value, True)
                solution, interim_solutions = solver.solve()
                
                self.times_greedy.append(time.time() - start_time)
                self.greedy_solutions.append({
                    "strategy": strategy.value,
                    "solution": solution,
                    "interim_solutions": interim_solutions
                })
        print("\nGreedy Algorithm Completed.")

    def greedy_runner(self, items, container_size, strategy_name):
        """
        Utility function to run the Greedy algorithm with the given strategy.
        """
        problem = RectanglePacker(items, container_size)
        greedy_solver = Greedy(problem, RecPac_Solution, apply_greedy_strategy, strategy_name, True)
        solution, interim_solutions = greedy_solver.solve()
        return solution, interim_solutions

    def run_local_search(self):
        """
        Runs the local search algorithm with all neighborhoods on all instances.
        """
        print("\nStarting Local Search...")
        for neighborhood in Neighborhoods:
            for i, instance_set in enumerate(self.instances):
                instance_set_copy = copy.deepcopy(instance_set)
                problem = RectanglePacker(instance_set_copy, self.box_length)
                
                if neighborhood.value == Neighborhoods.GEOMETRY.value:
                    start_solution, neighborhood_strategy = merge_geometry_based_solutions(problem, neighborhood.value, instance_set_copy, self.box_length, "", self.greedy_runner)
                else:
                    start_solution, neighborhood_strategy = get_neighborhood_and_start_solution(problem, neighborhood.value, instance_set_copy, self.box_length, "", self.greedy_runner)
                
                solver = LocalSearch(problem, start_solution, self.max_iterations, neighborhood_strategy, True)
                start_time = time.time()
                solution = solver.solve()
                
                self.times_local_search.append(time.time() - start_time)
                self.local_search_solutions.append({
                    "neighborhood": neighborhood.value,
                    "solution": solution
                })
        print("\nLocal Search Completed.")

    def run_backtracking(self):
        """
        Runs the backtracking algorithm on all instances.
        """
        print("\nStarting Backtracking...")
        for i, instance_set in enumerate(copy.deepcopy(self.instances)):
            problem = RectanglePacker(instance_set, self.box_length)
            solver = Backtracking(problem, RecPac_Solution, True)
            start_time = time.time()
            solution = solver.solve()
            
            self.times_backtracking.append(time.time() - start_time)
            self.backtracking_solutions.append({
                "solution": solution
            })
        print("\nBacktracking Completed.")

    def run_simulated_annealing(self):
        """
        Runs the simulated annealing algorithm on all instances.
        """
        print("\nStarting Simulated Annealing...")
        for i, instance_set in enumerate(self.instances):
            problem = RectanglePacker(instance_set, self.box_length)
            start_solution, neighborhood = merge_geometry_based_solutions(problem, Neighborhoods.GEOMETRY.value, instance_set, self.box_length, "", self.greedy_runner)
            
            solver = SimulatedAnnealing(
                problem=problem,
                start_solution=start_solution,
                initial_temperature=1000,
                end_temperature=25,
                cooling_rate=0.95,
                iterations_per_temp=10,
                neighborhood_strategy=neighborhood,
                in_test_env=True
            )
            start_time = time.time()
            solution = solver.solve()
            
            self.times_sim_annealing.append(time.time() - start_time)
            self.sim_annealing_solutions.append({
                "solution": solution
            })
        print("\nSimulated Annealing Completed.")

    def generate_instances(self, instance_count, rectangle_count, min_width, min_height, max_width, max_height):        
        """
        Generates rectangle instances for the test.
        """
        for _ in range(instance_count):
            self.instances.append(generate_instances(rectangle_count, min_width, max_width, min_height, max_height, ["blue", "yellow"]))

    def calculate_covered_area(self, box):
        """
        Calculates the percentage of the box area covered by the rectangles.
        Returns:
            float: Covered area in percentage
        """
        total_box_area = self.box_length ** 2
        covered_by_items = 0

        for item in box.items:
            covered_by_items += item.width * item.height

        return (covered_by_items / total_box_area) * 100

    def save_solutions(self):
        """
        Saves all solutions to a JSON file for further analysis.
        Organized by algorithm and strategy/neighborhood.
        """
        if not os.path.exists("solutions"):
            os.makedirs("solutions")
        
        # Struktur für die JSON-Ausgabe
        solution_data = {
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "box_length": self.box_length,
            "instances": len(self.instances),
            "rectangles_per_instance": len(self.instances[0]),
            "solutions": []
        }
        
        def prepare_solution_data(solutions, algorithm_name):
            for solution_dict in solutions:
                solution = solution_dict["solution"]
                if isinstance(solution, tuple):
                    solution = solution[0]  # Falls es ein Tuple ist, den ersten Wert nehmen
                
                # Metadaten zu Algorithmus und Strategie/Nachbarschaft
                solution_metadata = {
                    "algorithm": algorithm_name,
                    "strategy": solution_dict.get("strategy"),
                    "neighborhood": solution_dict.get("neighborhood"),
                    "boxes": [],
                }
                
                # Lösung analysieren
                for box in solution.boxes:
                    box_data = []
                    for rect in box.items:
                        box_data.append({
                            "x": int(rect.x),
                            "y": int(rect.y),
                            "w": int(rect.width),
                            "h": int(rect.height)
                        })
                    solution_metadata["boxes"].append(box_data)
                
                # Statistiken berechnen
                solution_metadata["num_boxes"] = len(solution.boxes)
                solution_metadata["utilization"] = [self.calculate_covered_area(box) for box in solution.boxes]
                solution_metadata["overlap_percentage"] = 0  # Hier ggf. Berechnung hinzufügen
                
                solution_data["solutions"].append(solution_metadata)
        
        # Lösungen für alle Algorithmen speichern
        prepare_solution_data(self.greedy_solutions, "Greedy")
        prepare_solution_data(self.local_search_solutions, "Local Search")
        prepare_solution_data(self.backtracking_solutions, "Backtracking")
        prepare_solution_data(self.sim_annealing_solutions, "Simulated Annealing")
        
        # Speichern in JSON-Datei
        file_name = f"solutions/solutions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(solution_data, f, indent=4, ensure_ascii=False)
        
        print(f"Solutions saved at: {file_name}")

    def create_protocol(self):
        """
        Creates a detailed JSON protocol for all test results.
        Organized by algorithm, strategy, neighborhood, and instance.
        """
        if not os.path.exists("protocols"):
            os.makedirs("protocols")
        
        # Struktur für die JSON-Ausgabe
        protocol_data = {
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "box_length": self.box_length,
            "instances": len(self.instances),
            "rectangles_per_instance": len(self.instances[0]),
            "algorithms": []
        }
        
        def add_protocol_data(solutions, times, algorithm_name):
            for i, solution_dict in enumerate(solutions):
                solution = solution_dict["solution"]
                if isinstance(solution, tuple):
                    solution = solution[0]  # Falls es ein Tuple ist, den ersten Wert nehmen
                
                # Flächenauslastung berechnen
                utilization = [self.calculate_covered_area(box) for box in solution.boxes]

                # Strukturierte Speicherung der Daten
                protocol_data["algorithms"].append({
                    "algorithm": algorithm_name,
                    "instance": i + 1,
                    "num_boxes": len(solution.boxes),
                    "time": times[i],
                    "utilization": utilization,
                    "strategy": solution_dict.get("strategy"),
                    "neighborhood": solution_dict.get("neighborhood")
                })
        
        # Lösungen für alle Algorithmen protokollieren
        add_protocol_data(self.greedy_solutions, self.times_greedy, "Greedy")
        add_protocol_data(self.local_search_solutions, self.times_local_search, "Local Search")
        add_protocol_data(self.backtracking_solutions, self.times_backtracking, "Backtracking")
        add_protocol_data(self.sim_annealing_solutions, self.times_sim_annealing, "Simulated Annealing")
        
        # Speichern in JSON-Datei
        file_name = f"protocols/protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(protocol_data, f, indent=4, ensure_ascii=False)
        
        print(f"Protocol saved at: {file_name}")

    def extract_solutions_for_viewer(self):
        """
        Extracts solutions for the solution viewer.
        Organized by algorithm, strategy, and neighborhood.
        """
        if not os.path.exists("viewer_solutions"):
            os.makedirs("viewer_solutions")
        
        viewer_data = {
            "box_length": self.box_length,
            "solutions": []
        }
        
        def generate_color(rect):
            """
            Generates a consistent color for each rectangle.
            """
            color_choices = ["red", "green", "blue", "yellow", "purple", "orange", "cyan"]
            # Color is chosen based on rectangle dimensions to ensure consistency
            return color_choices[(rect.width * rect.height) % len(color_choices)]
        
        def add_viewer_data(solutions, algorithm_name):
            for solution_dict in solutions:
                solution = solution_dict["solution"]
                interim_solutions = solution_dict.get("interim_solutions", [])
                if isinstance(solution, tuple):
                    solution = solution[0]  # Get the first element if it's a tuple
                
                # Extract metadata
                solution_metadata = {
                    "algorithm": algorithm_name,
                    "strategy": solution_dict.get("strategy"),
                    "neighborhood": solution_dict.get("neighborhood"),
                    "boxes": [],
                    "interim_solutions": []
                }
                
                # Extract the final solution
                for box in solution.boxes:
                    box_data = []
                    for rect in box.items:
                        box_data.append({
                            "x": int(rect.x),
                            "y": int(rect.y),
                            "w": int(rect.width),
                            "h": int(rect.height),
                            "color": generate_color(rect)
                        })
                    solution_metadata["boxes"].append(box_data)
                
                # Extract interim solutions for step-by-step viewing
                for interim_solution in interim_solutions:
                    interim_boxes = []
                    for box in interim_solution.boxes:
                        box_data = []
                        for rect in box.items:
                            box_data.append({
                                "x": rect.x,
                                "y": rect.y,
                                "w": rect.width,
                                "h": rect.height,
                                "color": generate_color(rect)
                            })
                        interim_boxes.append(box_data)
                    solution_metadata["interim_solutions"].append(interim_boxes)
                
                viewer_data["solutions"].append(solution_metadata)
        
        # Extract data for all algorithms
        add_viewer_data(self.greedy_solutions, "Greedy")
        add_viewer_data(self.local_search_solutions, "Local Search")
        add_viewer_data(self.backtracking_solutions, "Backtracking")
        add_viewer_data(self.sim_annealing_solutions, "Simulated Annealing")
        
        # Save the extracted data
        file_name = f"viewer_solutions/solutions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(viewer_data, f, indent=4, ensure_ascii=False)
        
        print(f"Solutions extracted for viewer at: {file_name}")


if __name__ == "__main__":
    test_env = TestEnvironment()
    test_env.box_length = 100
    
    # Schnell und für die Abnahme:
    test_env.generate_instances(5, 1000, 2, 3, 7, 9)
    
    # Aussagekräftig für Protokoll:
    # test_env.generate_instances(10, 150, 10, 15, 18, 23)
    
    test_env.max_iterations = 21
    test_env.run()
