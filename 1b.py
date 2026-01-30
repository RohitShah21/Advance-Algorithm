import math
import random

def euclidean_distance(city1, city2):
    return math.sqrt((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)

def total_tour_distance(tour, cities):
    dist = 0
    for i in range(len(tour)):
        from_city = cities[tour[i]]
        to_city = cities[tour[(i + 1) % len(tour)]]
        dist += euclidean_distance(from_city, to_city)
    return dist

def get_neighbor(tour):
    new_tour = tour[:]
    i, j = sorted(random.sample(range(len(tour)), 2))
    # Reverse the segment between i and j
    new_tour[i:j+1] = reversed(new_tour[i:j+1])
    return new_tour

def simulated_annealing(cities, initial_temp=1000, cooling_rate=0.995, max_iter=10000):
    current_tour = list(range(len(cities)))
    random.shuffle(current_tour)
    current_dist = total_tour_distance(current_tour, cities)
    
    best_tour = current_tour[:]
    best_dist = current_dist
    
    temp = initial_temp
    
    for i in range(max_iter):
        neighbor_tour = get_neighbor(current_tour)
        neighbor_dist = total_tour_distance(neighbor_tour, cities)
        
        delta = neighbor_dist - current_dist
        
        # Acceptance criteria: Always accept if better, else accept with probability
        if delta < 0 or random.random() < math.exp(-delta / temp):
            current_tour = neighbor_tour
            current_dist = neighbor_dist
            
            if current_dist < best_dist:
                best_dist = current_dist
                best_tour = current_tour[:]
        
        temp *= cooling_rate
        if temp < 1e-3:
            break
            
    return best_tour, best_dist

def solve_task1b():
    # Generate random cities as per requirement [cite: 500]
    num_cities = 20
    cities = [[random.uniform(0, 1000), random.uniform(0, 1000)] for _ in range(num_cities)]
    
    best_route, min_dist = simulated_annealing(cities)
    print(f"Final Best Distance for {num_cities} cities: {min_dist:.2f}")

if __name__ == "__main__":
    solve_task1b()