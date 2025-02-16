from abc import ABC, abstractmethod
from typing import List
import random

import numpy as np
from numba import njit

from objects import Box, Container, Item, RecPac_Solution, Rectangle


class OptimizationProblem(ABC):
    @abstractmethod
    def add_to_solution(self, *args):
        pass

    @abstractmethod
    def find_valid_assignment(self, *args):
        pass
    
    @abstractmethod
    def generate_initial_solution(self, *args):
        pass


@njit
def detect_item_invalidity(x, y, width, height, item_x, item_y, item_width, item_height):
    """Fast overlap check using Numba"""
    return not (x >= item_x + item_width or x + width <= item_x or
                y >= item_y + item_height or y + height <= item_y)

@njit
def find_valid_assignment_numba(container_size, items_x, items_y, items_width, items_height,
                                   item_width, item_height):
    """Fast brute-force search for a valid rectangle position"""
    for y in range(container_size - item_width + 1):
        for x in range(container_size - item_height + 1):
            fits = True
            for i in range(len(items_x)):  # Check all existing rectangles
                if detect_item_invalidity(x, y, item_width, item_height,
                                   items_x[i], items_y[i],
                                   items_width[i], items_height[i]):
                    fits = False
                    break  # If overlap, stop checking
            if fits:
                return x, y  # Found a valid position

    return -1, -1  # No valid position found


class RectanglePacker(OptimizationProblem):

    def __init__(self, items: List[Rectangle], container_size: int):
        self.items = items
        self.container_size = container_size

    def __repr__(self):
        return f"RectanglePacker(items={self.items}, container_size={self.container_size}"

    def add_to_solution(self, solution: RecPac_Solution, item: Rectangle):
        """Attempts to place a rectangle into an existing box. If no space is found, a new box is created."""
        if solution is None:
            return None

        for box in solution.boxes:
            x, y, rotated = self.find_valid_assignment(box, item)
            if x is not None and y is not None:
                item.x, item.y = x, y
                if rotated:
                    item.width, item.height = item.height, item.width  # Apply rotation
                box.add_rectangle(item)
                return solution  # Successfully placed, return solution

        # If no box can fit the rectangle, create a new one
        new_box = Box(self.container_size)
        item.x, item.y = 0, 0
        new_box.add_rectangle(item)
        solution.add_box(new_box)

        return solution

    def find_valid_assignment(self, container: Container, item: Item):
        """Wrapper function that prepares data and calls the Numba-optimized function"""

        # Convert Box data to NumPy arrays for Numba
        items_x = np.array([r.x for r in container.items], dtype=np.int32)
        items_y = np.array([r.y for r in container.items], dtype=np.int32)
        items_width = np.array([r.width for r in container.items], dtype=np.int32)
        items_height = np.array([r.height for r in container.items], dtype=np.int32)

        # Try normal orientation
        x, y = find_valid_assignment_numba(self.container_size, items_x, items_y, items_width, items_height, item.width, item.height)
        if x != -1:
            return x, y, False  # No rotation needed

        # Try rotated orientation
        if item.width != item.height:  # Only rotate if dimensions are different
            x, y = find_valid_assignment_numba(self.container_size, items_x, items_y, items_width, items_height, item.height, item.width)
            if x != -1:
                return x, y, True  # Rotation needed

        return None, None, False  # No valid position found
    
    def generate_initial_solution(self, rectangles, box_length):
        bad_solution = RecPac_Solution()

        for rect in rectangles:
            new_box = Box(box_length)

            if random.random() < 0.5:
                rect.width, rect.height = rect.height, rect.width

            rect.x = random.randint(0, box_length - rect.width)
            rect.y = random.randint(0, box_length - rect.height)

            new_box.add_rectangle(rect)
            bad_solution.add_box(new_box)
        return bad_solution
