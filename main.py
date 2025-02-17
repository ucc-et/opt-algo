import random
import tkinter as tk

from classes.base_classes import OptimizationProblem
from solvers.algorithms import Greedy, LocalSearch, Backtracking, SimulatedAnnealing
from solvers.enums import GreedyStrategy
from solvers.neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy
from classes.rectangle_packer_types import RectanglePacker, RecPac_Solution, Box
from view import RectanglePackerVisualizer

from classes import RecPac_Solution, RectanglePacker


def main():
    
    def get_neighborhood_and_start_solution(problem: OptimizationProblem, neighborhood_name, items, container_size, rulebased_strategy):
        start_solution_map = {
            "Geometriebasiert": problem.generate_initial_solution(items, container_size),
            "Regelbasiert": greedy_algorithm(items, container_size, GreedyStrategy.LARGEST_AREA_FIRST.value),
            "Überlappungen teilweise zulassen": generate_bad_solution_overlapping(items, container_size),
        }
        neighborhood_map = {
            "Geometriebasiert": GeometryBasedStrategy(problem, RecPac_Solution),
            "Regelbasiert": RuleBasedStrategy(problem, rulebased_strategy),
            "Überlappungen teilweise zulassen": OverlapStrategy(problem)
        }
        return start_solution_map[neighborhood_name], neighborhood_map[neighborhood_name]
    
    def greedy_algorithm(items, container_size, strategy_name):
        problem = RectanglePacker(items, container_size)
        greedy_solver = Greedy(problem, RecPac_Solution, strategy_name)
        return greedy_solver.solve()

    def local_search_algorithm(items, container_size, neighborhood_name, strategy_rulebased="", max_iterations=20):
        problem = RectanglePacker(items, container_size)
        start_solution, neighborhood = get_neighborhood_and_start_solution(problem, neighborhood_name, items, container_size, strategy_rulebased)
        local_search_solver = LocalSearch(problem, start_solution, max_iterations, neighborhood)
        return local_search_solver.solve()

    def backtracking_algorithm(items, container_size):
        problem = RectanglePacker(items, container_size)
        backtracking_solver = Backtracking(problem ,RecPac_Solution)
        solution = backtracking_solver.solve()
        return solution

    def simulated_annealing_algorithm(items, container_size, neighborhood_name, strategy_rulebased, initial_temperature=1000, end_temperature=1, cooling_rate=0.95, iterations_per_temp=10):
        problem = RectanglePacker(items, container_size)

        start_solution, neighborhood = get_neighborhood_and_start_solution(problem, neighborhood_name, items, container_size, strategy_rulebased)

        simulated_annealing_solver = SimulatedAnnealing(
            problem=problem,
            start_solution=start_solution,
            initial_temperature=initial_temperature,
            end_temperature=end_temperature,
            cooling_rate=cooling_rate,
            iterations_per_temp=iterations_per_temp,
            neighborhood_strategy=neighborhood
        )

        return simulated_annealing_solver.solve()

    def generate_bad_solution_overlapping(items, box_length):
        bad_solution = RecPac_Solution()
        new_box = Box(box_length)
        for item in items:
            item.x = 0
            item.y = 0
            new_box.add_rectangle(item)

        bad_solution.add_box(new_box)
        return bad_solution

    root = tk.Tk()
    app = RectanglePackerVisualizer(root, greedy_algorithm, local_search_algorithm, backtracking_algorithm, simulated_annealing_algorithm)
    root.mainloop()


if __name__ == "__main__":
    main()
