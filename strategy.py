           
            
def apply_strategy(items, strategy_name):
    if strategy_name == "Größte Fläche zuerst":
        items = sorted(items, key=lambda i: i.width * i.height, reverse=True)
    elif strategy_name == "Kleinste Fläche zuerst":
        items = sorted(items, key=lambda i: i.width * i.height)
    elif strategy_name == "Größtes Seitenverhältnis zuerst":
        items = sorted(items, key=lambda i: max(i.width / i.height, i.height / i.width), reverse=True)
    elif strategy_name == "Kleinstes Seitenverhältnis zuerst":
        items = sorted(items, key=lambda i: max(i.width / i.height, i.height / i.width))
        
    return items