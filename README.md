# 🧠 Optimization Framework (Beta)

## 🚀 Overview

Welcome to the **Optimization Framework** — a modular, extendable, and performance-focused system for solving complex combinatorial optimization problems using intelligent algorithmic strategies.

At its core, this project was more than just a course assignment — it was a chance to build a **general-purpose optimization engine** that combines powerful techniques with real-world visualization and testing capabilities. Whether you’re exploring classic Greedy logic or experimenting with Simulated Annealing, this framework lays the groundwork for scalable and reusable algorithmic exploration.

Currently, the framework supports the **Rectangle Packing Problem**, complete with:
- 🔁 Multiple optimization strategies (Greedy, Local Search, Backtracking, Simulated Annealing)
- 🎨 A user interface for configuration and visualization
- 🧪 A test environment for performance evaluations

And it's designed to grow — just implement a new problem’s logic and plug into the existing algorithm architecture in `base_classes/algorithms.py`.

---

## 📘 Project Background

This project was developed as part of the **"Optimization Algorithms"** course taught by Prof. Dr. Karsten Weihe at **TU Darmstadt**.

The full problem description is available in the included [`OptAlg.pdf`](./OptAlg.pdf).

---

## 🎯 Objective

The primary challenge: **implement generalized optimization algorithms** and use them to solve a rectangle packing problem under multiple constraints — both computational and visual.

### The highlights:
- Implement **Greedy** and **Local Search** with **three distinct neighborhoods**
- Ensure algorithm implementations remain **problem-agnostic**
- Enable visual interaction and flexible testing for different configurations

---

## 🧩 Optimization Strategies

The framework includes four implemented strategies:

### ⚙️ Greedy Algorithm
- Selects rectangles using one of four rules (e.g., largest area first, smallest aspect ratio first)
- Places rectangles accordingly, without revisiting prior placements
- Fast and simple, ideal for generating quick base solutions

### 🔍 Local Search (with 3 neighborhoods)
- **Geometry-based**: Rectangles are physically moved across boxes or inside their current box
- **Rule-based**: Treats solutions as permutations and tweaks rectangle orderings
- **Overlap-tolerant**: Allows overlaps initially and progressively removes them to improve layout

Each neighborhood brings its own strengths and allows deeper exploration of the solution space.

### 🔄 Simulated Annealing
- Probabilistically accepts worse solutions to escape local optima
- Cools down gradually using customizable parameters
- Uses geometry-based neighborhood for generating candidate states

### 🔙 Backtracking
- Classic recursive placement with backtracking when no valid configuration is found
- Best suited for smaller instances or educational comparison

---

## 📊 Evaluation Function

A flexible evaluation function assesses:
1. Number of used boxes
2. Space utilization
3. Unused space
4. Overlapping areas

The goal? **Minimize** the score:

$$\text{Score} = \left( w_1 \times \text{numBoxes}\right) + \left(w_2 \times \left(1-\text{utilization}\right)\right) + \left( w_3 \times \text{unusedSpace} \right) + \left( w_4 \times \text{totalOverlapArea} \right) $$


## ⚡ Performance Boosts

Python isn’t always fast — but we took care to squeeze performance where it counts:

- **NumPy** for vectorized computations and overlap detection
- **Numba (njit)** to compile bottleneck functions to native machine code
  - Used especially in `find_valid_placement()` with occupancy grids and integral images
- **Custom deep copy** utilities (faster than `copy.deepcopy`)
- **Integral image** optimizations for O(1) spatial queries

Result: up to **1000 rectangles packed in under 10 seconds** — and often, the solutions are visually near-optimal.

---

## 🖥️ User Interface (Tkinter)

We built a basic but functional UI for:
- Generating rectangle datasets
- Selecting algorithms and neighborhood types
- Comparing runs and replays
- Visualizing packing layouts

Usability matters — even if it's tkinter. Contrast, clarity, and ease of experimentation were key goals.

---

## 🔬 Test Environment

The test environment runs batch simulations to evaluate algorithm robustness.

Features:
- Fully parameterized: number of rectangles, instance size, box dimensions
- Two modes: quick test (few small instances) and heavy test (large, challenging inputs)
- Generates runtime protocols and output summaries

---

## 🧠 Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the main GUI
python main.py

# 3. Run the test suite
python test_env.py

# 4. Review solution outputs
python solution_viewer.py