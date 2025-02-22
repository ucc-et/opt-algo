import random
from typing import List

import numpy as np
from numba import njit

from base_classes.types import OptimizationProblem
from .neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy
from rectangle_packer_classes.problem_classes import Box, Rectangle, RecPac_Solution
from enum import Enum

#===================================
#               ENUMS
#===================================

class GreedyStrategy(Enum):
    """
    Enum for different greedy strategies in rectangle apcking
    """
    LARGEST_AREA_FIRST = "Größte Fläche zuerst"
    SMALLEST_AREA_FIRST = "Kleinste Fläche zuerst"
    LARGEST_ASPECT_RATIO_FIRST = "Größtes Seitenverhältnis zuerst"
    SMALLEST_ASPECT_RATIO = "Kleinstes Seitenverhältnis zuerst"
    
class Rules(Enum):
    """
    Enum for different rules to be used for rule-based neighborhodds in rectangle packing
    """
    HEIGHT_FIRST = "Absteigend nach Höhe"
    WIDTH_FIRST = "Absteigend nach Breite"
    AREA_FIRST = "Absteigend nach Fläche"
    
class Neighborhoods(Enum):
    """
    Enum for different neighborhoods for local-search approaches.
    """
    GEOMETRY = "Geometriebasiert"
    RULE = "Regelbasiert"
    OVERLAP = "Überlappungen teilweise zulassen"

@njit
def copy_numpy_array(array):
    """
    Quickly copies a NumPy array using Numba's JIT compilation.
    
    Args:
        array (np.ndarray): Input array to copy.
    
    Returns:
        np.ndarray: A deep copy of the input array.
    """
    copy = np.empty_like(array)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            copy[i, j] = array[i, j]
    return copy

def color_to_int(color):
    """
    Converts a color name to a unique integer.
    Ensures consistency in color preservation.
    """
    color_map = {
        "red": 1,
        "green": 2,
        "blue": 3,
        "yellow": 4,
        "purple": 5,
        "orange": 6,
        "cyan": 7
    }
    return color_map.get(color, 0) 

def int_to_color(color_int):
    """
    Converts an integer back to its corresponding color name.
    """
    int_map = {
        1: "red",
        2: "green",
        3: "blue",
        4: "yellow",
        5: "purple",
        6: "orange",
        7: "cyan"
    }
    return int_map.get(color_int, "black")  # Default to black if not found

def quick_copy(solution: RecPac_Solution):
    """
    Quickly creates a deep copy of the Solution object using NumPy and Numba.
    
    Args:
        solution (Solution): The solution object to be copied.
    
    Returns:
        Solution: A deep copy of the input solution.
    """
    # Step 1: Extract data into NumPy arrays
    boxes_data = []
    for box in solution.boxes:
        items_data = np.array([[rect.x, rect.y, rect.width, rect.height, color_to_int(rect.color)] for rect in box.items], dtype=np.int32)
        boxes_data.append(items_data)

    # Step 2: Copy data using Numba for speed
    copied_boxes_data = [copy_numpy_array(data) for data in boxes_data]
    
    # Step 3: Reconstruct Solution object
    new_solution = solution.__class__()  # Dynamically create a new Solution object
    for box_data in copied_boxes_data:
        new_box = Box(solution.boxes[0].box_length)  # Assume uniform box length
        for rect_data in box_data:
            x, y, w, h, c = rect_data
            new_box.add_item(Rectangle(x, y, w, h, int_to_color(c)))
        new_solution.add_box(new_box)
    
    return new_solution

def merge_geometry_based_solutions(problem, neighborhood_name, items, container_size, rulebased_strategy, greedy_algorithm_runner):
    """
    Merges solutions into one solution, providing a good starting solution for most local searches

    Args:
        problem (OptimizationProblem): optimization problem instance
        neighborhood_name (str): name of neighborhood strategy
        items (list[Rectangle]): list of rectangles
        container_size (int): size of the container
        rulebased_strategy (str): strategy name of the rule-based strategy
        greedy_algorithm_runner (function): greedy algorithm function for quick starting solutions

    Returns:
        tuple: (start_solution, neighborhood) where start_solution is the merged solution and neighborhood is the corresponding neighborhood strategy
    """
    start_solution = RecPac_Solution()
    sub_lists, neighborhood = get_neighborhood_and_start_solution(problem, neighborhood_name, items, container_size, rulebased_strategy, greedy_algorithm_runner)
    
    # apply the greedy algorith  to each rectangle sublist and merge all solutions at the end
    for sub_list in sub_lists:
        temp_sol, _ = greedy_algorithm_runner(sub_list, container_size, GreedyStrategy.LARGEST_AREA_FIRST.value)
        for box in temp_sol.boxes:
            start_solution.add_box(box)
    return start_solution, neighborhood

def get_neighborhood_and_start_solution(problem: OptimizationProblem, neighborhood_name, items, container_size, rulebased_strategy, greedy_algorithm_runner):
    """Returns the initial solution and the neighborhood strategy for the given problem

    Args:
        problem (OptimizationProblem): optimization problem instance
        neighborhood_name (str): name of neighborhood strategy
        items (list[Rectangle]): list of rectangles
        container_size (int): size of the container
        rulebased_strategy (str): strategy name of the rule-based strategy
        greedy_algorithm_runner (function): greedy algorithm function for quick starting solutions

    Returns:
        tuple: (start_solution, neighborhood) for the selected strategy.
    """
    
    # intial solutions for each neighborhood strategy
    start_solution_map = {
        "Geometriebasiert": lambda: problem.generate_item_samples(items),
        "Regelbasiert": lambda: greedy_algorithm_runner(items, container_size, GreedyStrategy.LARGEST_AREA_FIRST.value)[0],
        "Überlappungen teilweise zulassen": lambda: problem.generate_initial_solution(items, container_size),
    }
    
    # neighborhood mapping
    neighborhood_map = {
        "Geometriebasiert": GeometryBasedStrategy(problem, RecPac_Solution),
        "Regelbasiert": RuleBasedStrategy(problem, rulebased_strategy),
        "Überlappungen teilweise zulassen": OverlapStrategy(problem)
    }
    return start_solution_map[neighborhood_name](), neighborhood_map[neighborhood_name]

def generate_instances(n, min_width, max_width, min_height, max_height, possible_colors) -> List[Rectangle]:
    """
        Generates a list of rectangle instances with random dimensions.
        
        Args:
            n (int): Number of rectangles to generate.
            min_width (int): Minimum width for rectangles.
            max_width (int): Maximum width for rectangles.
            min_height (int): Minimum height for rectangles.
            max_height (int): Maximum height for rectangles.
        
        Returns:
         List[Rectangle]: List of generated rectangle instances.
    """
    instances = []
    for _ in range(n):
        random_width = random.randint(min_width, max_width)
        random_height = random.randint(min_height, max_height)
        color = random.choice(possible_colors)
        rect = Rectangle(None, None, random_width, random_height, color)
        instances.append(rect)

    return instances

def apply_greedy_strategy(items, strategy_name):
    """
    Applies a greedy strategy to provided items.
    
    Args:
        items (list[Rectangle]): List of rectangles to be sorted.
        strategy_name (str): Greedy strategy name.
    
    Returns:
        list[Rectangle]: Sorted list of rectangles.
    """
    if strategy_name == GreedyStrategy.LARGEST_AREA_FIRST.value:
        items = sorted(items, key=lambda i: i.width * i.height, reverse=True)
    elif strategy_name == GreedyStrategy.SMALLEST_AREA_FIRST.value:
        items = sorted(items, key=lambda i: i.width * i.height)
    elif strategy_name == GreedyStrategy.LARGEST_ASPECT_RATIO_FIRST.value:
        items = sorted(items, key=lambda i: max(i.width / i.height, i.height / i.width), reverse=True)
    elif strategy_name == GreedyStrategy.SMALLEST_ASPECT_RATIO.value:
        items = sorted(items, key=lambda i: max(i.width / i.height, i.height / i.width))
        
    return items

def apply_rule(items, rule_name):
    """
    Applies a rule-based strategy to reorder rectangles.
    
    Args:
        items (list[Rectangle]): List of rectangles to be reordered.
        rule_name (str): Rule-based strategy name.
    
    Returns:
        list[Rectangle]: Reordered list of rectangles.
    """
    if rule_name == Rules.HEIGHT_FIRST.value:
        return sorted(items, key=lambda item: item.height, reverse=True)
    elif rule_name == Rules.AREA_FIRST.value:
        return sorted(items, key=lambda item: item.height*item.width, reverse=True)
    elif rule_name == Rules.WIDTH_FIRST.value:
        return sorted(items, key=lambda item: item.width, reverse=True)
