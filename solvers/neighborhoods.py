import random
import copy
import numpy as np

from classes.base_classes import  OptimizationProblem, Solution, Neighborhood
from classes.rectangle_packer_types import RecPac_Solution, Rectangle, Box
import classes.helpers

from .enums import Rules

class GeometryBasedStrategy(Neighborhood):
    def __init__(self, problem: OptimizationProblem, solution_type: type):
        self.problem = problem
        self.solution_type = solution_type

    def generate_neighbor(self, solution: Solution):
        if not solution.boxes:
            return solution

        new_solution = copy.deepcopy(solution)

        box_from = new_solution.boxes[-1]
        if not box_from.items:
            return new_solution

        for _ in range(len(box_from.items)):
            rect_to_move = random.choice(box_from.items)
            box_from.remove_rectangle(rect_to_move)

            index = 0

            while True:
                box_to = new_solution.boxes[index]

                x, y, rotated = self.problem.find_valid_assignment(box_to, rect_to_move)

                if x is not None and y is not None:
                    rect_to_move.x = x
                    rect_to_move.y = y
                    if rotated:
                        rect_to_move.width, rect_to_move.height = rect_to_move.height, rect_to_move.width
                    box_to.add_rectangle(rect_to_move)
                    new_solution.check_if_box_empty(box_from)
                    break

                else:
                    index += 1

        return new_solution


class RuleBasedStrategy(Neighborhood):
    def __init__(self, problem: OptimizationProblem, rule: str = Rules.HEIGHT_FIRST):
        self.problem = problem
        self.rule = rule

    def generate_neighbor(self, solution: Solution):
        if not solution.boxes:
            return solution

        current_solution = RecPac_Solution()
        items = [item for box in solution.boxes for item in box.items]

        if len(items) > 1:
            items = classes.helpers.apply_rule(items, self.rule)

            small_rectangles = items[:len(items) // 2]
            selected = random.choice(small_rectangles)

            i = items.index(selected)
            j = i + 1 if i < len(items) - 1 else i - 1
            items[i], items[j] = items[j], items[i]

        for item in items:
            item.x, item.y = None, None

            new_solution = self.problem.add_to_solution(current_solution, item)

            if new_solution is not None:
                current_solution = new_solution

        return current_solution

class OverlapStrategy(Neighborhood):
    def __init__(self, problem: OptimizationProblem, initial_overlap: float = 1.0, decay_rate: float = 0.05):
        self.overlap_percentage = initial_overlap
        self.decay_rate = decay_rate
        self.problem = problem

    def generate_neighbor(self, solution: Solution):
        new_solution = solution # deep copy slow apparently

        for box in new_solution.boxes:
            spatial_data = self.build_spatial_array(box)

            items_to_relocate = self.find_violating_rectangles(box, spatial_data)

            for item in items_to_relocate:
                box.remove_rectangle(item)

            self.reassign_rectangles(new_solution, items_to_relocate)

        self.overlap_percentage = max(0.0, round(self.overlap_percentage - self.decay_rate, 6))
        return new_solution

    def build_spatial_array(self, box: Box):
        if not box.items:
            return np.empty((0, 5), dtype=np.float32)

        return np.array([[rect.x, rect.y, rect.x + rect.width, rect.y + rect.height, rect.width * rect.height] for rect in box.items], dtype=np.float32)

    def find_violating_rectangles(self, box, spatial_data):
        violating_items = []

        for rect in box.items:
            rect_arr = np.array([rect.x, rect.y, rect.x + rect.width, rect.y + rect.height, rect.width * rect.height], dtype=np.float32)
            if not self.check_overlap_vectorized(spatial_data, rect_arr, self.overlap_percentage):
                violating_items.append(rect)

        return violating_items

    def reassign_rectangles(self, new_solution, items_to_relocate):
        for item in items_to_relocate:
            placed = False
            for box in new_solution.boxes:
                x, y, rotated = self.problem.find_valid_assignment(box, item, self.overlap_percentage * 0.3)
                if x is not None:
                    item.x, item.y = x, y
                    if rotated:
                        item.width, item.height = item.height, item.width
                    box.add_rectangle(item)
                    placed = True
                    break

            if not placed:
                new_box = Box(new_solution.boxes[0].box_length)
                item.x, item.y = 0, 0
                new_box.add_rectangle(item)
                new_solution.add_box(new_box)

    def check_overlap_vectorized(self, spatial_data, rect_arr, overlap_percentage):
        if spatial_data.shape[0] == 0:
            return True

        rect_x1, rect_y1, rect_x2, rect_y2, rect_area = rect_arr

        x_overlap = np.maximum(0, np.minimum(spatial_data[:, 2], rect_x2) - np.maximum(spatial_data[:, 0], rect_x1))
        y_overlap = np.maximum(0, np.minimum(spatial_data[:, 3], rect_y2) - np.maximum(spatial_data[:, 1], rect_y1))

        overlap_areas = x_overlap * y_overlap
        max_areas = np.maximum(rect_area, spatial_data[:, 4])

        overlap_ratios = overlap_areas / max_areas
        if np.any(overlap_ratios > overlap_percentage):
            return False

        return True

