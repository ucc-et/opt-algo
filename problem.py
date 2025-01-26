from abc import ABC, abstractmethod

class OptimizationProblem(ABC):

    @abstractmethod
    def start_solution(self):
        pass

    @abstractmethod
    def evaluate_solution(self, solution):
        pass

    @abstractmethod
    def generate_neighbors(self, solution):
        pass

    @abstractmethod
    def is_better(self, solution1, solution2):
        pass
    
    @abstractmethod
    def get_instances(self):
        pass
    
    @abstractmethod
    def place_instance(self, boxes, rectangle):
        pass

class RectanglePacker(OptimizationProblem):
    
    def __init__(self, rectangles, box_length, neighborhood_strategy):
        self.rectangles = rectangles
        self.box_length = box_length
        self.neighborhood_strategy = neighborhood_strategy
    
    """
        rectangle: (x, y, width, height)
        boxes: [box, box, box, ...]
        box: [rectangle, rectangle, ...]
    """
    
    def get_instances(self):
        return self.rectangles
    
    def place_instance(self, boxes, rectangle):
        # place the rectangle in one of the boxes. If it does not fit, it will add a new box, and initialize the rectangle at 0, 0
        rectangle_list_item = [rectangle[0], rectangle[1], rectangle[2], rectangle[3]]
        
        if boxes == None:
            pass
        
        for box in boxes:
            x, y = self.fit_rectangle_inside_box(box, rectangle_list_item)
            if x is not None and y is not None:
                rectangle_list_item[0] = x
                rectangle_list_item[1] = y
                box.append(rectangle_list_item)
                return

        # If no box can fit the rectangle, create a new box
        new_box = []
        rectangle_list_item[0] = 0
        rectangle_list_item[1] = 0
        new_box.append(rectangle_list_item)
        boxes.append(new_box)
        return boxes
    
    def fit_rectangle_inside_box(self, box, rectangle):
        # check if rectangle fits into the box provided. 
        # if it does, it returns the x, y coordinates that it can be placed into the box. 
        # if it doesn't it returns None, None
        
        box_length = self.box_length
        
        for y in range(box_length - rectangle[3] + 1):  # Iterate within box height
            for x in range(box_length - rectangle[2] + 1):  # Iterate within box width
                fits = True
                for rect in box:
                    # Check for overlap with any existing rectangles
                    if (
                        x < rect[0] + rect[2] and x + rectangle[2] > rect[0] and
                        y < rect[1] + rect[3] and y + rectangle[3] > rect[1]
                    ):
                        fits = False
                        break

                if fits:
                    return x, y  # Return the valid position

        return None, None

    def start_solution(self):
        return [[rect] for rect in self.rectangles]
    
    def evaluate_solution(self, solution):
        return len(solution)
    
    def generate_neighbors(self, solution):
        return self.neighborhood_strategy.generate_neighbors(solution, self)

    def is_better(self, solution1, solution2):
        return self.evaluate_solution(solution1) <= self.evaluate_solution(solution2)