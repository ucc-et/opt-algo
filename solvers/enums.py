from enum import Enum

class GreedyStrategy(Enum):
    LARGEST_AREA_FIRST = "Größte Fläche zuerst"
    SMALLEST_AREA_FIRST = "Kleinste Fläche zuerst"
    LARGEST_ASPECT_RATIO_FIRST = "Größtes Seitenverhältnis zuerst"
    SMALLEST_ASPECT_RATIO = "Kleinstes Seitenverhältnis zuerst"
    
class Rules(Enum):
    HEIGHT_FIRST = "Absteigend nach Höhe"
    WIDTH_FIRST = "Absteigend nach Breite"
    AREA_FIRST = "Absteigend nach Fläche"
    
class Neighborhoods(Enum):
    GEOMETRY = "Geometriebasiert"
    RULE = "Regelbasiert"
    OVERLAP = "Überlappung teilweise zulassen"