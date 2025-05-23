import json
import tkinter as tk
from tkinter import filedialog
import random
import rectangle_packer_classes.problem_classes
from base_classes.ui_classes import GUI

class SolutionViewer(GUI):
    """
    GUI class to visualize solutions of the rectangle packing test environment.

    """
    def __init__(self, root, solutions):
        self.root = root
        self.solutionsRaw = solutions
        self.solutions = []
        self.solutionsalgorithms = []
        self.rectangle_colors = {}
        
        self.step_size = 1
        self.current_index = 0
        self.zoom_factor = 1.0
        self.zoom_steps = 0
        self.max_zoom_steps = 7
        
        self.parse_solutions()
        self.setup_ui()
        self.draw()
    
    def parse_solutions(self):
        """
        Parses the loaded solutions from the JSON file.
        Handles the new structure from the updated TestEnvironment.
        """
        solutionsRaw = self.solutionsRaw["solutions"]
        box_length = int(self.solutionsRaw["box_length"])
        
        # each solution prase
        for solution in solutionsRaw:
            # Get metadata, with defaults
            algorithm = solution.get("algorithm", "Unknown Algorithm")
            strategy = solution.get("strategy", "No Strategy")
            neighborhood = solution.get("neighborhood", "No Neighborhood")
            
            # Access boxes directly
            boxes = solution.get("boxes", [])
            
            # Create RecPac_Solution object for visualization
            current_solution = rectangle_packer_classes.problem_classes.RecPac_Solution()
            for box in boxes:
                current_box = rectangle_packer_classes.problem_classes.Box(box_length)
                for rectangle in box:
                    current_box.add_item(rectangle_packer_classes.problem_classes.Rectangle(rectangle["x"], rectangle["y"], rectangle["w"], rectangle["h"], rectangle["color"]))
                current_solution.add_box(current_box)
            
            # Store parsed solution and metadata
            self.solutions.append(current_solution)
            self.solutionsalgorithms.append({
                "algorithm": algorithm,
                "strategy": strategy,
                "neighborhood": neighborhood
            })
    
    def setup_ui(self):
        """
        Sets up the UI components for the Solution Viewer.
        """
        self.root.title("Solution Viewer")

        # Input and nav
        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack(pady=10)

        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        # Zoom control
        btn_zoom_in = tk.Button(frame_buttons, text="Zoom In", command=self.zoom_in)
        btn_zoom_in.grid(row=0, column=2, padx=5)
        
        btn_zoom_out = tk.Button(frame_buttons, text="Zoom Out", command=self.zoom_out)
        btn_zoom_out.grid(row=0, column=3, padx=5)
        
        self.step_size_label = tk.Label(frame_buttons, text="Schrittgröße: ")
        self.step_size_entry = tk.Entry(frame_buttons, width=5)
        self.step_size_entry.insert(0, "1")  # Default step size
        self.step_size_entry.bind("<KeyRelease>", self.update_step_size)
        
        btn_iterate_start = tk.Button(frame_buttons, text="<<", command=self.jump_to_start)
        btn_iterate_start.grid(row=2, column=1, padx=5)
        
        btn_iterate_left = tk.Button(frame_buttons, text="<", command=self.lower_solution_index)
        btn_iterate_left.grid(row=2, column=2, padx=5)
        
        btn_iterate_right = tk.Button(frame_buttons, text=">", command=self.increase_solution_index)
        btn_iterate_right.grid(row=2, column=3, padx=5)
        
        btn_iterate_end = tk.Button(frame_buttons, text=">>", command=self.jump_to_end)
        btn_iterate_end.grid(row=2, column=4, padx=5)
        
        # Labels for solution metadata
        self.label_algorithm = tk.Label(self.root, text=f"Algorithm: {self.solutionsalgorithms[self.current_index]['algorithm']}")
        self.label_algorithm.pack()
        
        self.label_strategy = tk.Label(self.root, text=f"Strategy: {self.solutionsalgorithms[self.current_index]['strategy']}")
        self.label_strategy.pack()
        
        self.label_neighborhood = tk.Label(self.root, text=f"Neighborhood: {self.solutionsalgorithms[self.current_index]['neighborhood']}")
        self.label_neighborhood.pack()
        
        self.label_solution_number = tk.Label(self.root, text=f"Solution: {self.current_index+1}/{len(self.solutions)}")
        self.label_solution_number.pack()

        # Canvas for solution display
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.step_size_entry.focus_set()

    def jump_to_start(self):
        self.current_index = 0
        self.update_labels()
        self.redraw_canvas()
        
    def jump_to_end(self):
        self.current_index = len(self.solutions)-1
        self.update_labels()
        self.redraw_canvas()

        
    def lower_solution_index(self):
        """
        Moves to the previous solution and updates labels.
        """
        new_index = max(0, self.current_index - self.step_size)
        if new_index != self.current_index:
            self.current_index = new_index
            self.update_labels()
            self.redraw_canvas()


    def update_step_size(self, event=None):
        try:
            if self.step_size_entry.get() == "":
                return
            # Get the step size from the input field
            step_size = int(self.step_size_entry.get())
            
            # Ensure step size is at least 1
            if step_size < 1:
                raise ValueError
            
            self.step_size = step_size
        except ValueError:
            # Reset to default step size if invalid input
            self.step_size = 1
            self.step_size_entry.delete(0, tk.END)
            self.step_size_entry.insert(0, "1")
            
            

    def increase_solution_index(self):
        """
        Moves to the next solution and updates labels.
        """
        new_index = min(len(self.solutions) - 1, self.current_index + self.step_size)
        if new_index != self.current_index:
            self.current_index = new_index
            self.update_labels()
            self.redraw_canvas()

    def update_labels(self):
        """
        Updates the labels to reflect the current solution's metadata.
        """
        self.label_algorithm.config(text=f"Algorithm: {self.solutionsalgorithms[self.current_index]['algorithm']}")
        self.label_strategy.config(text=f"Strategy: {self.solutionsalgorithms[self.current_index]['strategy']}")
        self.label_neighborhood.config(text=f"Neighborhood: {self.solutionsalgorithms[self.current_index]['neighborhood']}")
        self.label_solution_number.config(text=f"Solution: {self.current_index+1}/{len(self.solutions)}")

    def update_scrollregion(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def draw(self):
        self.canvas.delete("all")

        box_padding = 10 * self.zoom_factor
        x_offset = 0
        y_offset = 0
        row_height = 0
        canvas_width = self.canvas.winfo_width()
        
        length = self.solutions[self.current_index].boxes[0].box_length

        for box_id, box in enumerate(self.solutions[self.current_index].boxes):
            scaled_box_length = int(length * self.zoom_factor)

            if x_offset + scaled_box_length + box_padding > canvas_width:
                x_offset = 0
                y_offset += row_height + box_padding
                row_height = 0

            row_height = max(row_height, scaled_box_length)

            self.canvas.create_rectangle(
                x_offset, y_offset,
                x_offset + scaled_box_length, y_offset + scaled_box_length,
                outline="black"
            )

            for rect in box.items:
                x, y, w, h, color = rect.x, rect.y, rect.width, rect.height, rect.color
                scaled_x = int(x * self.zoom_factor) + x_offset
                scaled_y = int(y * self.zoom_factor) + y_offset
                scaled_w = int(w * self.zoom_factor)
                scaled_h = int(h * self.zoom_factor)

                self.canvas.create_rectangle(
                    scaled_x, scaled_y,
                    scaled_x + scaled_w, scaled_y + scaled_h,
                    fill=color,
                    outline="black"
                )

            x_offset += scaled_box_length + box_padding

        self.update_scrollregion()
    
    def zoom_in(self):
        if self.zoom_steps < self.max_zoom_steps:
            self.zoom_factor *= 1.2
            self.zoom_steps += 1
            self.redraw_canvas()
    
    def redraw_canvas(self):
        self.canvas.delete("all")
        self.draw() 
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def zoom_out(self):
        if self.zoom_steps > -1:
            self.zoom_factor /= 1.2
            self.zoom_steps -= 1
            self.redraw_canvas()
    
    @staticmethod
    def load_solutions():
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}
    
if __name__ == "__main__":
    root = tk.Tk()
    solutions = SolutionViewer.load_solutions()
    app = SolutionViewer(root, solutions)
    root.mainloop()
