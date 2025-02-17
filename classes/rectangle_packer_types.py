
from typing import List
from .base_classes import Item, Solution, Container, OptimizationProblem
from numba import njit
import random
import numpy as np

class Rectangle(Item):
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return f"Rectangle(x={self.x}, y={self.y}, width={self.width}, height={self.height})"


class Box(Container):
    def __init__(self, box_length: int):
        self.box_length = box_length
        self.items: Rectangle = []
        self.last_covered_area = None

    def __repr__(self):
        return f"Box(box_length={self.box_length}, rectangles={self.items}, last_covered_area={self.last_covered_area})"

    def add_rectangle(self, item: Rectangle):
        self.items.append(item)

    def remove_rectangle(self, item: Rectangle):
        self.items.remove(item)

    def calculate_covered_area(self):
        total_box_area = self.box_length ** 2
        covered_by_items = 0

        for item in self.items:
            covered_by_items += item.width * item.height

        return (covered_by_items / total_box_area) * 100


class RecPac_Solution(Solution):
    def __init__(self):
        self.boxes: List[Box] = []

    def add_box(self, box: Box):
        self.boxes.append(box)

    def set_boxes(self, boxes: List[Box]):
        self.boxes = boxes

    def check_if_box_empty(self, box: Box):
        if len(box.items) == 0:
            self.boxes.remove(box)

    def evaluate_solution(self, w1=1.0, w2=0.5, w3=0.2, w4=1000):
        num_boxes = len(self.boxes)

        total_area_used, total_box_area, total_overlap_area = 0, 0, 0

        for box in self.boxes:
            box_area = box.box_length**2
            total_box_area += box_area

            used_area = sum(rect.width * rect.height for rect in box.items)
            total_area_used += used_area

            for i in range(len(box.items)):
                for j in range(i+1, len(box.items)):
                    overlap_area = self.compute_overlap(box.items[i], box.items[j])
                    total_overlap_area += overlap_area

        utilization = total_area_used / total_box_area
        unused_space = total_box_area - total_area_used

        return (w1 * num_boxes) + (w2 * (1 - utilization)) + (w3 * unused_space) + (w4 * total_overlap_area)

    def compute_overlap(self, rect1, rect2):
        x_overlap = max(0, min(rect1.x + rect1.width, rect2.x + rect2.width) - max(rect1.x, rect2.x))
        y_overlap = max(0, min(rect1.y + rect1.height, rect2.y + rect2.height) - max(rect1.y, rect2.y))
        return x_overlap * y_overlap

    def __repr__(self):
        return f"RecPac_Solution(boxes={self.boxes})"

@njit
def detect_item_invalidity(x, y, width, height, item_x, item_y, item_width, item_height, overlap_percentage):
    
    
    if overlap_percentage == 0.0:
        return not (x >= item_x + item_width or x + width <= item_x or y >= item_y + item_height or y + height <= item_y)
    
    # Calculate Overlap
    x_overlap = max(0, min(x + width, item_x + item_width) - max(x, item_x))
    y_overlap = max(0, min(y + height, item_y + item_height) - max(y, item_y))
    overlap_area = x_overlap * y_overlap

    max_area = max(width * height, item_width * item_height)
    actual_overlap = overlap_area / max_area if max_area > 0 else 0.0

    # If overlap under overlap_percentage, overlap is allowed
    return actual_overlap >= overlap_percentage

@njit
def find_valid_assignment_numba(container_size, items_x, items_y, items_width, items_height, item_width, item_height, overlap_percentage):
    """Fast brute-force search for a valid rectangle position"""
    for y in range(container_size - item_width + 1):
        for x in range(container_size - item_height + 1):
            fits = True
            for i in range(len(items_x)):  # Check all existing rectangles
                if detect_item_invalidity(x, y, item_width, item_height, items_x[i], items_y[i], items_width[i], items_height[i], overlap_percentage):
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

    def find_valid_assignment(self, container: Container, item: Item, overlap_percentage: float = 0.0):
        """Wrapper function that prepares data and calls the Numba-optimized function"""

        # Convert Box data to NumPy arrays for Numba
        items_x = np.array([r.x for r in container.items], dtype=np.int32)
        items_y = np.array([r.y for r in container.items], dtype=np.int32)
        items_width = np.array([r.width for r in container.items], dtype=np.int32)
        items_height = np.array([r.height for r in container.items], dtype=np.int32)

        # Try normal orientation
        x, y = find_valid_assignment_numba(self.container_size, items_x, items_y, items_width, items_height, item.width, item.height, overlap_percentage)
        if x != -1:
            return x, y, False  # No rotation needed

        # Try rotated orientation
        if item.width != item.height:  # Only rotate if dimensions are different
            x, y = find_valid_assignment_numba(self.container_size, items_x, items_y, items_width, items_height, item.height, item.width, overlap_percentage)
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