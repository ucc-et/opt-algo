import tkinter as tk
import random

from algorithms import Greedy, LocalSearch, Backtracking
from neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy
from objects import RecPac_Solution, Box
from problem import RectanglePacker
from strategy import apply_strategy
from view import GUI


def main():
    def greedy_algorithm(items, container_size, strategy_name):
        items = apply_strategy(items, strategy_name)
        problem = RectanglePacker(items, container_size)
        greedy_solver = Greedy(problem, RecPac_Solution, strategy_name)
        return greedy_solver.solve()

    def local_search_algorithm(items, container_size, neighborhood_name, strategy_rulebased="", max_iterations=20):
        problem = RectanglePacker(items, container_size)
        
        start_solution_map = {
            "Geometriebasiert": problem.generate_initial_solution(items, container_size),
            "Regelbasiert": greedy_algorithm(items, container_size, "Größte Fläche zuerst"),
        }
        neighborhood_map = {
            "Geometriebasiert": GeometryBasedStrategy(problem),
            "Regelbasiert": RuleBasedStrategy(problem, strategy_rulebased),
            "Überlappungen teilweise zulassen": OverlapStrategy(initial_overlap=0.1)
        }
        local_search_solver = LocalSearch(problem, start_solution_map[neighborhood_name], max_iterations, neighborhood_map[neighborhood_name])
        return local_search_solver.solve()

    def backtracking_algorithm(items, container_size):
        problem = RectanglePacker(items, container_size)
        backtracking_solver = Backtracking(problem)
        solution = backtracking_solver.solve()
        return solution

    root = tk.Tk()
    app = GUI(root, greedy_algorithm, local_search_algorithm, backtracking_algorithm)
    root.mainloop()


if __name__ == "__main__":
    main()
