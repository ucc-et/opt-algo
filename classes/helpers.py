import random
from typing import List

from classes import Rectangle
from solvers.enums import Rules

def generate_instances(n, min_width, max_width, min_height, max_height) -> List[Rectangle]:

    instances = []
    for _ in range(n):
        random_width = random.randint(min_width, max_width)
        random_height = random.randint(min_height, max_height)
        rect = Rectangle(None, None, random_width, random_height)
        instances.append(rect)

    return instances

def apply_greedy_strategy(items, strategy_name):
    if strategy_name == "Größte Fläche zuerst":
        items = sorted(items, key=lambda i: i.width * i.height, reverse=True)
    elif strategy_name == "Kleinste Fläche zuerst":
        items = sorted(items, key=lambda i: i.width * i.height)
    elif strategy_name == "Größtes Seitenverhältnis zuerst":
        items = sorted(items, key=lambda i: max(i.width / i.height, i.height / i.width), reverse=True)
    elif strategy_name == "Kleinstes Seitenverhältnis zuerst":
        items = sorted(items, key=lambda i: max(i.width / i.height, i.height / i.width))
        
    return items

def apply_rule(items, rule_name):
    if rule_name == Rules.HEIGHT_FIRST:
        return sorted(items, key=lambda item: item.height, reverse=True)
    elif rule_name == Rules.AREA_FIRST:
        return sorted(items, key=lambda item: item.height*item.width, reverse=True)
    elif rule_name == Rules.WIDTH_FIRST:
        return sorted(items, key=lambda item: item.width, reverse=True)
