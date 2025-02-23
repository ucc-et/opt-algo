# Optimization Framework (beta)

## Overview

This project is an optimization framework designed to solve complex combinatorial optimization problems using generalized algorithms, including:

* Greedy Algorithm
* Local Search
* Simulated Annealing
* Backtracking

This framework currently only uses the rectangle packer problem. But other optimization problems could be added in the future, and should be able to run with the currently existing algorithms in base_classes/algorithms.py, if problem specific files are added and implemented correctly.
A graphical user interface for visualization and a test environment for strategies is provided for the rectangle packing problem. 

## Task Desciption

This project is the result of a assignment for the course 'Optimization Algorithms' taught by Prof. Dr. Karsten Weihe at the TU Darmstadt.\\
The Problem description is provided in the 'OptAlg.pdf'. 

## Summary
Implement Greedy and local search with three neighborhoods to solve and display the rectangle packer problem. 
Following constraints apply
* The implementation of the algorithms should be generalized, so that the implementation does not tell the reader, which optimization problem is being solved.
* In the implementation of the optimizationproblems there shall not be any algorithm or neighborhood specific methods or variables.
* following neighborhoods should be implemented for local-search
    * geometry based, in which a neighbor is creates by directly moving rectangles inside a box or from one box to another
    * rule based, in which the algorithm works with permutations of the rectangles. The neighborhood is defined by small modifications of the permutation of rectangles.
    * allow partial overlaps, in which a overlap-percentage is initialized at 100% and determines how much the rectangles are allowed to overlap. The percentage gradually decreases and the output shall be a overlap-free solution.
* implement two different picking strategies for greedy algorithm, so two orders where the rectangles will be taken and placed with.
* UI-Constraints
    * visualize the generated solutions
    * allow the user to enter in the UI how the rectangles should be generated
    * the UI allows to run algorithms on the same rectangles multiple times, also with different neighborhoods or rules.
    * do not overlap information
    * try to work with usability and good color contrasts
* Test-Environment Constraints
    * the test environment should be parametritized with amount of instances, amount of rectangles, 2 minimal widths and heights, box length. Then run the implemented algorithms on those instances without visualizing it.
    * Each generation shall create a protocol of the run with run times
    * the test environment should be runnable in two versions:
        * with enoughly little instance size and amounts so the test environment can run through in a couple minutes
        * with enoughly large instance sizes and amounts so the test environment can be a meaningful representator of the correctness of the algorithms.
* every algorithm should pack instances with up to 1000 rectangles in 10 seconds. The solutions should not be able to be improved with the naked eye

## Getting Started
1. Install dependencies
```shell
pip install -r requirements.txt
```

2. run the standard gui
```shell
python main.py
```

3. run the test environment
```shell
python test_env.py
```

4. run the solution viewer
```shell
python solution_viewer.py
```