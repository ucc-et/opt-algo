from typing import List
from abc import ABC

class Item(ABC):
    pass

class Container(ABC):
    pass

class Solution(ABC):
    pass
    

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
        x_overlap = max(0, min(rect1.x + rect1.width, rect2.x + rect2.width) - max(rect1.x, rect2.x))
        y_overlap = max(0, min(rect1.y + rect1.height, rect2.y + rect2.height) - max(rect1.y, rect2.y))
        return x_overlap * y_overlap

    def __repr__(self):
        return f"RecPac_Solution(boxes={self.boxes})"
