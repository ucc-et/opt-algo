import tkinter as tk
from helpers import generate_instances
from searches import greedy_algorithm, local_search
from view import GUI

def main():
    root = tk.Tk()
    app = GUI(root, generate_instances, greedy_algorithm, local_search)
    root.mainloop()

if __name__ == "__main__":
    main()
