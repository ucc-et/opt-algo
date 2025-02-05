import time
from helpers import generate_instances
from neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy


class Test_Environment:
    def __init__(self):
        self.instances = []
        self.box_length = -1
        self.greedy_strategy = None
        self.neighborhood = None
    
    def __repr__(self):
        return f"Test_Environment(box_length={self.box_length}, greedy_strategy={self.greedy_strategy}, neighborhood={self.neighborhood})"
    
    def run_greedy(self):
        pass
    
    def run_local_search(self, instance_index):
        pass
    
    def generate_multiple_instances(self, instance_count, rectangle_count, min_breite, min_hoehe, max_breite, max_hoehe):        
        for _ in range(instance_count):
            self.instances.append(generate_instances(rectangle_count, min_breite, max_breite, min_hoehe, max_hoehe))
        
    def run(self):
        pass
    



if __name__ == "__main__":
    test_env = Test_Environment()
    
    # Frage Daten zur Instanzgenerierung ab
    instanzen, rechtecke, min_breite, min_hoehe, max_breite, max_hoehe, box_laenge = None, None, None, None, None, None, None 
    if instanzen is None and rechtecke is None and min_breite is None and min_hoehe is None and max_hoehe is None and max_breite is None and box_laenge is None:
        eingabe = input("Geben Sie die Parameter ein (Anzahl Instanzen, Anzahl Rechtecke, min. Breite, min. Höhe, max. Breite, max. Höhe, Boxlänge) durch Kommas getrennt: ")
        instanzen, rechtecke, min_breite, min_hoehe, max_breite, max_hoehe, box_laenge = map(int, eingabe.split(","))
    
    test_env.box_length = box_laenge
    
    # Generiere Instanzen
    test_env.generate_multiple_instances(instanzen, rechtecke, min_breite, min_hoehe, max_breite, max_hoehe)
    
    # Wähle Greedy Strategie aus
    greedy_strategies = {1: "Größte Fläche zuerst", 2: "Kleinste Fläche zuerst", 3: "Größtes Seitenverhältnis zuerst", 4: "Kleinstes Seitenverhältnis zuerst"}
    
    chosen_strategy = int(input("Wähle eine Greedy Strategie für die Rechteck Wahl (1: Größte Fläche zuerst, 2: Kleinste Fläche zuerst, 3: Größtes Seitenverhältnis zuerst, 4: Kleinstes Seitenverhältnis zuerst): "))
    if(int(chosen_strategy) > 4):
        chosen_strategy = 1
        print("Die Eingabe war fehlerhaft. Es wird die größte Fläche zuerst gewählt")
    
    test_env.greedy_strategy = greedy_strategies[chosen_strategy]
    
    # Wähle Nachbarschaft für lokale Suche aus
    local_search_neighborhoods = {1: GeometryBasedStrategy(), 2: RuleBasedStrategy(), 3: OverlapStrategy()}
    
    chosen_neighborhood = int(input("Wähle eine Nachbarschaft für die lokale Suche aus, indem Sie eine Zahl zwischen 1 und 3 eingeben (1: Geometrie basiert, 2: Regel basiert, 3: Überlappen erlauben): "))
    if(int(chosen_neighborhood) > 3):
        chosen_neighborhood = 1
        print("Die Eingabe war fehlerhaft. Es wird die Geometrie basierte Strategy genutzt")
        
    test_env.neighborhood = local_search_neighborhoods[chosen_neighborhood]
    
    test_env.run()
    
    
        
    
        
    
        
    
    