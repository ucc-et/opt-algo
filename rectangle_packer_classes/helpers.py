import random
from typing import List

from base_classes.types import OptimizationProblem
from .neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy
from rectangle_packer_classes.problem_classes import Rectangle, RecPac_Solution
from enum import Enum

class GreedyStrategy(Enum):
    LARGEST_AREA_FIRST = "Größte Fläche zuerst"
    SMALLEST_AREA_FIRST = "Kleinste Fläche zuerst"
    LARGEST_ASPECT_RATIO_FIRST = "Größtes Seitenverhältnis zuerst"
    SMALLEST_ASPECT_RATIO = "Kleinstes Seitenverhältnis zuerst"
    
class Rules(Enum):
    HEIGHT_FIRST = "Absteigend nach Höhe"
    WIDTH_FIRST = "Absteigend nach Breite"
    AREA_FIRST = "Absteigend nach Fläche"
    
class Neighborhoods(Enum):
    GEOMETRY = "Geometriebasiert"
    RULE = "Regelbasiert"
    OVERLAP = "Überlappung teilweise zulassen"


def merge_geometry_based_solutions(problem, neighborhood_name, items, container_size, rulebased_strategy, greedy_algorithm_runner):
        start_solution = RecPac_Solution()
        sub_lists, neighborhood = get_neighborhood_and_start_solution(problem, neighborhood_name, items, container_size, rulebased_strategy, greedy_algorithm_runner)
        for sub_list in sub_lists:
            temp_solt = greedy_algorithm_runner(sub_list, container_size, GreedyStrategy.LARGEST_AREA_FIRST.value)
            for box in temp_solt.boxes:
                start_solution.add_box(box)
        return start_solution, neighborhood

def get_neighborhood_and_start_solution(problem: OptimizationProblem, neighborhood_name, items, container_size, rulebased_strategy, greedy_algorithm_runner):
        start_solution_map = {
            "Geometriebasiert": problem.generate_item_samples(items),
            "Regelbasiert": greedy_algorithm_runner(items, container_size, GreedyStrategy.LARGEST_AREA_FIRST.value),
            "Überlappungen teilweise zulassen": problem.generate_initial_solution(items, container_size),
        }
        neighborhood_map = {
            "Geometriebasiert": GeometryBasedStrategy(problem, RecPac_Solution),
            "Regelbasiert": RuleBasedStrategy(problem, rulebased_strategy),
            "Überlappungen teilweise zulassen": OverlapStrategy(problem)
        }
        return start_solution_map[neighborhood_name], neighborhood_map[neighborhood_name]

def generate_instances(n, min_width, max_width, min_height, max_height) -> List[Rectangle]:
    instances = []
    for _ in range(n):
        random_width = random.randint(min_width, max_width)
        random_height = random.randint(min_height, max_height)
        rect = Rectangle(None, None, random_width, random_height)
        instances.append(rect)

    return instances

def apply_greedy_strategy(items, strategy_name):
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
    if rule_name == Rules.HEIGHT_FIRST.value:
        return sorted(items, key=lambda item: item.height, reverse=True)
    elif rule_name == Rules.AREA_FIRST.value:
        return sorted(items, key=lambda item: item.height*item.width, reverse=True)
    elif rule_name == Rules.WIDTH_FIRST.value:
        return sorted(items, key=lambda item: item.width, reverse=True)
