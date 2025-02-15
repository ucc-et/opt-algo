import copy
import random
from abc import ABC, abstractmethod

from objects import Box, RecPac_Solution, Rectangle
from problem import OptimizationProblem


class NeighborhoodStrategy(ABC):
    @abstractmethod
    def generate_neighbor(self, solution):
        pass


class GeometryBasedStrategy(NeighborhoodStrategy):
    def __init__(self, problem: OptimizationProblem):
        self.problem = problem

    def generate_neighbor(self, solution: RecPac_Solution):
        if not solution.boxes:
            return solution

        new_solution = copy.deepcopy(solution)

        box_from = new_solution.boxes[-1]
        if not box_from.rectangles:
            return new_solution

        for _ in range(len(box_from.rectangles)):
            rect_to_move = random.choice(box_from.rectangles)
            box_from.remove_rectangle(rect_to_move)

            index = 0

            while True:
                box_to = new_solution.boxes[index]

                x, y, rotated = self.problem.fit_rectangle_inside_box(box_to, rect_to_move)

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


class RuleBasedStrategy(NeighborhoodStrategy):
    def __init__(self, problem: OptimizationProblem, rule: str = "Absteigend nach Höhe"):
        self.problem = problem
        self.rule = rule

    def generate_neighbor(self, solution: RecPac_Solution):
        if not solution.boxes:
            return solution

        # Create a new empty solution
        current_solution = RecPac_Solution()

        # Extract all rectangles
        rectangles = [rect for box in solution.boxes for rect in box.rectangles]

        if len(rectangles) > 1:
            if self.rule == "Absteigend nach Höhe":
                rectangles = sorted(rectangles, key=lambda rect: rect.height, reverse=True)
            elif self.rule == "Absteigend nach Breite":
                rectangles = sorted(rectangles, key=lambda rect: rect.width, reverse=True)
            elif self.rule == "Absteigend nach Fläche":
                rectangles = sorted(rectangles, key=lambda rect: rect.height*rect.width, reverse=True)

            # Pick a small rectangle from the first half
            small_rectangles = rectangles[:len(rectangles) // 2]
            selected = random.choice(small_rectangles)

            # Swap with its neighbor
            i = rectangles.index(selected)
            j = i + 1 if i < len(rectangles) - 1 else i - 1
            rectangles[i], rectangles[j] = rectangles[j], rectangles[i]

        # Place rectangles **from scratch** to prevent overlaps
        for instance in rectangles:
            instance.x, instance.y = None, None  # Reset position before placing

            new_solution = self.problem.add_to_solution(current_solution, instance)

            if new_solution is not None:
                current_solution = new_solution

        return current_solution

class OverlapStrategy(NeighborhoodStrategy):
    def __init__(self,problem: OptimizationProblem, initial_overlap: float = 1.0, decay_rate: float = 0.05):
        self.overlap_percentage = initial_overlap
        self.decay_rate = decay_rate
        self.problem = problem

    def generate_neighbor(self, solution: RecPac_Solution):
        if not solution.boxes:
            return solution

        new_solution = copy.deepcopy(solution)

        for box_from in new_solution.boxes:

            for rect_to_move in box_from.rectangles:
                box_from.remove_rectangle(rect_to_move)

                position_found = False

                # check all boxes in this solution
                for box_to in new_solution.boxes:
                    x, y, rotated = self.problem.fit_rectangle_inside_box_with_overlap(box_to, rect_to_move,
                                                                                       self.overlap_percentage)

                    if x is not None and y is not None:
                        rect_to_move.x = x
                        rect_to_move.y = y
                        if rotated:
                            rect_to_move.width, rect_to_move.height = rect_to_move.height, rect_to_move.width
                        box_to.add_rectangle(rect_to_move)
                        position_found = True
                        break

                # if there is no valid position create new box
                if not position_found:
                    new_box = Box(new_solution.boxes[0].box_length)
                    rect_to_move.x, rect_to_move.y = 0, 0
                    new_box.add_rectangle(rect_to_move)
                    new_solution.add_box(new_box)
                    break

            new_solution.check_if_box_empty(box_from)

        # decrease overlap_percentage
        self.overlap_percentage = max(0, self.overlap_percentage - self.decay_rate)

        return new_solution

    def check_overlap(self, box: Box, rect: Rectangle):
        overlapping_area = 0
        max_rect_area = max(rect.width * rect.height, 1)
        max_existing_area = 1

        for existing_rect in box.rectangles:
            x_overlap = max(0, min(existing_rect.x + existing_rect.width, rect.x + rect.width) - max(existing_rect.x, rect.x))
            y_overlap = max(0, min(existing_rect.y + existing_rect.height, rect.y + rect.height) - max(existing_rect.y, rect.y))

            overlap_area = x_overlap * y_overlap
            overlapping_area += overlap_area

            max_existing_area = max(max_existing_area, existing_rect.width * existing_rect.height)

        denominator = max(max_rect_area, max_existing_area)
        if overlapping_area / denominator <= self.overlap_percentage:
            return True

        return False