import tkinter as tk
from tkinter import ttk
import random

from helpers import generate_instances
from searches import greedy_algorithm, local_search


def generate_rectangles():
    """
    Get data from input fields in the UI and utilize the values in there to generate_instances
    """
    global rectangles, L
    n = int(entry_num_rectangles.get())
    min_w = int(entry_min_width.get())
    max_w = int(entry_max_width.get())
    min_h = int(entry_min_height.get())
    max_h = int(entry_max_height.get())
    L = int(entry_box_length.get())
    
    rectangles = generate_instances(n, min_w, max_w, min_h, max_h)
    label_status.config(text=f"{n} Rechtecke generiert!")

def run_algorithm():
    """
    Choose which algorithm to run, depending if Greedy is selected in the dropdown or local search
    """
    algorithm = algo_selector.get()
    if algorithm == "Greedy":
        solution = greedy_algorithm(rectangles, L, greedy_strat.get())
    elif algorithm == "Lokale Suche":
        initial_solution = greedy_algorithm(rectangles, L, greedy_strat.get())
        solution = local_search(initial_solution, L)
    visualize_solution(solution)

def visualize_solution(solution):
    """
    Generate box instances in the UI with the rectangles filled in them
    """

    canvas.delete("all")
    
    box_padding = 10
    x_offset = 0
    y_offset = 0
    row_height = 0
    canvas_width = canvas.winfo_width()

    for box_id, box in enumerate(solution):
        # If box too big for current line, go to next
        if x_offset + L + box_padding > canvas_width:
            x_offset = 0
            y_offset += row_height + box_padding
            row_height = 0

        row_height = max(row_height, L)

        canvas.create_rectangle(
            x_offset, y_offset,
            x_offset + L, y_offset + L,
            outline="black"
        )

        # Rectangle drawer
        for rect in box:
            x, y, w, h = rect
            canvas.create_rectangle(
                x_offset + x, y_offset + y,
                x_offset + x + w, y_offset + y + h,
                fill=random.choice(["red", "green", "blue", "yellow"]),
                outline="black"
            )

        x_offset += L + box_padding

    update_scrollregion()

def update_scrollregion():
    """
    Update canvas to make Scrollbar work properly
    """
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


"""
=========
== GUI ==
=========
"""
# Initialize GUI
root = tk.Tk()
root.title("Optimierungsalgorithmen GUI")

# Create input fields and place them in UI
frame_inputs = tk.Frame(root)
frame_inputs.pack(pady=10)

tk.Label(frame_inputs, text="Anzahl Rechtecke:").grid(row=0, column=0)
entry_num_rectangles = tk.Entry(frame_inputs)
entry_num_rectangles.grid(row=0, column=1)

tk.Label(frame_inputs, text="Min Breite:").grid(row=1, column=0)
entry_min_width = tk.Entry(frame_inputs)
entry_min_width.grid(row=1, column=1)

tk.Label(frame_inputs, text="Max Breite:").grid(row=2, column=0)
entry_max_width = tk.Entry(frame_inputs)
entry_max_width.grid(row=2, column=1)

tk.Label(frame_inputs, text="Min Höhe:").grid(row=3, column=0)
entry_min_height = tk.Entry(frame_inputs)
entry_min_height.grid(row=3, column=1)

tk.Label(frame_inputs, text="Max Höhe:").grid(row=4, column=0)
entry_max_height = tk.Entry(frame_inputs)
entry_max_height.grid(row=4, column=1)

tk.Label(frame_inputs, text="Boxlänge L:").grid(row=5, column=0)
entry_box_length = tk.Entry(frame_inputs)
entry_box_length.grid(row=5, column=1)

# Choose the selected algorithm
algo_selector = ttk.Combobox(frame_inputs, values=["Greedy", "Lokale Suche"])
algo_selector.set("Greedy")
algo_selector.grid(row=6, column=1)

# Choose Greedy strategy
greedy_strat = ttk.Combobox(frame_inputs, values= ["area", "aspect_ratio"])
greedy_strat.set("area")
greedy_strat.grid(row=7, column=1)
greedy_strat.grid_remove()

# Function to toggle visibility based on strategy
def update_visibility(*args):
    if algo_selector.get() == "Greedy":
        greedy_strat.grid()
    else:
        greedy_strat.grid_remove()

# Attach function to algorithm selection change
algo_selector.bind("<<ComboboxSelected>>", update_visibility)

# Ensure visibility is updated during initialization
update_visibility()

# Create Buttons in UI to Generate Instances and Start Packer
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

btn_generate = tk.Button(frame_buttons, text="Instanz generieren", command=generate_rectangles)
btn_generate.grid(row=0, column=0, padx=5)

btn_run = tk.Button(frame_buttons, text="Algorithmus ausführen", command=run_algorithm)
btn_run.grid(row=0, column=1, padx=5)

# Display Status of Program and the canvas with the rectangles
label_status = tk.Label(root, text="Status: Bereit")
label_status.pack()

# Create the scrollable canvas frame
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill="both", expand=True)

# Create the canvas
canvas = tk.Canvas(canvas_frame, bg="white")
canvas.pack(side="left", fill="both", expand=True)

# Add vertical scrollbar
v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
v_scrollbar.pack(side="right", fill="y")

# Configure the canvas to work with the vertical scrollbar
canvas.configure(yscrollcommand=v_scrollbar.set)



root.mainloop()
