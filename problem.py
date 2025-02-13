from abc import ABC, abstractmethod
from typing import List

import numpy as np
from numba import njit

from objects import Box, RecPac_Solution, Rectangle


class OptimizationProblem(ABC):

    @abstractmethod
    def basic_solution(self):
        pass

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

    def __init__(self, rectangles: List[Rectangle], box_length: int):
        self.rectangles = rectangles
        self.box_length = box_length

    def __repr__(self):
        return f"RectanglePacker(rectangles={self.rectangles}, box_length={self.box_length}"

    def add_to_solution(self, solution: RecPac_Solution, instance: Rectangle):
        """Attempts to place a rectangle into an existing box. If no space is found, a new box is created."""
        if solution is None:
            return None

        for box in solution.boxes:
            x, y, rotated = self.fit_rectangle_inside_box(box, instance)
            if x is not None and y is not None:
                instance.x, instance.y = x, y
                if rotated:
                    instance.width, instance.height = instance.height, instance.width  # Apply rotation
                box.add_rectangle(instance)
                return solution  # Successfully placed, return solution

        # If no box can fit the rectangle, create a new one
        new_box = Box(self.box_length)
        instance.x, instance.y = 0, 0
        new_box.add_rectangle(instance)
        solution.add_box(new_box)

        return solution

    def fit_rectangle_inside_box(self, box: Box, rectangle: Rectangle):
        """Wrapper function that prepares data and calls the Numba-optimized function"""
        box_length = self.box_length

        # Convert Box data to NumPy arrays for Numba
        rectangles_x = np.array([r.x for r in box.rectangles], dtype=np.int32)
        rectangles_y = np.array([r.y for r in box.rectangles], dtype=np.int32)
        rectangles_width = np.array([r.width for r in box.rectangles], dtype=np.int32)
        rectangles_height = np.array([r.height for r in box.rectangles], dtype=np.int32)

        # Try normal orientation
        x, y = fit_rectangle_inside_box_numba(box_length, rectangles_x, rectangles_y, rectangles_width,
                                              rectangles_height,
                                              rectangle.width, rectangle.height)
        if x != -1:
            return x, y, False  # No rotation needed

        # Try rotated orientation
        if rectangle.width != rectangle.height:  # Only rotate if dimensions are different
            x, y = fit_rectangle_inside_box_numba(box_length, rectangles_x, rectangles_y, rectangles_width,
                                                  rectangles_height,
                                                  rectangle.height, rectangle.width)
            if x != -1:
                return x, y, True  # Rotation needed

        return None, None, False  # No valid position found

    def basic_solution(self):
        """Creates a solution, in which each rectangle has its own box

        Returns:
            RecPac_Solution: solution with one box per rectangle
        """
        solution = RecPac_Solution()
        for rectangle in self.rectangles:
            box = Box(self.box_length)
            rectangle.x, rectangle.y = 0, 0
            box.add_rectangle(rectangle)
            solution.add_box(box)
        return solution
