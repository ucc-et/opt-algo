import json
import tkinter as tk
from tkinter import filedialog
import random

from objects import Box, RecPac_Solution, Rectangle

class SolutionViewer:
    def __init__(self, root, solutions):
        self.root = root
        self.solutionsRaw = solutions
        self.solutions = []
        self.rectangle_colors = {}
        self.current_type = "greedy"  # Start with Greedy solutions
        self.current_index = 0
        self.zoom_factor = 1.0
        self.zoom_steps = 0
        self.max_zoom_steps = 4
        
        self.setup_ui()
        self.parse_solutions()
        self.visualize_solution()
    
    def parse_solutions(self):
        
        solutionsRaw = self.solutionsRaw["solutions"]
        box_length = int(self.solutionsRaw["box_length"])
        
        for solution in solutionsRaw:
            current_solution = RecPac_Solution()
            for box in solution["boxes"]:
                current_box = Box(box_length)
                for rectangle in box:
                    current_box.add_rectangle(Rectangle(rectangle[0], rectangle[1], rectangle[2], rectangle[3]))
                current_solution.add_box(current_box)
            self.solutions.append(current_solution)
    
    def setup_ui(self):
        self.root.title("Optimierungsalgorithmen GUI")

        # Create input fields and place them in UI
        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack(pady=10)

        tk.Label(frame_inputs, text="Anzahl Rechtecke:").grid(row=0, column=0)
        self.entry_num_rectangles = tk.Entry(frame_inputs)
        self.entry_num_rectangles.grid(row=0, column=1)

        tk.Label(frame_inputs, text="Min Breite:").grid(row=1, column=0)
        self.entry_min_width = tk.Entry(frame_inputs)
        self.entry_min_width.grid(row=1, column=1)

        tk.Label(frame_inputs, text="Max Breite:").grid(row=2, column=0)
        self.entry_max_width = tk.Entry(frame_inputs)
        self.entry_max_width.grid(row=2, column=1)

        tk.Label(frame_inputs, text="Min Höhe:").grid(row=3, column=0)
        self.entry_min_height = tk.Entry(frame_inputs)
        self.entry_min_height.grid(row=3, column=1)

        tk.Label(frame_inputs, text="Max Höhe:").grid(row=4, column=0)
        self.entry_max_height = tk.Entry(frame_inputs)
        self.entry_max_height.grid(row=4, column=1)

        tk.Label(frame_inputs, text="Boxlänge L:").grid(row=5, column=0)
        self.entry_box_length = tk.Entry(frame_inputs)
        self.entry_box_length.grid(row=5, column=1)

        # Label for error messages
        self.error_label = tk.Label(self.root, text="", fg="red")
        self.error_label.pack()

        # Create Buttons in UI to Generate Instances and Start Packer
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        btn_zoom_in = tk.Button(frame_buttons, text="Zoom In", command=self.zoom_in)
        btn_zoom_in.grid(row=0, column=2, padx=5)
        
        btn_zoom_out = tk.Button(frame_buttons, text="Zoom Out", command=self.zoom_out)
        btn_zoom_out.grid(row=0, column=3, padx=5)

        # Create the scrollable canvas frame
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True)

        # Create the canvas
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Add vertical scrollbar
        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        # Configure the canvas to work with the vertical scrollbar
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
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
        
    def visualize_solution(self):
        self.canvas.delete("all")

        box_padding = 10 * self.zoom_factor  # Skaliere den Abstand zwischen den Boxen
        x_offset = 0
        y_offset = 0
        row_height = 0
        canvas_width = self.canvas.winfo_width()
        
        length = self.solutions[self.current_index].boxes[0].box_length

        for box_id, box in enumerate(self.solutions[self.current_index].boxes):
            scaled_box_length = int(length * length)

            # Überprüfen, ob die Box in die aktuelle Zeile passt
            if x_offset + scaled_box_length + box_padding > canvas_width:
                x_offset = 0
                y_offset += row_height + box_padding
                row_height = 0

            row_height = max(row_height, scaled_box_length)

            # Zeichne die Box
            self.canvas.create_rectangle(
                x_offset, y_offset,
                x_offset + scaled_box_length, y_offset + scaled_box_length,
                outline="black"
            )

            # Zeichne die Rechtecke innerhalb der Box
            for rect in box.rectangles:
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

            # Aktualisiere den x_offset für die nächste Box
            x_offset += scaled_box_length + box_padding

        self.update_scrollregion()
    
    def prev_solution(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_solution()
    
    def next_solution(self):
        if self.current_index < len(self.solutions.get(self.current_type, [])) - 1:
            self.current_index += 1
            self.display_solution()
    
    def zoom_in(self):
        if self.zoom_steps < self.max_zoom_steps:
            self.zoom_factor *= 1.2
            self.zoom_steps += 1
            self.redraw_canvas()
    
    def redraw_canvas(self):
        self.canvas.delete("all")
        self.visualize_solution(self.current_solution) 
    
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
            with open(file_path, "r") as file:
                return json.load(file)
        return {}
    
if __name__ == "__main__":
    root = tk.Tk()
    solutions = SolutionViewer.load_solutions()
    app = SolutionViewer(root, solutions)
    root.mainloop()
