import tkinter as tk
from view import GUI
from neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy
from problem import RectanglePacker
from algorithms import Greedy, LocalSearch
from helpers import generate_instances

def main():

    def greedy_algorithm(rectangles, box_length, strategy_name):
        if strategy_name == "largest_area_first":
            rectangles = sorted(rectangles, key=lambda r: r[2] * r[3], reverse=True)
        elif strategy_name == "smallest_area_first":
            rectangles = sorted(rectangles, key=lambda r: r[2] * r[3])
        elif strategy_name == "largest_aspect_ratio_first":
            rectangles = sorted(rectangles, key=lambda r: max(r[2] / r[3], r[3] / r[2]), reverse=True)
        elif strategy_name == "smallest_aspect_ratio_first":
            rectangles = sorted(rectangles, key=lambda r: max(r[2] / r[3], r[3] / r[2]))
        problem = RectanglePacker(rectangles, box_length)
        greedy_solver = Greedy(problem, strategy_name)
        return greedy_solver.solve()

    def local_search_algorithm(rectangles, box_length, neighborhood_name, max_iterations):
        neighborhood_map = {
            "Geometriebasiert": GeometryBasedStrategy(),
            "Regelbasiert": RuleBasedStrategy(),
            "Überlappungen teilweise zulassen": OverlapStrategy(initial_overlap=0.1)
        }
        problem = RectanglePacker(rectangles, box_length, neighborhood_map[neighborhood_name])
        local_search_solver = LocalSearch(problem, neighborhood_map[neighborhood_name], max_iterations)
        return local_search_solver.solve()

    root = tk.Tk()
    app = GUI(root, generate_instances, greedy_algorithm, local_search_algorithm)
    root.mainloop()

if __name__ == "__main__":
    main()
