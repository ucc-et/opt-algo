import random
from typing import List

from classes import Rectangle

def generate_instances(n, min_width, max_width, min_height, max_height) -> List[Rectangle]:
    """
    Generate rectangle Instances.
    n: amount of rectangles that will be generated
    min_width: A rectangle has to have a width that is bigger or equals min_width
    max_width: A rectangle has to have a width that is smaller or equals max_width
    min_height: A rectangle has to have a height that is bigger or equals min_height
    max_height: A rectangle has to have a height that is smaller or equals max_height
    """
    
    instances = []
    for _ in range(n):
        random_width = random.randint(min_width, max_width)
        random_height = random.randint(min_height, max_height)
        rect = Rectangle(None, None, random_width, random_height)
        instances.append(rect)

    return instances
