from abc import ABC, abstractmethod
from typing import List

import numpy as np
from numba import njit

from objects import Box, RecPac_Solution, Rectangle


class OptimizationProblem(ABC):
    @abstractmethod
    def add_to_solution(self, solution, instance) -> object:
        pass

    @abstractmethod
    def fit_rectangle_inside_box(self, box: Box, rectangle: Rectangle):
        pass


@njit
def check_collision(x, y, width, height, rect_x, rect_y, rect_width, rect_height):
    """Fast overlap check using Numba"""
    return not (x >= rect_x + rect_width or x + width <= rect_x or
                y >= rect_y + rect_height or y + height <= rect_y)


@njit
def fit_rectangle_inside_box_numba(box_length, rectangles_x, rectangles_y, rectangles_width, rectangles_height,
                                   rect_width, rect_height):
    """Fast brute-force search for a valid rectangle position"""
    for y in range(box_length - rect_height + 1):
        for x in range(box_length - rect_width + 1):
            fits = True
            for i in range(len(rectangles_x)):  # Check all existing rectangles
                if check_collision(x, y, rect_width, rect_height,
                                   rectangles_x[i], rectangles_y[i],
                                   rectangles_width[i], rectangles_height[i]):
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
        return f"RectanglePacker(items={self.items}, box_length={self.container_size}"

    def add_to_solution(self, solution: RecPac_Solution, item: Rectangle):
        """Attempts to place a rectangle into an existing box. If no space is found, a new box is created."""
        if solution is None:
            return None

        for box in solution.boxes:
            x, y, rotated = self.fit_rectangle_inside_box(box, item)
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

    def fit_rectangle_inside_box(self, box: Box, item: Rectangle):
        """Wrapper function that prepares data and calls the Numba-optimized function"""

        # Convert Box data to NumPy arrays for Numba
        items_x = np.array([r.x for r in box.rectangles], dtype=np.int32)
        items_y = np.array([r.y for r in box.rectangles], dtype=np.int32)
        items_width = np.array([r.width for r in box.rectangles], dtype=np.int32)
        items_height = np.array([r.height for r in box.rectangles], dtype=np.int32)

        # Try normal orientation
        x, y = fit_rectangle_inside_box_numba(self.container_size, items_x, items_y, items_width, items_height, item.width, item.height)
        if x != -1:
            return x, y, False  # No rotation needed

        # Try rotated orientation
        if item.width != item.height:  # Only rotate if dimensions are different
            x, y = fit_rectangle_inside_box_numba(self.container_size, items_x, items_y, items_width, items_height, item.height, item.width)
            if x != -1:
                return x, y, True  # Rotation needed

        return None, None, False  # No valid position found
