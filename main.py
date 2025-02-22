import tkinter as tk

from base_classes.algorithms import Greedy, LocalSearch, Backtracking, SimulatedAnnealing
from rectangle_packer_classes.helpers import get_neighborhood_and_start_solution, merge_geometry_based_solutions, GreedyStrategy, Neighborhoods, apply_greedy_strategy
from rectangle_packer_classes.problem_classes import RectanglePacker, RecPac_Solution, Box
from rectangle_packer_classes.rectangle_packer_viewer import RectanglePackerVisualizer


def main():
    
    def greedy_runner(items, container_size, strategy_name):
        problem = RectanglePacker(items, container_size)
        greedy_solver = Greedy(problem, RecPac_Solution, apply_greedy_strategy, strategy_name)
        return greedy_solver.solve()

    def local_search_runner(items, container_size, neighborhood_name, strategy_rulebased, max_iterations=21):
        problem = RectanglePacker(items, container_size)
        if neighborhood_name == Neighborhoods.GEOMETRY.value:
            start_solution, neighborhood = merge_geometry_based_solutions(problem, neighborhood_name, items, container_size, strategy_rulebased, greedy_runner)
        else:
            start_solution, neighborhood = get_neighborhood_and_start_solution(problem, neighborhood_name, items, container_size, strategy_rulebased, greedy_runner)
        local_search_solver = LocalSearch(problem, start_solution, max_iterations, neighborhood)
        solution = local_search_solver.solve()
        return solution

    def backtracking_runner(items, container_size):
        problem = RectanglePacker(items, container_size)
        backtracking_solver = Backtracking(problem ,RecPac_Solution)
        solution = backtracking_solver.solve()
        return solution

    def simulated_annealing_runner(items, container_size, neighborhood_name, strategy_rulebased, initial_temperature=1000, end_temperature=25, cooling_rate=0.95, iterations_per_temp=10, max_time=10):
        problem = RectanglePacker(items, container_size)

        start_solution, neighborhood = merge_geometry_based_solutions(problem, neighborhood_name, items, container_size, strategy_rulebased, greedy_runner)

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

    

    root = tk.Tk()
    app = RectanglePackerVisualizer(root, greedy_runner, local_search_runner, backtracking_runner, simulated_annealing_runner)
    root.mainloop()


if __name__ == "__main__":
    main()
