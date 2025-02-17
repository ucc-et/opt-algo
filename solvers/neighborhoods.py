import copy
import random

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
    def __init__(self,problem: OptimizationProblem, initial_overlap: float = 1.0, decay_rate: float = 0.05):
        self.overlap_percentage = initial_overlap
        self.decay_rate = decay_rate
        self.problem = problem

    def generate_neighbor(self, solution: Solution):
        new_solution = copy.deepcopy(solution)

        for box in new_solution.boxes:
            for item in box.items:
                if not self.check_overlap(box, item):
                    box.remove_rectangle(item)
                    x, y, rotated = self.problem.find_valid_assignment(box, item, self.overlap_percentage)

                    if x is not None and y is not None:
                        item.x, item.y = x, y
                        if rotated:
                            item.width, item.height = item.height, item.width
                        box.add_rectangle(item)
                    else:
                        placed = False
                        for other_box in new_solution.boxes:
                            if other_box is not box:
                                x, y, rotated = self.problem.find_valid_assignment(other_box, item, self.overlap_percentage)
                                if x is not None and y is not None:
                                    item.x, item.y = x, y
                                    if rotated:
                                        item.width, item.height = item.height, item.width
                                    other_box.add_rectangle(item)
                                    placed = True
                                    break

                        if not placed:
                            new_box = Box(new_solution.boxes[0].box_length)
                            item.x, item.y = 0, 0
                            new_box.add_rectangle(item)
                            new_solution.add_box(new_box)
                            
        self.overlap_percentage = max(0, round(self.overlap_percentage - self.decay_rate, 6))

        return new_solution

    def check_overlap(self, box: Box, rect: Rectangle):
        max_rect_area = rect.width * rect.height

        for existing_rect in box.items:
            if existing_rect == rect:
                continue

            x_overlap = max(0, min(existing_rect.x + existing_rect.width, rect.x + rect.width) - max(existing_rect.x, rect.x))
            y_overlap = max(0, min(existing_rect.y + existing_rect.height, rect.y + rect.height) - max(existing_rect.y, rect.y))

            overlap_area = x_overlap * y_overlap
            max_existing_area = existing_rect.width * existing_rect.height

            denominator = min(max_rect_area, max_existing_area)
            if overlap_area / denominator > self.overlap_percentage:
                return False

        return True