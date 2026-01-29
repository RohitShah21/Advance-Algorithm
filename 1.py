"""
Module: Task1a.py
Problem: Optimal Sensor Placement for Signal Strength
Description: Implementation of the Weiszfeld Algorithm to minimize the total 
Euclidean distance between a central hub and a network of sensors.
"""

import math

def calculate_distance(p1, p2):
    """
    Computes the Euclidean distance between two 2D coordinates.
    Formula: sqrt((x2 - x1)^2 + (y2 - y1)^2)
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def get_initial_centroid(sensors):
    """
    Calculates the arithmetic mean (centroid) to use as the starting 
    point for the iterative optimization.
    """
    total_x = sum(s[0] for s in sensors)
    total_y = sum(s[1] for s in sensors)
    n = len(sensors)
    return [total_x / n, total_y / n]

def weiszfeld_algorithm(sensors, max_iter=100, tolerance=1e-7):
    """
    Iteratively finds the geometric median of a set of points.
    This minimizes the function defined in the assignment brief.
    """
    # Start at the average position of all sensors
    hub = get_initial_centroid(sensors)
    
    for _ in range(max_iter):
        prev_hub = [hub[0], hub[1]]
        num_x, num_y, denominator = 0.0, 0.0, 0.0
        
        for s in sensors:
            dist = calculate_distance(hub, s)
            
            # Avoid division by zero if the hub is exactly on a sensor
            if dist == 0:
                continue
                
            weight = 1.0 / dist
            num_x += s[0] * weight
            num_y += s[1] * weight
            denominator += weight
            
        if denominator == 0:
            break
            
        # Update hub coordinates based on weighted averages
        hub[0] = num_x / denominator
        hub[1] = num_y / denominator
        
        # Check for convergence
        if calculate_distance(hub, prev_hub) < tolerance:
            break
            
    return hub

def solve_optimal_placement(sensor_locations):
    """
    Main execution function to solve the problem and return the 
    minimum total sum of distances[cite: 42].
    """
    if not sensor_locations:
        return 0.0
        
    if len(sensor_locations) == 1:
        return 0.0

    # Optimize the hub position
    optimal_hub = weiszfeld_algorithm(sensor_locations)
    
    # Calculate the total sum of Euclidean distances to the optimal hub
    total_sum = sum(calculate_distance(optimal_hub, s) for s in sensor_locations)
    
    # Return formatted output as per Example 1 [cite: 49]
    return round(total_sum, 5)

# --- Validation with Assignment Examples ---
if __name__ == "__main__":
    print("-" * 40)
    print("TASK 1a: SENSOR HUB OPTIMIZATION")
    print("-" * 40)

    # Example 1 [cite: 48, 49]
    case1 = [[0, 1], [1, 0], [1, 2], [2, 1]]
    result1 = solve_optimal_placement(case1)
    print(f"Example 1 Input: {case1}")
    print(f"Example 1 Output: {result1:.5f} (Expected: 4.00000)")

    # Example 2 [cite: 63, 62]
    case2 = [[1, 1], [3, 3]]
    result2 = solve_optimal_placement(case2)
    print(f"\nExample 2 Input: {case2}")
    print(f"Example 2 Output: {result2:.5f} (Expected: 2.82843)")
    print("-" * 40)