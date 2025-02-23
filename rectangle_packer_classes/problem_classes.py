from typing import List
from base_classes.types import Item, Solution, Container, OptimizationProblem
import numpy as np

from rectangle_packer_classes.utils import compute_overlap_numba, find_valid_assignment_numba

class Rectangle(Item):
    """
    Represents a rectangle with position (x, y) and dimensions (width, height)
    """
    def __init__(self, x: int, y: int, width: int, height: int, color: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def __repr__(self):
        return f"Rectangle(x={self.x}, y={self.y}, width={self.width}, height={self.height}, color={self.color})"


class Box(Container):
    """
    Container class for storing rectangles and calculating covered area.
    """
    def __init__(self, box_length: int):
        self.box_length = box_length
        self.items: Rectangle = []

    def __repr__(self):
        return f"Box(box_length={self.box_length}, rectangles={self.items})"

    def add_item(self, item: Rectangle):
        """Add a item to the box.

        Args:
            item (Rectangle): rectangle item, that will be added
        """
        self.items.append(item)

    def remove_item(self, item: Rectangle):
        """Remove item from the box

        Args:
            item (Rectangle): the rectangle item, which will be removed from the box
        """
        self.items.remove(item)


class RecPac_Solution(Solution):
    """
    Clss that represents a solution of the rectangle packing problem.
    """
    def __init__(self):
        self.boxes: List[Box] = []

    def add_box(self, box: Box):
        """
        Adds a box to the solution.
        """
        self.boxes.append(box)

    def check_if_box_empty(self, box: Box):
        """
        Checks if the box has any rectangles inside of it. If not, it will be removed from the solution

        Args:
            box (Box): the box which is checked
        """
        if len(box.items) == 0:
            self.boxes.remove(box)

    def evaluate_solution(self, w1=1.0, w2=0.5, w3=0.2, w4=100):
        """Evaluates the solution based on number of boxes, space utilization, unused space and overlapping items.

        Args:
            w1 (float, optional): weight for number of boxes. Defaults to 1.0.
            w2 (float, optional): weight for utilization. Defaults to 0.5.
            w3 (float, optional): weight for unused space. Defaults to 0.2.
            w4 (int, optional): weight for total_overlap_area. Defaults to 100.

        Returns:
            float: evaluation score of the solution. The lower the number the better the solution is
        """
        num_boxes = len(self.boxes)

        total_area_used, total_box_area, total_overlap_area = 0, 0, 0

        for box in self.boxes:
            box_area = box.box_length**2
            total_box_area += box_area

            used_area = sum(rect.width * rect.height for rect in box.items)
            total_area_used += used_area

            # calculate overlap area between rectangles in the same box
            for i in range(len(box.items)):
                for j in range(i+1, len(box.items)):
                    overlap_area = self.compute_overlap(box.items[i], box.items[j])
                    total_overlap_area += overlap_area

        utilization = total_area_used / total_box_area
        unused_space = total_box_area - total_area_used

        return (w1 * num_boxes) + (w2 * (1 - utilization)) + (w3 * unused_space) + (w4 * total_overlap_area)

    def compute_overlap(self, rect1, rect2):
        """Calls a numba method, that will compute the overlap between two rectangles.

        Args:
            rect1, rect2 (Rectangle): Rectangles to check for overlaps

        Returns:
            int: overlapping area
        """
        return compute_overlap_numba(rect1.x, rect1.y, rect1.width, rect1.height,
                                 rect2.x, rect2.y, rect2.width, rect2.height)
    
    def are_solutions_equal(self, compare_solution):
        """
        Compares two solutions to check if they are the same.
        
        Args:
            solution1 (Solution): First solution to compare.
            solution2 (Solution): Second solution to compare.
        
        Returns:
            bool: True if both solutions are the same, False otherwise.
        """
        # Compare number of boxes
        if len(self.boxes) != len(compare_solution.boxes):
            return False
        
        # Compare each box
        for box1, box2 in zip(self.boxes, compare_solution.boxes):
            # Compare number of rectangles in each box
            if len(box1.items) != len(box2.items):
                return False
            
            # Sort rectangles by position and dimensions for order-independent comparison
            sorted_rects1 = sorted(box1.items, key=lambda r: (r.x, r.y, r.width, r.height))
            sorted_rects2 = sorted(box2.items, key=lambda r: (r.x, r.y, r.width, r.height))
            
            # Compare each rectangle
            for rect1, rect2 in zip(sorted_rects1, sorted_rects2):
                if (rect1.x != rect2.x or 
                    rect1.y != rect2.y or 
                    rect1.width != rect2.width or 
                    rect1.height != rect2.height):
                    return False
        return True

    def __repr__(self):
        return f"RecPac_Solution(boxes={self.boxes})"

class RectanglePacker(OptimizationProblem):
    """
    Optimization problem class for rectangle packing problem

    Attributes:
        items (List[Rectangle]): list of rectangles that will be packed
        container_size (int): size of the box container
    """

    def __init__(self, items: List[Rectangle], container_size: int):
        self.items = items
        self.container_size = container_size

    def __repr__(self):
        return f"RectanglePacker(items={self.items}, container_size={self.container_size}"

    def add_to_solution(self, solution: RecPac_Solution, item: Rectangle):
        """
        Attempts to place a rectangle into an existing box.
        If no space is found, a new box is created.

        Args:
            solution (RecPac_Solution): solution that the item will be added to 
            item (Rectangle): item that will be packed

        Returns:
            solution (RecPac_Solution): solution, that will either have the item packed in one of the exisitng boxes, or will have a new box added to it.
        """
        if solution is None:
            return None

        # iterate through boxes to find a assignment for the item
        for box in solution.boxes:
            x, y, rotated = self.find_valid_assignment(box, item)
            
            if x is not None and y is not None:
                item.x, item.y = x, y
                if rotated:
                    item.width, item.height = item.height, item.width  # Apply rotation, if it was rotated to place
                box.add_item(item)
                return solution

        # No existing box was able to fit the rectangle, so a new one will be added
        new_box = Box(self.container_size)
        item.x, item.y = 0, 0
        new_box.add_item(item)
        solution.add_box(new_box)

        return solution

    def find_valid_assignment(self, container: Container, item: Item, overlap_percentage: float = 0.0):
        """
        Prepare data to pass it to numba method and find positions (with rotations if needed)

        Args:
            container (Container): Box to place the item in
            item (Item): rectangle to be placed
            overlap_percentage (float, optional): allowed percentage of overlaps between rectangles. Defaults to 0.0.

        Returns:
            tuple: (x, y, rotated) where x, y are the coordinates and rotated is a boolean, indicating rotation.
        """

        # Convert Box data to NumPy arrays for Numba processing
        items_x = np.array([r.x for r in container.items], dtype=np.int32)
        items_y = np.array([r.y for r in container.items], dtype=np.int32)
        items_width = np.array([r.width for r in container.items], dtype=np.int32)
        items_height = np.array([r.height for r in container.items], dtype=np.int32)

        # try placing the item without rotation
        x, y = find_valid_assignment_numba(self.container_size, items_x, items_y, items_width, items_height, item.width, item.height, overlap_percentage)
        if x != -1:
            return x, y, False # no rotation needed

        # try placing the item with a rotation, but only if the dimensions are different
        if item.width != item.height:
            x, y = find_valid_assignment_numba(self.container_size, items_x, items_y, items_width, items_height, item.height, item.width, overlap_percentage)
            if x != -1:
                return x, y, True # rotation needed

        return None, None, False # no valid position found
    
    def generate_item_samples(self, rectangles, n=4):
        """
        splits the list of rectangles into n approximately equal sublists.

        Args:
            rectangles (list[Rectangle]): list of rectangles that will be split
            n (int, optional): number of sublists to generate. Defaults to 4.

        Returns:
            list[list[Rectangle]]: List of n sublists of rectangles
        """
        
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
        """
        Generates an initial (suboptimal) solution by placing all items in a single box

        Args:
            items (list[ectangles]): rectangles that will be placed into the suboptimal solution
            box_length (int): size of the box container

        Returns:
            RecPac_Solution: solution with all items in their own box
        """
        bad_solution = RecPac_Solution()
        
        for item in items:
            new_box = Box(box_length)
            item.x = 0
            item.y = 0
            new_box.add_item(item)
            bad_solution.add_box(new_box)
        return bad_solution