import json
from collections import defaultdict

def analyze_algorithm_performance(file_path):
    """
    Analyzes the performance of algorithms from a given JSON protocol file.
    
    Args:
        file_path (str): Path to the JSON file containing the protocol data.
    
    Returns:
        None: Prints the total and average run time for each algorithm.
    """
    try:
        # Load the JSON data
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Check if the necessary keys are present
        if "algorithms" not in data:
            print("Invalid file structure: 'algorithms' key not found.")
            return
        
        # Collecting total time and count for each algorithm
        algorithm_stats = defaultdict(lambda: {"total_time": 0.0, "count": 0})

        for entry in data["algorithms"]:
            algo_name = entry.get("algorithm", "Unknown")
            run_time = entry.get("time", 0.0)
            
            # Summing up time and incrementing count for average calculation
            algorithm_stats[algo_name]["total_time"] += run_time
            algorithm_stats[algo_name]["count"] += 1

        total_test_run_time = 0

        # Output total and average run time for each algorithm
        print("\nAlgorithm Performance Analysis:")
        print("="*40)
        for algo, stats in algorithm_stats.items():
            total_time = stats["total_time"]
            total_test_run_time += total_time
            count = stats["count"]
            average_time = total_time / count if count > 0 else 0.0
            
            print(f"Algorithm: {algo}")
            print(f"  Total Run Time: {total_time:.4f} seconds")
            print(f"  Average Run Time: {average_time:.4f} seconds\n")
        print(f"Total run time of Test Environment: {total_test_run_time: .2f} Seconds | {total_test_run_time/60: .2f} Minutes")

    except FileNotFoundError:
        print("File not found. Please check the file path.")
    except json.JSONDecodeError:
        print("Invalid JSON format. Please check the file content.")

# Usage
file_path = "protocols/protocol_C.json"  # Update with your file path
analyze_algorithm_performance(file_path)
