from numba import njit
import numpy as np

def color_to_int(color):
    """
    Converts a color name to a unique integer.
    Ensures consistency in color preservation and allows to copy the rectangle data with numba.
    """
    color_map = {
        "red": 1,
        "green": 2,
        "blue": 3,
        "yellow": 4,
        "purple": 5,
        "orange": 6,
        "cyan": 7
    }
    return color_map.get(color, 0) 

def int_to_color(color_int):
    """
    Converts an integer back to its corresponding color name.
    """
    int_map = {
        1: "red",
        2: "green",
        3: "blue",
        4: "yellow",
        5: "purple",
        6: "orange",
        7: "cyan"
    }
    return int_map.get(color_int, "black")  # Default to black if not found


@njit
def find_valid_assignment_numba(container_size, items_x, items_y, items_width, items_height, item_width, item_height, overlap_percentage):
    """
    Finds a valid position for a new rectangle using an occupancy grid approach and utilizing njit.

    Args:
        container_size (int): size of the container
        items_x, items_y, items_width, items_height (np.array): Arrays of existing rectangle positions and sizes, where the position i, will provide all the info for rectangle i. 
        item_width, item_height (int): dimensions of the rectangle, for which the assignment is searched
        overlap_percentage (float): Allowed overlap percentage

    Returns:
        tuple: (x, y) position if valid, otherwise (-1, -1).
    """

    occupancy_grid = np.zeros((container_size, container_size), dtype=np.uint8)

    # fill occupancy grid with existing rectangles
    for i in range(len(items_x)):
        x1, y1 = items_x[i], items_y[i]
        x2, y2 = x1 + items_width[i], y1 + items_height[i]
        occupancy_grid[x1:x2, y1:y2] = 1

    # compute integral image for fast overlap calculations
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

    # check for valid positions
    for y in range(container_size - item_height + 1):
        for x in range(container_size - item_width + 1):
            x2, y2 = x + item_width - 1, y + item_height - 1
            total_area = item_width * item_height

            overlap_area = integral_image[x2, y2] # bottom right
            if x > 0:
                overlap_area -= integral_image[x-1, y2] # left of rectangle
            if y > 0:
                overlap_area -= integral_image[x2, y-1] # above rectangle
            if x > 0 and y > 0:
                overlap_area += integral_image[x-1, y-1] # top-left

            overlap_ratio = overlap_area / total_area

            if overlap_ratio <= overlap_percentage:
                return x, y

    return -1, -1

@njit 
def compute_overlap_numba(x1, y1, w1, h1, x2, y2, w2, h2):
    """
    Fast overlap computation using Numba JIT compilation
    
    Args: 
        x1, y1, w1, h1, x2, y2, w2, h2: position and dimension of rectangles, so they can be used by numba
    """
    x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    return x_overlap * y_overlap

@njit
def copy_numpy_array(array):
    """
    Quickly copies a NumPy array using numba.
    
    Args:
        array (np.ndarray): Input array to copy.
    
    Returns:
        np.ndarray: A deep copy of the input array which is generated faster than copy.deepcopy.
    """
    copy = np.empty_like(array)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            copy[i, j] = array[i, j]
    return copy
