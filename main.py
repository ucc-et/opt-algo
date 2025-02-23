import tkinter as tk

from base_classes.algorithms import Greedy, LocalSearch, Backtracking, SimulatedAnnealing
from rectangle_packer_classes.helpers import get_neighborhood_and_start_solution, merge_geometry_based_solutions, GreedyStrategy, Neighborhoods, apply_greedy_strategy
from rectangle_packer_classes.problem_classes import RectanglePacker, RecPac_Solution
from rectangle_packer_classes.rectangle_packer_viewer import RectanglePackerVisualizer


def main():
    
    def greedy_runner(items, container_size, strategy_name):
        """
        Runs the greedy algorithm for rectangle packing.

        Args:
            items (list[Rectangle]): List of the rectangles that will be packed into the containers
            container_size (int): Size of the container box 
            strategy_name (str): Name of the greedy strategy that will be used

        Returns:
            RecPac_Solution: Object that represents a solution for the rectangle packer.
        """
        problem = RectanglePacker(items, container_size)
        greedy_solver = Greedy(problem, RecPac_Solution, apply_greedy_strategy, strategy_name, False)
        end_solution, interim_solutions = greedy_solver.solve()
        return end_solution, interim_solutions

    def local_search_runner(items, container_size, neighborhood_name, strategy_rulebased, max_iterations=21):
        """
        Runs the local search algorithm for rectangle packing.

        Args:
            items (list[Rectangle]): List of the rectangles that will be packed into the containers
            container_size (int): Size of the container box
            neighborhood_name (str): Name of the chosen neighborhood strategy
            strategy_rulebased (str): Chosen strategy that will be used, when the neighborhood 'rule-based' is chosen
            max_iterations (int, optional): Maximum number of iterations for local search. Defaults to 21

        Returns:
            RecPac_Solution: Object that represents a solution for the rectangle packer.
        """
        problem = RectanglePacker(items, container_size)
        
        # determine start solution and neighborhood strategy based on neighborhood. If its the geometery based neighborhood, it will generate the start_solution differently, to get better results
        if neighborhood_name == Neighborhoods.GEOMETRY.value:
            start_solution, neighborhood = merge_geometry_based_solutions(problem, neighborhood_name, items, container_size, strategy_rulebased, greedy_runner)
        else:
            start_solution, neighborhood = get_neighborhood_and_start_solution(problem, neighborhood_name, items, container_size, strategy_rulebased, greedy_runner)
        local_search_solver = LocalSearch(problem, start_solution, max_iterations, neighborhood, False)
        solution, interim_solutions = local_search_solver.solve()
        return solution, interim_solutions

    def backtracking_runner(items, container_size):
        """
        Runs Backtracking algorithm for rectangle packing.
        
        Args:
            items (list[Rectangle]): List of the rectangles that will be packed into the containers
            container_size (int): Size of the container box
        
        Returns:
            RecPac_Solution: Object that represents a solution for the rectangle packer.
        """
        problem = RectanglePacker(items, container_size)
        backtracking_solver = Backtracking(problem ,RecPac_Solution, False)
        solution, interim_solutions = backtracking_solver.solve()
        return solution, interim_solutions

    def simulated_annealing_runner(items, container_size, neighborhood_name=Neighborhoods.GEOMETRY.value, strategy_rulebased="", initial_temperature=1000, end_temperature=25, cooling_rate=0.95, iterations_per_temp=10, max_time=10):
        """
        Runs Simulated Annealing algorithm for rectangle packing.
        
        Args:
            items (list[Rectangle]): List of the rectangles that will be packed into the containers.
            container_size (int): Size of the container box.
            neighborhood_name (str): Name of the neighborhood strategy.
            strategy_rulebased (str): Chosen strategy that will be used, when the neighborhood 'rule-based' is chosen
            initial_temperature (float): Initial temperature for annealing algorithm.
            end_temperature (float): Temperature that will stop algorithm if reached.
            cooling_rate (float): Cooling rate for temperature reduction.
            iterations_per_temp (int): Amount of iterations, that the temperature will be constant for.
            max_time (int): Maximum allowed time for the algorithm.
        
        Returns:
            RecPac_Solution: Object that represents a solution for the rectangle packer.
        """
        problem = RectanglePacker(items, container_size)

        start_solution, neighborhood = merge_geometry_based_solutions(problem, neighborhood_name, items, container_size, strategy_rulebased, greedy_runner)

        simulated_annealing_solver = SimulatedAnnealing(
            problem=problem,
            start_solution=start_solution,
            initial_temperature=initial_temperature,
            end_temperature=end_temperature,
            cooling_rate=cooling_rate,
            iterations_per_temp=iterations_per_temp,
            neighborhood_strategy=neighborhood,
            in_test_env=False
        )
        solution, interim_solutions = simulated_annealing_solver.solve()
        return solution, interim_solutions

    
    # init tkinter root window and the visualizer application
    root = tk.Tk()
    app = RectanglePackerVisualizer(root, greedy_runner, local_search_runner, backtracking_runner, simulated_annealing_runner)
    root.mainloop()


if __name__ == "__main__":
    main()
