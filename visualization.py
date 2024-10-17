import tkinter as tk
from tkinter import ttk

def open_screen_window(box_size):
    # This function opens the second window when "Start" is clicked
    screen_window = tk.Toplevel(root)  # Create a new top-level window
    screen_window.title("Screen Window")
    screen_window.geometry(f"{box_size}x{box_size}")  # Set the size of the window

    # Large screen area (75% of the window)
    screen_frame = tk.Frame(screen_window, bg='lightgray', bd=2, relief='solid')
    screen_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # For demonstration purposes, you could display a message or graphic here.
    screen_label = tk.Label(screen_frame, text="Large Screen Area", font=("Arial", 20))
    screen_label.place(relx=0.5, rely=0.5, anchor="center")

def update_algorithm_options(*args):
    # Clear current dropdown for algorithm specific options
    for widget in control_frame.grid_slaves(row=8, column=1):
        widget.grid_forget()
    
    algorithm_choice = algorithm_var.get()
    
    if algorithm_choice == "Greedy":
        # Dropdown for Greedy algorithm: options "a" and "b"
        greedy_options = ["a", "b"]
        greedy_dropdown = ttk.Combobox(control_frame, values=greedy_options, state="readonly")
        greedy_dropdown.grid(row=8, column=1, padx=5, pady=5)
        greedy_dropdown.current(0)  # Default value
    
    elif algorithm_choice == "Local Search":
        # Dropdown for Local Search algorithm: options "geometry", "rule", "overlaps"
        local_search_options = ["geometry", "rule", "overlaps"]
        local_search_dropdown = ttk.Combobox(control_frame, values=local_search_options, state="readonly")
        local_search_dropdown.grid(row=8, column=1, padx=5, pady=5)
        local_search_dropdown.current(0)  # Default value

def on_start():
    # This function is called when the Start button is pressed
    print("Start button pressed")
    
    # Retrieve values from the entries if needed
    anzahl_value = entry_anzahl.get()
    upper_bound_a_value = entry_upperBoundA.get()
    lower_bound_a_value = entry_lowerBoundA.get()
    upper_bound_b_value = entry_upperBoundB.get()
    lower_bound_b_value = entry_lowerBoundB.get()
    box_size_value = entry_box_size.get()
    algorithm_choice = algorithm_var.get()

    # Print values (or add processing logic here)
    print(f"Anzahl: {anzahl_value}, Upper Bound A: {upper_bound_a_value}, Lower Bound A: {lower_bound_a_value}, Upper Bound B: {upper_bound_b_value}, Lower Bound B: {lower_bound_b_value}")
    print(f"Box Size: {box_size_value}, Algorithm Choice: {algorithm_choice}")
    
    # Open the second window with the large screen area
    open_screen_window(box_size_value)

# Create the main window for input fields
root = tk.Tk()
root.title("Input Window")
root.geometry("400x400")  # Width x Height

# Right side: Fields and Start button
control_frame = tk.Frame(root, bd=2, relief='solid')
control_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Adding some fields to the control frame
# Example field 1: Label and Entry for "Anzahl"
label_anzahl = ttk.Label(control_frame, text="Anzahl:")
label_anzahl.grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_anzahl = ttk.Entry(control_frame)
entry_anzahl.grid(row=0, column=1, padx=5, pady=5)

# Example field 2: Label and Entry for "Upper Bound A"
label_upperBoundA = ttk.Label(control_frame, text="Upper Bound A:")
label_upperBoundA.grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_upperBoundA = ttk.Entry(control_frame)
entry_upperBoundA.grid(row=1, column=1, padx=5, pady=5)

# Example field 3: Label and Entry for "Lower Bound A"
label_lowerBoundA = ttk.Label(control_frame, text="Lower Bound A:")
label_lowerBoundA.grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_lowerBoundA = ttk.Entry(control_frame)
entry_lowerBoundA.grid(row=2, column=1, padx=5, pady=5)

# Example field 4: Label and Entry for "Upper Bound B"
label_upperBoundB = ttk.Label(control_frame, text="Upper Bound B:")
label_upperBoundB.grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_upperBoundB = ttk.Entry(control_frame)
entry_upperBoundB.grid(row=3, column=1, padx=5, pady=5)

# Example field 5: Label and Entry for "Lower Bound B"
label_lowerBoundB = ttk.Label(control_frame, text="Lower Bound B:")
label_lowerBoundB.grid(row=4, column=0, padx=5, pady=5, sticky="w")
entry_lowerBoundB = ttk.Entry(control_frame)
entry_lowerBoundB.grid(row=4, column=1, padx=5, pady=5)

# Box Size Field
label_box_size = ttk.Label(control_frame, text="Box Size:")
label_box_size.grid(row=5, column=0, padx=5, pady=5, sticky="w")
entry_box_size = ttk.Entry(control_frame)
entry_box_size.grid(row=5, column=1, padx=5, pady=5)

# Algorithm Choice (Greedy or Local Search)
label_algorithm = ttk.Label(control_frame, text="Algorithm:")
label_algorithm.grid(row=6, column=0, padx=5, pady=5, sticky="w")

algorithm_var = tk.StringVar()
algorithm_dropdown = ttk.Combobox(control_frame, textvariable=algorithm_var, values=["Greedy", "Local Search"], state="readonly")
algorithm_dropdown.grid(row=6, column=1, padx=5, pady=5)
algorithm_dropdown.current(0)  # Default value is "Greedy"
algorithm_var.trace("w", update_algorithm_options)  # Update options based on selection

# Placeholder for dropdown (Greedy: a/b or Local Search: geometry/rule/overlaps)
placeholder_label = ttk.Label(control_frame, text="Options:")
placeholder_label.grid(row=7, column=0, padx=5, pady=5, sticky="w")

# Start Button
start_button = ttk.Button(control_frame, text="Start", command=on_start)
start_button.grid(row=9, column=1, padx=5, pady=20, sticky="e")

# Run the application
root.mainloop()
