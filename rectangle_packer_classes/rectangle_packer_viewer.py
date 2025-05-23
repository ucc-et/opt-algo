import json
from typing import List
from PIL import Image, ImageTk
from tkinter import ttk, filedialog
import tkinter as tk

from rectangle_packer_classes.problem_classes import Rectangle
from rectangle_packer_classes.helpers import Neighborhoods, generate_instances, GreedyStrategy, Rules
from base_classes.ui_classes import GUI, Tooltip


class RectanglePackerVisualizer(GUI):
    """A GUI for visualizing optimization algorithms for rectangle packing.
    Allows configuration and execution of various algorithms with step-wise visualization
    """
    def __init__(self, root, greedy_algorithm, local_search, backtracking, simulated_annealing):
        self.root = root
        self.greedy_algorithm = greedy_algorithm
        self.local_search = local_search
        self.backtracking = backtracking
        self.simulated_annealing = simulated_annealing
        
        # state management
        self.can_export_rectangles = "disabled"
        self.can_zoom = "disabled"
        self.available_colors = ["red", "green", "blue", "yellow", "purple", "orange", "cyan"]
        self.interim_solutions = []
        self.interim_index = 0
        self.interim_step_size = 1
        self.instances: List[Rectangle] = []
        self.box_size: int = 0
        self.rectangle_colors = {}
        self.zoom_factor = 1.0
        self.zoom_steps = 0
        self.max_zoom_steps = 4
        self.solution = None
        
        # init ui
        self.setup_ui()
    
    def setup_ui(self):
        """Sets up the GUI elements for the visualizer. 
        initializes input fields, buttons, progress bar and canvas
        """
        self.root.title("Optimierungsalgorithmen GUI")
        
        self.style_dropdown()
        
        self.load_icons()
        self.setup_inputs()
        self.setup_navigation()
        self.setup_canvas()
    
    def load_icons(self):
        self.zoom_in_icon = Image.open("assets/zoom-in.png").resize((30, 30))
        self.zoom_in_icon = ImageTk.PhotoImage(self.zoom_in_icon)
        self.zoom_out_icon = Image.open("assets/zoom-out.png").resize((30, 30))
        self.zoom_out_icon = ImageTk.PhotoImage(self.zoom_out_icon)
        self.import_icon = Image.open("assets/import.png").resize((30, 30))
        self.import_icon = ImageTk.PhotoImage(self.import_icon)
        self.export_icon = Image.open("assets/export.png").resize((30, 30))
        self.export_icon = ImageTk.PhotoImage(self.export_icon)
    
    def setup_inputs(self):

        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack(pady=10)

        tk.Label(frame_inputs, text="Anzahl Rechtecke:").grid(row=0, column=0)
        self.entry_num_rectangles = tk.Entry(frame_inputs)
        self.entry_num_rectangles.grid(row=0, column=1, pady=5)

        tk.Label(frame_inputs, text="Min Breite:").grid(row=1, column=0)
        self.entry_min_width = tk.Entry(frame_inputs)
        self.entry_min_width.grid(row=1, column=1, pady=5)

        tk.Label(frame_inputs, text="Max Breite:").grid(row=2, column=0)
        self.entry_max_width = tk.Entry(frame_inputs)
        self.entry_max_width.grid(row=2, column=1, pady=5)

        tk.Label(frame_inputs, text="Min Höhe:").grid(row=3, column=0)
        self.entry_min_height = tk.Entry(frame_inputs)
        self.entry_min_height.grid(row=3, column=1, pady=5)

        tk.Label(frame_inputs, text="Max Höhe:").grid(row=4, column=0)
        self.entry_max_height = tk.Entry(frame_inputs)
        self.entry_max_height.grid(row=4, column=1, pady=5)

        tk.Label(frame_inputs, text="Boxlänge L:").grid(row=5, column=0)
        self.entry_box_length = tk.Entry(frame_inputs)
        self.entry_box_length.grid(row=5, column=1, pady=5)
        
        # ===========================
        # Multi-Select Dropdown for Colors
        # ===========================
        self.selected_colors = tk.StringVar(value=self.available_colors)

        self.color_scheme_label = tk.Label(frame_inputs, text="Rechteckfarben:")
        self.color_scheme_label.grid(row=15, column=0, pady=5)

        self.color_multiselect = tk.Listbox(frame_inputs, listvariable=self.selected_colors, selectmode="multiple", height=5, exportselection=False)
        self.color_multiselect.grid(row=15, column=1, pady=5)
        for i in range(len(self.available_colors)):
            self.color_multiselect.select_set(i)  # Select all by default
            
        self.style_listbox(self.color_multiselect)

        # Add a scrollbar for color selection
        scrollbar = tk.Scrollbar(frame_inputs, orient="vertical", command=self.color_multiselect.yview)
        scrollbar.grid(row=15, column=2, sticky="ns")
        self.color_multiselect.config(yscrollcommand=scrollbar.set)

        self.algo_select_label = tk.Label(frame_inputs, text="Algorithmus wählen: ").grid(row=7, column=0, padx=5)
        self.algo_selector = ttk.Combobox(frame_inputs, values=["Greedy", "Lokale Suche", "Backtracking", "Simulated Annealing"], state="readonly")
        self.algo_selector.set("Greedy")
        self.algo_selector.grid(row=7, column=1, pady=5)

        self.strategy_label = ttk.Label(frame_inputs, text="Greedy Strategie wählen: ")
        self.strategy_label.grid(row=8, column=0, padx=5)
        self.greedy_strat = ttk.Combobox(frame_inputs, state="readonly", values=[GreedyStrategy.LARGEST_AREA_FIRST.value, GreedyStrategy.SMALLEST_AREA_FIRST.value, GreedyStrategy.LARGEST_ASPECT_RATIO_FIRST.value, GreedyStrategy.SMALLEST_ASPECT_RATIO.value])
        self.greedy_strat.set(GreedyStrategy.LARGEST_AREA_FIRST.value)
        self.greedy_strat.grid(row=8, column=1, pady=5)
        self.greedy_strat.grid_remove()
        self.strategy_label.grid_remove()

        self.neighborhood_label = ttk.Label(frame_inputs, text="Nachbarschaft wählen")
        self.neighborhood_label.grid(row=9, column=0, padx=5)
        self.local_search_neighborhood_selector = ttk.Combobox(frame_inputs, state="readonly", values=["Geometriebasiert", "Regelbasiert", "Überlappungen teilweise zulassen"])
        self.local_search_neighborhood_selector.set("Geometriebasiert")
        self.local_search_neighborhood_selector.grid(row=9, column=1, pady=5)
        self.local_search_neighborhood_selector.grid_remove()
        self.neighborhood_label.grid_remove()
        
        self.rulebased_strategy_label = ttk.Label(frame_inputs, text="Regel wählen: ")
        self.rulebased_strategy_label.grid(row=10, column=0, padx=5)
        self.rulebased_strat = ttk.Combobox(frame_inputs, state="readonly", values=[Rules.HEIGHT_FIRST.value, Rules.WIDTH_FIRST.value, Rules.AREA_FIRST.value])
        self.rulebased_strat.set(Rules.HEIGHT_FIRST.value)
        self.rulebased_strat.grid(row=10, column=1, pady=5)
        self.rulebased_strat.grid_remove()
        self.rulebased_strategy_label.grid_remove()

        self.local_search_max_iterations_label = tk.Label(frame_inputs, text="Maximum Iterationen")
        self.local_search_max_iterations_label.grid(row=11, column=0, pady=5)
        self.local_search_max_iterations = tk.Entry(frame_inputs)
        self.local_search_max_iterations.grid(row=11, column=1)
        self.local_search_max_iterations.insert(0, "21")
        
        self.start_temperature_label = tk.Label(frame_inputs, text="Starttemperatur")
        self.start_temperature_label.grid(row=10, column=0)
        self.start_temperature = tk.Entry(frame_inputs)
        self.start_temperature.insert(0,"1000")
        self.start_temperature.grid(row=10, column=1)
        self.start_temperature_label.grid_remove()
        self.start_temperature.grid_remove()
        
        self.end_temperature_label = tk.Label(frame_inputs, text="Endtemperatur")
        self.end_temperature_label.grid(row=11, column=0)
        self.end_temperature = tk.Entry(frame_inputs)
        self.end_temperature.insert(0,"5")
        self.end_temperature.grid(row=11, column=1)
        self.end_temperature_label.grid_remove()
        self.end_temperature.grid_remove()
        
        self.cool_rate_label = tk.Label(frame_inputs, text="Abkühlrate (in %)")
        self.cool_rate_label.grid(row=12, column=0)
        self.cool_rate = tk.Entry(frame_inputs)
        self.cool_rate.insert(0,"5")
        self.cool_rate.grid(row=12, column=1)
        self.cool_rate_label.grid_remove()
        self.cool_rate.grid_remove()
        
        self.cool_rate_constant_label = tk.Label(frame_inputs, text="Temperature konstant für x Iterationen: ")
        self.cool_rate_constant_label.grid(row=13, column=0)
        self.cool_rate_constant = tk.Entry(frame_inputs)
        self.cool_rate_constant.insert(0, "10")
        self.cool_rate_constant.grid(row=13, column=1)
        self.cool_rate_constant.grid_remove()
        self.cool_rate_constant_label.grid_remove()
        
        self.max_time_label = tk.Label(frame_inputs, text="Maximale Laufzeit (in Sekunden): ")
        self.max_time_label.grid(row=14, column=0)
        self.max_time = tk.Entry(frame_inputs)
        self.max_time.insert(0,"10")
        self.max_time.grid(row=14, column=1)
        self.max_time_label.grid_remove()
        self.max_time.grid_remove()

        self.algo_selector.bind("<<ComboboxSelected>>", self.update_algorithm)
        self.local_search_neighborhood_selector.bind("<<ComboboxSelected>>", self.update_algorithm)
        self.update_algorithm()

        self.error_label = tk.Label(self.root, text="", fg="red")
        self.error_label.pack()

    def setup_navigation(self):

        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        btn_generate = tk.Button(frame_buttons, text="Rechtecke generieren", command=self.generate_rectangles_clicked)
        btn_generate.grid(row=0, column=0, padx=5)

        btn_run = tk.Button(frame_buttons, text="Algorithmus ausführen", command=self.run_algorithm)
        btn_run.grid(row=1, column=0, padx=5)
        
        self.btn_import = tk.Button(frame_buttons, image=self.import_icon, width=30, borderwidth=0,command=self.import_rectangles)
        self.btn_import.grid(row=1, column=1, padx=5)
        Tooltip(self.btn_import, "Importiere Rechtecke")

        self.btn_export = tk.Button(frame_buttons, image=self.export_icon, width=30, borderwidth=0, state="disabled",command=self.export_rectangles)
        self.btn_export.grid(row=1, column=2, padx=5)
        Tooltip(self.btn_export, "Exportiere Rechtecke")

        self.btn_zoom_in = tk.Button(frame_buttons, image=self.zoom_in_icon, borderwidth=0, state="disabled", command=self.zoom_in)
        self.btn_zoom_in.grid(row=1, column=3, padx=5)
        Tooltip(self.btn_zoom_in, "Zoom In")
        
        self.btn_zoom_out = tk.Button(frame_buttons, image=self.zoom_out_icon, borderwidth=0, state="disabled",command=self.zoom_out)
        self.btn_zoom_out.grid(row=1, column=4, padx=5)
        Tooltip(self.btn_zoom_out, "Zoome Out")

        self.label_status = tk.Label(self.root, text="Status: Bereit")
        self.label_status.pack()
        
        frame_navigation = tk.Frame(self.root)
        frame_navigation.pack(pady=10)
        
        self.step_size_label = tk.Label(frame_navigation, text="Schrittgröße:")
        self.step_size_label.grid(row=0, column=0, padx=5)
        self.step_size_entry = tk.Entry(frame_navigation, width=5)
        self.step_size_entry.insert(0, "1")  # Default step size
        self.step_size_entry.grid(row=0, column=1, padx=5)
        self.step_size_entry.bind("<KeyRelease>", self.update_step_size)
        
        # Position Label for interim solutions (e.g., "Step 3 of 10")
        self.position_label = tk.Label(frame_navigation, text="Schritt 0 von 0")
        self.position_label.grid(row=0, column=2, padx=10)
        
        self.btn_first = tk.Button(frame_navigation, text="<<", command=self.go_to_first)
        self.btn_first.grid(row=1, column=0, padx=5)
        
        self.btn_left_sol = tk.Button(frame_navigation, text="<", command=self.go_left_solution)
        self.btn_left_sol.grid(row=1, column=1, padx=5)
        
        self.progress = ttk.Progressbar(frame_navigation, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=1, column=2, padx=5)
        
        
        self.btn_right_sol = tk.Button(frame_navigation, text=">", command=self.go_right_solution)
        self.btn_right_sol.grid(row=1, column=3, padx=5)
        
        self.btn_last = tk.Button(frame_navigation, text=">>", command=self.go_to_last)
        self.btn_last.grid(row=1, column=4, padx=5)
        
        self.update_progress_bar()

    def style_listbox(self, listbox):
        """Styles the Listbox used in the Multi-Select Dropdown."""
        
        listbox.config(
            bg="#757574",          # White background
            fg="black",          # Black text color
            selectbackground="white",  # Light gray background when selected
            selectforeground="black",    # Keep text black when selected
            highlightthickness=0,  # Remove border highlight
            relief="flat",         # Flat border style for a modern look
            activestyle="none"     # Remove underlined text for active item
        )


    def style_dropdown(self):
        """
        Customize appearance of multi select dropdown, cause tkinter native way is not so pretty
        """
        style = ttk.Style()
        
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground="white",
            selectforeground="black",
            background="white",
            foreground="black",
            selectbackground="#D3D3D3",
            padding=5
        )
        
        style.map("TCombobox",
                fieldbackground=[('readonly', 'white')],
                background=[('readonly', 'white')],
                selectbackground=[('focus', '#D3D3D3')],
                selectforeground=[('focus', 'black')],
                )

        style.map('TCombobox',
                background=[('active', '#F0F0F0')],
                highlightbackground=[('focus', '#F0F0F0')],
                highlightcolor=[('focus', '#F0F0F0')]
                )

    def setup_canvas(self):

        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
    
    # =======================================
    #              Navigation 
    # =======================================
    
    def go_to_first(self):
        self.interim_index = 0
        self.solution = self.interim_solutions[self.interim_index]
        
        self.redraw_canvas()
        self.update_position_label()
        self.update_progress_bar()
               
    def go_to_last(self):
        if len(self.interim_solutions) > 0 :
            self.interim_index = len(self.interim_solutions)-1
            self.solution = self.interim_solutions[self.interim_index]
            
            self.redraw_canvas()
            self.update_position_label()
            self.update_progress_bar()
        
    def update_step_size(self, event=None):
        try:
            if self.step_size_entry.get() == "":
                return
            # Get the step size from the input field
            step_size = int(self.step_size_entry.get())
            
            # Ensure step size is at least 1
            if step_size < 1:
                raise ValueError
            
            self.interim_step_size = step_size
        except ValueError:
            # Reset to default step size if invalid input
            self.interim_step_size = 1
            self.step_size_entry.delete(0, tk.END)
            self.step_size_entry.insert(0, "1")
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        
    def zoom_in(self):
        if(self.zoom_steps < 10):
            self.btn_zoom_in.config(state="normal")
            self.zoom_factor *= 1.2
            self.zoom_steps += 1
            self.redraw_canvas()
        else:
            self.btn_zoom_in.config(state="disabled")
        
    def zoom_out(self):
        if(self.zoom_steps > -1):
            self.btn_zoom_out.config(state="normal")
            self.zoom_factor /= 1.2
            self.zoom_steps -= 1
            self.redraw_canvas()
        else:
            self.btn_zoom_out.config(state="disabled")
    
    def update_scrollregion(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))   
    
    def go_left_solution(self):
        new_index = max(0, self.interim_index - self.interim_step_size)
    
        # Only update if the index changes
        if new_index != self.interim_index:
            self.interim_index = new_index
            self.solution = self.interim_solutions[self.interim_index]
            self.redraw_canvas()
            self.update_progress_bar()
            self.update_position_label()
    
    def go_right_solution(self):
        # Calculate new index with step size
        new_index = min(len(self.interim_solutions) - 1, self.interim_index + self.interim_step_size)
        
        # Only update if the index changes
        if new_index != self.interim_index:
            self.interim_index = new_index
            self.solution = self.interim_solutions[self.interim_index]
            self.redraw_canvas()
            self.update_progress_bar()
            self.update_position_label()
                            
    # =======================================
    #     Solution Handling and execution
    # =======================================
         
    def update_algorithm(self, *args):
        if self.algo_selector.get() == "Greedy":
            self.show_greedy_widgets()
            self.hide_local_search_widgets()
            self.hide_simulated_annealing_widgets()
        elif self.algo_selector.get() == "Lokale Suche":
            self.show_local_search_widgets()
            self.hide_greedy_widgets()
            self.hide_simulated_annealing_widgets()
            if self.local_search_neighborhood_selector.get() == "Regelbasiert":
                self.rulebased_strat.grid()
                self.rulebased_strategy_label.grid()
            else:
                self.rulebased_strat.grid_remove()
                self.rulebased_strategy_label.grid_remove()
        elif self.algo_selector.get() == "Backtracking":
            self.hide_local_search_widgets()
            self.hide_greedy_widgets()
            self.hide_simulated_annealing_widgets()
        elif self.algo_selector.get() == "Simulated Annealing":
            self.hide_greedy_widgets()
            self.show_simulated_annealing_widgets()
            self.hide_local_search_widgets()
           
    def validate_inputs(self):
        errors = []

        try:
            num_rectangles = int(self.entry_num_rectangles.get())
            min_width = int(self.entry_min_width.get())
            max_width = int(self.entry_max_width.get())
            min_height = int(self.entry_min_height.get())
            max_height = int(self.entry_max_height.get())
            box_length = int(self.entry_box_length.get())

            if num_rectangles < 1:
                errors.append("Es muss mind. 1 rechteck geben")
            if min_width > max_width:
                errors.append("Min Breite größer als Max Breite")
            if min_height > max_height:
                errors.append("Min Höhe größer als Max Höhe")
            if box_length < 1:
                errors.append("Die Länge der Box muss mind. 1 sein")
            if min_width > box_length or max_width > box_length or min_height > box_length or max_height > box_length:
                errors.append("Die Rechtecke dürfen nicht breiter/höher sein als die Box")
            if self.local_search_max_iterations_is_visible:
                max_iterations = int(self.local_search_max_iterations.get())
                if max_iterations < 1:
                    errors.append("Es muss mindestens eine Iteration ausgeführt werden")

        except ValueError:
            errors.append("Bitte geben Sie gültige Zahlen ein und befüllen Sie alle Felder")

        return errors

    def generate_rectangles_clicked(self):
        self.error_label.config(text="")
        errors = self.validate_inputs()

        if errors:
            self.error_label.config(text="\n".join(errors), fg="red")
        else:
            n = int(self.entry_num_rectangles.get())
            min_w = int(self.entry_min_width.get())
            max_w = int(self.entry_max_width.get())
            min_h = int(self.entry_min_height.get())
            max_h = int(self.entry_max_height.get())
            self.box_size = int(self.entry_box_length.get())
            
            selected_indices = self.color_multiselect.curselection()
            selected_colors = [self.available_colors[i] for i in selected_indices]
            
            if not selected_colors:
                selected_colors = self.available_colors
            
            self.instances = generate_instances(n, min_w, max_w, min_h, max_h, selected_colors)
            self.btn_export.config(state="normal")
            self.label_status.config(text=f"{n} Rechtecke generiert!")
        
    def run_algorithm(self):
        algorithm = self.algo_selector.get()
        self.interim_solutions = []
        self.interim_index = 0
        self.update_progress_bar()
        self.zoom_factor = 1.2
        self.zoom_steps = 0
        self.rectangle_colors = {}
        
        if algorithm == "Greedy":
            self.solution, self.interim_solutions = self.greedy_algorithm(
                self.instances, 
                self.box_size, 
                self.greedy_strat.get()
            )
        elif algorithm == "Lokale Suche":
            neighborhood = self.local_search_neighborhood_selector.get()
            rulebased_strategy = self.rulebased_strat.get() if neighborhood == Neighborhoods.RULE.value else ""
            self.solution, self.interim_solutions = self.local_search(
                self.instances, 
                self.box_size, 
                neighborhood,
                rulebased_strategy,
                int(self.local_search_max_iterations.get())
            )
        elif algorithm == "Backtracking":
            self.solution, self.interim_solutions = self.backtracking(self.instances, self.box_size)
        elif algorithm == "Simulated Annealing":
            self.run_simulated_annealing()
        
        self.interim_index = len(self.interim_solutions)-1
        self.remove_duplicates()
        self.update_progress_bar()
        self.update_position_label()
        self.draw()

    def run_simulated_annealing(self):
        neighborhood = Neighborhoods.GEOMETRY.value
        start_temp = int(self.start_temperature.get())
        end_temp = int(self.end_temperature.get())
        cool_down_rate = int(self.cool_rate.get())
        max_time = int(self.max_time.get())
        constant = int(self.cool_rate_constant.get())
        rulebased_strategy = self.rulebased_strat.get() if neighborhood == Neighborhoods.RULE.value else ""
        self.solution, self.interim_solutions = self.simulated_annealing(self.instances, self.box_size, neighborhood, rulebased_strategy, start_temp, end_temp, (100-cool_down_rate)/100, constant, max_time)    

    # =======================================
    #         Visualization Methods
    # =======================================

    def draw(self):
        self.canvas.delete("all")
        
        box_padding = 10 * self.zoom_factor
        x_offset = 0
        y_offset = 0
        row_height = 0
        canvas_width = self.canvas.winfo_width()

        for box_id, box in enumerate(self.solution.boxes):
            scaled_box_length = int(self.box_size * self.zoom_factor)

            # apply zooming dimensions without distorting ratios
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
                x, y, w, h, c = rect.x, rect.y, rect.width, rect.height, rect.color
                scaled_x = int(x * self.zoom_factor) + x_offset
                scaled_y = int(y * self.zoom_factor) + y_offset
                scaled_w = int(w * self.zoom_factor)
                scaled_h = int(h * self.zoom_factor)

                self.canvas.create_rectangle(
                    scaled_x, scaled_y,
                    scaled_x + scaled_w, scaled_y + scaled_h,
                    fill=c,
                    outline="black"
                )

            x_offset += scaled_box_length + box_padding
        self.btn_zoom_in.config(state="normal")
        self.btn_zoom_out.config(state="normal")
        self.update_scrollregion()
       
    def redraw_canvas(self):
        self.canvas.delete("all")
        self.draw()
    
    def update_position_label(self):
        total_steps = len(self.interim_solutions)
        current_step = self.interim_index + 1 if total_steps > 0 else 0
        
        # Update the label with current step and total count
        self.position_label.config(text=f"Schritt {current_step} von {total_steps}")
    
    def update_progress_bar(self):
        if len(self.interim_solutions) > 0:
            progress_percentage = (self.interim_index + 1) / len(self.interim_solutions) * 100
            self.progress['value'] = progress_percentage
        else:
            self.progress['value'] = 0
    
    def show_greedy_widgets(self):
        self.strategy_label.grid()
        self.greedy_strat.grid()
    
    def show_local_search_widgets(self):
        self.local_search_neighborhood_selector.grid()
        self.local_search_max_iterations.grid()
        self.local_search_max_iterations_label.grid()
        self.neighborhood_label.grid()
        self.local_search_max_iterations_is_visible = True
    
    def show_simulated_annealing_widgets(self):
        self.start_temperature.grid()
        self.start_temperature_label.grid()
        self.end_temperature.grid()
        self.end_temperature_label.grid()
        self.cool_rate_label.grid()
        self.cool_rate.grid()
        self.max_time.grid()
        self.max_time_label.grid()
        self.cool_rate_constant.grid()
        self.cool_rate_constant_label.grid()
    
    def hide_greedy_widgets(self):
        self.greedy_strat.grid_remove()
        self.strategy_label.grid_remove()
    
    def hide_local_search_widgets(self):
        self.local_search_neighborhood_selector.grid_remove()
        self.local_search_max_iterations.grid_remove()
        self.local_search_max_iterations_label.grid_remove()
        self.neighborhood_label.grid_remove()
        self.local_search_max_iterations_is_visible = False
        self.rulebased_strat.grid_remove()
        self.rulebased_strategy_label.grid_remove()
    
    def hide_simulated_annealing_widgets(self):
        self.start_temperature.grid_remove()
        self.start_temperature_label.grid_remove()
        self.end_temperature.grid_remove()
        self.end_temperature_label.grid_remove()
        self.cool_rate_label.grid_remove()
        self.cool_rate.grid_remove()
        self.max_time.grid_remove()
        self.max_time_label.grid_remove()
        self.cool_rate_constant.grid_remove()
        self.cool_rate_constant_label.grid_remove()
    # =======================================
    #     Utility and helper methods
    # =======================================
            
    def solution_to_tuple(self, sol):
        """
        Converts a solution into a nested tuple representation.

        Args:
            solution (RecPac_Solution): The solution to be converted.

        Returns:
            tuple: A nested tuple representation of the solution which is hashable.
        """
        normalized_boxes = []
        for box in sol.boxes:
            normalized_rects = sorted(
                [(rect.x, rect.y, rect.width, rect.height, rect.color) for rect in box.items]
            )
            normalized_boxes.append(tuple(normalized_rects))
    
        return tuple(normalized_boxes)
        
    def remove_duplicates(self):
        """
        Removes duplicated solutions fromt he interim_solutions, 
        to have individual steps in the viz.
        """
        if len(self.interim_solutions) > 1:
            seen_hashes = set()
            unique_solutions = []

            for solution in self.interim_solutions:
                # Convert to tuples and hash
                canonical_tuple = self.solution_to_tuple(solution)
                solution_hash = hash(canonical_tuple)
                
                # Only add if this configuration hasn't been seen before
                if solution_hash not in seen_hashes:
                    seen_hashes.add(solution_hash)
                    unique_solutions.append(solution)
            self.interim_solutions = unique_solutions
            self.interim_index = len(self.interim_solutions)-1
    
            
    def import_rectangles(self):
        """
        Method that allows the user to import a list of rectangles, which has been exported before.
        """
        # open file dialog
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    # read file data
                    data = json.load(file)
                    
                    # save data into the input boxes and configuration
                    self.instances = [Rectangle(rect[0], rect[1], rect[2], rect[3], rect[4]) for rect in data.get("rectangles", [])]
                    self.box_size = data.get("box_length", 0)
                    
                    self.entry_num_rectangles.delete(0, tk.END)
                    self.entry_num_rectangles.insert(0, data.get("num_rectangles", ""))
                    
                    self.entry_min_width.delete(0, tk.END)
                    self.entry_min_width.insert(0, data.get("min_width", ""))
                    
                    self.entry_max_width.delete(0, tk.END)
                    self.entry_max_width.insert(0, data.get("max_width", ""))
                    
                    self.entry_min_height.delete(0, tk.END)
                    self.entry_min_height.insert(0, data.get("min_height", ""))
                    
                    self.entry_max_height.delete(0, tk.END)
                    self.entry_max_height.insert(0, data.get("max_height", ""))
                    
                    self.entry_box_length.delete(0, tk.END)
                    self.entry_box_length.insert(0, self.box_size)
                    
                    self.label_status.config(text="Rechtecke erfolgreich importiert!")
            except Exception as e:
                self.error_label.config(text=f"Fehler beim Importieren: {e}", fg="red")
    
    def export_rectangles(self):
        """
        Method that allows the user to export the last generated list of rectangles, for later import
        """
        default_filename = "rectangles.json"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    data = {
                        "rectangles": [(instance.x, instance.y, instance.width, instance.height, instance.color) for instance in self.instances],
                        "box_length": self.box_size,
                        "num_rectangles": len(self.instances),
                        "min_width": self.entry_min_width.get(),
                        "max_width": self.entry_max_width.get(),
                        "min_height": self.entry_min_height.get(),
                        "max_height": self.entry_max_height.get(),
                    }
                    json.dump(data, file)
                    self.label_status.config(text="Rechtecke erfolgreich exportiert!")
            except Exception as e:
                self.error_label.config(text=f"Fehler beim Exportieren: {e}", fg="red")