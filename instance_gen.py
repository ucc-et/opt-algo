import random
from vo import Rectangle

def generateInstances(amount, upperBoundA, lowerBoundA, upperBoundB, lowerBoundB):
    """
        Generate Rectangles within the given bounds
        BoundA is for Height;
        BoundB is for Width;
    """
    generatedInstances = []

    for _ in range(amount):
        height = random.uniform(lowerBoundA, upperBoundA)
        width = random.uniform(lowerBoundB, upperBoundB)
        generatedInstances.append(Rectangle(width, height))
        
    return generatedInstances