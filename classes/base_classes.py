from abc import ABC, abstractmethod

# =================================================
#               OptimizationProblem
# =================================================

class OptimizationProblem(ABC):
    @abstractmethod
    def add_to_solution(self, *args):
        pass

    @abstractmethod
    def find_valid_assignment(self, *args):
        pass
    
    @abstractmethod
    def generate_initial_solution(self, *args):
        pass
    
# =================================================
#                 Neighborhood
# =================================================
    
class Neighborhood(ABC):
    @abstractmethod
    def generate_neighbor(self, *args):
        pass
    
# =================================================
#             Item, Container, Solution
# =================================================

class Item(ABC):
    pass

class Container(ABC):
    pass

class Solution(ABC):
    pass