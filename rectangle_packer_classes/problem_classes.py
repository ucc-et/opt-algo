
from typing import List
from base_classes.types import Item, Solution, Container, OptimizationProblem
from numba import njit
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

    def evaluate_solution(self, w1=1.0, w2=0.5, w3=0.2, w4=100):
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
        return compute_overlap_numba(rect1.x, rect1.y, rect1.width, rect1.height,
                                 rect2.x, rect2.y, rect2.width, rect2.height)

    def __repr__(self):
        return f"RecPac_Solution(boxes={self.boxes})"

@njit 
def compute_overlap_numba(x1, y1, w1, h1, x2, y2, w2, h2):
    """Fast overlap computation using Numba JIT compilation"""
    x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    return x_overlap * y_overlap

@njit
def find_valid_assignment_numba(container_size, items_x, items_y, items_width, items_height, item_width, item_height, overlap_percentage):

    occupancy_grid = np.zeros((container_size, container_size), dtype=np.uint8)

    for i in range(len(items_x)):
        x1, y1 = items_x[i], items_y[i]
        x2, y2 = x1 + items_width[i], y1 + items_height[i]
        occupancy_grid[x1:x2, y1:y2] = 1

    integral_image = np.zeros_like(occupancy_grid, dtype=np.int32)

    for x in range(container_size):
        for y in range(container_size):
            integral_image[x, y] = occupancy_grid[x, y]
            if x > 0:
                integral_image[x, y] += integral_image[x-1, y]
            if y > 0:
                integral_image[x, y] += integral_image[x, y-1]
            if x > 0 and y > 0:
                integral_image[x, y] -= integral_image[x-1, y-1]

    for y in range(container_size - item_height + 1):
        for x in range(container_size - item_width + 1):
            x2, y2 = x + item_width - 1, y + item_height - 1
            total_area = item_width * item_height

            overlap_area = integral_image[x2, y2]
            if x > 0:
                overlap_area -= integral_image[x-1, y2]
            if y > 0:
                overlap_area -= integral_image[x2, y-1]
            if x > 0 and y > 0:
                overlap_area += integral_image[x-1, y-1]

            overlap_ratio = overlap_area / total_area

            if overlap_ratio <= overlap_percentage:
                return x, y

    return -1, -1



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
    
    def generate_item_samples(self, rectangles, n=4):
        
        avg_size = len(rectangles) // n
        remainder = len(rectangles) % n
        sub_lists = []
        start = 0
        for i in range(n):
            extra = 1 if i < remainder else 0
            end = start + avg_size + extra
            sub_lists.append(rectangles[start:end])
            start = end
        
        return sub_lists
    
    def generate_initial_solution(self, items, box_length):
        bad_solution = RecPac_Solution()
        new_box = Box(box_length)
        for item in items:
            item.x = 0
            item.y = 0
            new_box.add_rectangle(item)

        bad_solution.add_box(new_box)
        return bad_solution