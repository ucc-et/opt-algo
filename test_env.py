import copy
from datetime import datetime
import os
import random
import time
from solvers.algorithms import Greedy, LocalSearch
#from classes.helpers import generate_instances, apply_greedy_strategy
import classes.helpers
from solvers.neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy

import json

from classes import Box, RecPac_Solution, RectanglePacker

class Test_Environment:
    def __init__(self):
        self.instances = []
        self.box_length = -1
        self.greedy_strategy = None
        self.neighborhood = None
        self.max_iterations = 21
        self.greedy_solutions = []
        self.local_search_solutions = []
        
        self.times_greedy = []
        self.times_local_search = []
    
    def __repr__(self):
        return f"Test_Environment(box_length={self.box_length}, greedy_strategy={self.greedy_strategy}, neighborhood={self.neighborhood}, max_iterations={self.max_iterations})"
    
    def run_greedy(self):
        print("\nStarte Greedy-Algorithmus...")
        for i, instance_set in enumerate(self.instances):
            start_time = time.time()
            print(f"->Verarbeite Instanz {i+1}/{len(self.instances)} mit {len(instance_set)} Rechtecken...")
            
            instance_set = classes.helpers.apply_greedy_strategy(instance_set, self.greedy_strategy)
            
            problem = RectanglePacker(instance_set, self.box_length)
            solver = Greedy(problem, RecPac_Solution, self.greedy_strategy)
            solution = solver.solve()
            self.times_greedy.append(time.time() - start_time)
            self.greedy_solutions.append(solution)
            
        print(f"\nGreedy-Algorithmen abgeschlossen.")
        pass
    
    def generate_bad_solution(self, rectangles, box_length):
        bad_solution = RecPac_Solution()

        for rect in rectangles:
            new_box = Box(box_length)

            if random.random() < 0.5:
                rect.width, rect.height = rect.height, rect.width

            rect.x = random.randint(0, box_length - rect.width)
            rect.y = random.randint(0, box_length - rect.height)

            new_box.add_rectangle(rect)
            bad_solution.add_box(new_box)
        return bad_solution
    
    def run_local_search(self):
        print("\nStarte lokale Suche...")
        for i, instance_set in enumerate(self.instances):
            start_time = time.time()
            print(f"-> Verarbeite Instanz {i+1}/{len(self.instances)} mit {len(instance_set)} Rechtecken...")
            
            instance_set_copy = copy.deepcopy(instance_set)
            problem = RectanglePacker(instance_set_copy, self.box_length)
            
            local_search_neighborhoods = {1: GeometryBasedStrategy(problem, RecPac_Solution), 2: RuleBasedStrategy(problem), 3: OverlapStrategy()}
            
            if type(self.neighborhood) == int:
                self.neighborhood = local_search_neighborhoods[self.neighborhood]
            start_solution = self.generate_bad_solution(instance_set_copy, self.box_length)
            solver = LocalSearch(problem, start_solution, self.max_iterations, self.neighborhood)
            solution = solver.solve()
            
            self.times_local_search.append(time.time() - start_time)
            self.local_search_solutions.append(solution)

        elapsed_time = time.time() - start_time
        print(f"\nLokale Suche abgeschlossen. Gesamtdauer: {elapsed_time:.6f} Sekunden")
    
    def generate_instances(self, instance_count, rectangle_count, min_breite, min_hoehe, max_breite, max_hoehe):        
        for _ in range(instance_count):
            self.instances.append(classes.helpers.generate_instances(rectangle_count, min_breite, max_breite, min_hoehe, max_hoehe))
        
    def run(self):
        self.run_greedy()
        self.run_local_search()
        self.save_solutions()
        self.create_protocol()

    def save_solutions(self):
        with open("test_env_solutions.json", "w") as f:
            
            obj = {"box_length": self.box_length, "solutions": []}
            
            
            for solution in self.greedy_solutions:
                current = {"boxes": [], "algorithm": "greedy"}
                for box in solution.boxes:
                    current_box = [{"x": rect.x, "y": rect.y, "w": rect.width, "h": rect.height} for rect in box.items]
                    current["boxes"].append(current_box)
                obj["solutions"].append(current)
            
            for solution in self.local_search_solutions:
                current = {"boxes": [], "algorithm": "local_search"}
                for box in solution.boxes:
                    current_box = [{"x": rect.x, "y": rect.y, "w": rect.width, "h": rect.height} for rect in box.items]
                    current["boxes"].append(current_box)
                obj["solutions"].append(current)
                
            json.dump(obj, f, indent=4)

    def create_protocol(self):
        if not os.path.exists("protocols"):
            os.makedirs("protocols")
        
        protocol_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totale_run_time": sum(x for x in self.times_greedy)+sum(x for x in self.times_local_search),
            "box_length": self.box_length,
            "greedy_strategy": self.greedy_strategy,
            "neighborhood": str(self.neighborhood.__class__.__name__) if not isinstance(self.neighborhood, int) else self.neighborhood,
            "max_iterations": self.max_iterations,
            "total_instances": len(self.instances),
            "solutions": []
        }
        
        for i, solution in enumerate(self.greedy_solutions):
            protocol_data["solutions"].append({
                "algorithm": "Greedy",
                "instance": i + 1,
                "num_boxes": len(solution.boxes),
                "time": self.times_greedy[i]
            })
        
        for i, solution in enumerate(self.local_search_solutions):
            protocol_data["solutions"].append({
                "algorithm": "Local Search",
                "instance": i + 1,
                "num_boxes": len(solution.boxes),
                "time": self.times_local_search[i]
            })
        
        file_name = f"protocols/protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_name, "w") as f:
            json.dump(protocol_data, f, indent=4)
        
        print(f"Protokoll gespeichert unter: {file_name}")


if __name__ == "__main__":
    test_env = Test_Environment()
    
    #instanzen, rechtecke, min_breite, min_hoehe, max_breite, max_hoehe, box_laenge = None, None, None, None, None, None, None 
    instanzen, rechtecke, min_breite, min_hoehe, max_breite, max_hoehe, box_laenge = 10, 150, 10, 15, 18, 23, 100 
    
    chosen_strategy = 1
    chosen_neighborhood = 1
    max_iterations = 21
    
    if instanzen is None and rechtecke is None and min_breite is None and min_hoehe is None and max_hoehe is None and max_breite is None and box_laenge is None:
        eingabe = input("Geben Sie die Parameter ein (Anzahl Instanzen, Anzahl Rechtecke, min. Breite, min. Höhe, max. Breite, max. Höhe, Boxlänge) durch Kommas getrennt: ")
        instanzen, rechtecke, min_breite, min_hoehe, max_breite, max_hoehe, box_laenge = map(int, eingabe.split(","))
    
    test_env.box_length = box_laenge
    
    test_env.generate_instances(instanzen, rechtecke, min_breite, min_hoehe, max_breite, max_hoehe)
    
    greedy_strategies = {1: "Größte Fläche zuerst", 2: "Kleinste Fläche zuerst", 3: "Größtes Seitenverhältnis zuerst", 4: "Kleinstes Seitenverhältnis zuerst"}
    
    if chosen_strategy is None:
        chosen_strategy = int(input("Wähle eine Greedy Strategie für die Rechteck Wahl (1: Größte Fläche zuerst, 2: Kleinste Fläche zuerst, 3: Größtes Seitenverhältnis zuerst, 4: Kleinstes Seitenverhältnis zuerst): "))
        if(int(chosen_strategy) > 4):
            chosen_strategy = 1
            print("Die Eingabe war fehlerhaft. Es wird die größte Fläche zuerst gewählt")
    
    test_env.greedy_strategy = greedy_strategies[chosen_strategy]
    
    if chosen_neighborhood is None:
        chosen_neighborhood = int(input("Wähle eine Nachbarschaft für die lokale Suche aus, indem Sie eine Zahl zwischen 1 und 3 eingeben (1: Geometrie basiert, 2: Regel basiert, 3: Überlappen erlauben): "))
        if(int(chosen_neighborhood) > 3):
            chosen_neighborhood = 1
            print("Die Eingabe war fehlerhaft. Es wird die Geometrie basierte Strategy genutzt")
            
    test_env.neighborhood = chosen_neighborhood
    
    if max_iterations is None:
        max_iterations = int(input("Geben Sie die maximale Anzahl an Iterationen für die lokale Suche ein (Standard ist 21): "))
        if(int(max_iterations)<=0):
            max_iterations = 21
            print("Die Eingabe war fehlerhaft. Es wird 21 als maximale Iterationsanzahl gesetzt")
            
    test_env.max_iterations = max_iterations
    
    test_env.run()
    
    
    
    
        
    
        
    
        
    
    