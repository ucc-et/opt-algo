from helpers import calculate_objective, generate_neighbors, rectangle_fits_in_box

"""
TODO: Instead of having two methods, try to have a Generic Class like in the old approach
"""

def local_search(initial_solution, L, max_iterations=100):
    """
    Perform local search to minimize the number of boxes.
    initial_solution: Starting solution (e.g., from Greedy algorithm).
    L: Box length.
    max_iterations: Maximum number of iterations to avoid infinite loops.
    """
    current_solution = initial_solution
    current_objective = calculate_objective(current_solution)

    for iteration in range(max_iterations):
        neighbors = generate_neighbors(current_solution, L)
        best_neighbor = None
        best_objective = current_objective

        for neighbor in neighbors:
            neighbor_objective = calculate_objective(neighbor)
            if neighbor_objective < best_objective:
                best_neighbor = neighbor
                best_objective = neighbor_objective

        if best_neighbor is None:  # No improvement found
            break

        current_solution = best_neighbor
        current_objective = best_objective
        print(f"Iteration {iteration + 1}: Objective = {current_objective}")

    return current_solution

def greedy_algorithm(rectangles, L, strategy):
    # TODO: check if these 'strategy types' are sufficient for the task description
    if strategy == "area":
        rectangles.sort(key=lambda x: x[0] * x[1], reverse=True)  # Sortiere Rechtecke nach Fläche
    elif strategy == "aspect_ratio":
        rectangles.sort(key=lambda x: x[0] / x[1], reverse=True)  # Sortiere nach Aspect Ratio
        
    boxes = []
    
    # Rechtecke platzieren
    for rect in rectangles:
        placed = False
        for box in boxes:
            # Try to place in this box by finding an empty spot
            for x in range(L):
                for y in range(L):
                    if rectangle_fits_in_box(box, (x, y, rect[0], rect[1]), L):
                        box.append((x, y, rect[0], rect[1]))  # Place rectangle
                        placed = True
                        break
                if placed:
                    break
        if not placed:
            # Create a new box and place the rectangle at (0, 0)
            boxes.append([(0, 0, rect[0], rect[1])])
    
    return boxes