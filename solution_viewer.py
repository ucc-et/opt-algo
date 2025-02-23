import json
import tkinter as tk
from tkinter import filedialog
import random

from rectangle_packer_classes.problem_classes import Box, RecPac_Solution, Rectangle
from base_classes.ui_classes import GUI

class SolutionViewer(GUI):
    def __init__(self, root, solutions):
        self.root = root
        self.solutionsRaw = solutions
        self.solutions = []
        self.solutionsalgorithms = []
        self.rectangle_colors = {}
        self.current_type = "greedy"
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
        
        for solution in solutionsRaw:
            # Get metadata, with default values if missing
            algorithm = solution.get("algorithm", "Unknown Algorithm")
            strategy = solution.get("strategy", "No Strategy")
            neighborhood = solution.get("neighborhood", "No Neighborhood")
            
            # Access boxes directly, no longer inside "solution"
            boxes = solution.get("boxes", [])
            
            # Create RecPac_Solution object for visualization
            current_solution = RecPac_Solution()
            for box in boxes:
                current_box = Box(box_length)
                for rectangle in box:
                    current_box.add_item(Rectangle(rectangle["x"], rectangle["y"], rectangle["w"], rectangle["h"], rectangle["color"]))
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

        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack(pady=10)

        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        btn_zoom_in = tk.Button(frame_buttons, text="Zoom In", command=self.zoom_in)
        btn_zoom_in.grid(row=0, column=2, padx=5)
        
        btn_zoom_out = tk.Button(frame_buttons, text="Zoom Out", command=self.zoom_out)
        btn_zoom_out.grid(row=0, column=3, padx=5)
        
        btn_iterate_left = tk.Button(frame_buttons, text="<", command=self.lower_solution_index)
        btn_iterate_left.grid(row=1, column=2, padx=5)
        
        btn_iterate_right = tk.Button(frame_buttons, text=">", command=self.increase_solution_index)
        btn_iterate_right.grid(row=1, column=3, padx=5)
        
        # Labels for solution metadata
        self.label_algorithm = tk.Label(self.root, text=f"Algorithm: {self.solutionsalgorithms[self.current_index]['algorithm']}")
        self.label_algorithm.pack()
        
        self.label_strategy = tk.Label(self.root, text=f"Strategy: {self.solutionsalgorithms[self.current_index]['strategy']}")
        self.label_strategy.pack()
        
        self.label_neighborhood = tk.Label(self.root, text=f"Neighborhood: {self.solutionsalgorithms[self.current_index]['neighborhood']}")
        self.label_neighborhood.pack()
        
        self.label_solution_number = tk.Label(self.root, text=f"Solution: {self.current_index+1}/{len(self.solutions)}")
        self.label_solution_number.pack()

        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        
    def lower_solution_index(self):
        """
        Moves to the previous solution and updates labels.
        """
        if self.current_index > 0:
            self.current_index -= 1
            self.update_labels()
            self.redraw_canvas()

    def increase_solution_index(self):
        """
        Moves to the next solution and updates labels.
        """
        if self.current_index < len(self.solutions) - 1:
            self.current_index += 1
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

        
    def get_rectangle_color(self, rect):
        if len(self.rectangle_colors.keys()) == 0 or rect not in self.rectangle_colors.keys():
            color = random.choice(["red", "green", "blue", "yellow", "purple", "orange", "cyan"])
            self.rectangle_colors[rect] = color
        else:
            color = self.rectangle_colors[rect]
        return color

    def update_scrollregion(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def run_algorithm(self):
        pass
        
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
                x, y, w, h = rect.x, rect.y, rect.width, rect.height
                scaled_x = int(x * self.zoom_factor) + x_offset
                scaled_y = int(y * self.zoom_factor) + y_offset
                scaled_w = int(w * self.zoom_factor)
                scaled_h = int(h * self.zoom_factor)

                self.canvas.create_rectangle(
                    scaled_x, scaled_y,
                    scaled_x + scaled_w, scaled_y + scaled_h,
                    fill=self.get_rectangle_color(rect),
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
