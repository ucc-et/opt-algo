           
            
def apply_strategy(instances, strategy_name):
    if strategy_name == "Größte Fläche zuerst":
        instances = sorted(instances, key=lambda r: r.width * r.height, reverse=True)
    elif strategy_name == "Kleinste Fläche zuerst":
        instances = sorted(instances, key=lambda r: r.width * r.height)
    elif strategy_name == "Größtes Seitenverhältnis zuerst":
        instances = sorted(instances, key=lambda r: max(r.width / r.height, r.height / r.width), reverse=True)
    elif strategy_name == "Kleinstes Seitenverhältnis zuerst":
        instances = sorted(instances, key=lambda r: max(r.width / r.height, r.height / r.width))
        
    return instances