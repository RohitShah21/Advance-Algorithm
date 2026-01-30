import collections
import heapq

# 1. State Space from Diagram (a) [cite: 757-795]
graph = {
    'Glogow': {'Leszno': 45, 'Wroclaw': 140},
    'Leszno': {'Glogow': 45, 'Poznan': 90, 'Kalisz': 140, 'Wroclaw': 100},
    'Poznan': {'Leszno': 90, 'Bydgoszcz': 140, 'Konin': 120, 'Kalisz': 130},
    'Wroclaw': {'Glogow': 140, 'Leszno': 100, 'Kalisz': 160, 'Czestochowa': 118, 'Opole': 100},
    'Opole': {'Wroclaw': 100, 'Katowice': 85},
    'Czestochowa': {'Wroclaw': 118, 'Lodz': 128, 'Katowice': 80},
    'Katowice': {'Opole': 85, 'Czestochowa': 80, 'Krakow': 85},
    'Krakow': {'Katowice': 85, 'Kielce': 120, 'Radom': 280},
    'Kielce': {'Krakow': 120, 'Radom': 82},
    'Radom': {'Krakow': 280, 'Kielce': 82, 'Warsaw': 105, 'Lodz': 165},
    'Lodz': {'Kalisz': 160, 'Konin': 120, 'Warsaw': 150, 'Radom': 165, 'Czestochowa': 128},
    'Warsaw': {'Plock': 130, 'Lodz': 150, 'Radom': 105},
    'Plock': {'Wloclawek': 55, 'Warsaw': 130},
    'Wloclawek': {'Bydgoszcz': 110, 'Plock': 55, 'Konin': 120},
    'Bydgoszcz': {'Poznan': 140, 'Wloclawek': 110},
    'Konin': {'Poznan': 120, 'Wloclawek': 120, 'Lodz': 120, 'Kalisz': 120},
    'Kalisz': {'Leszno': 140, 'Poznan': 130, 'Konin': 120, 'Lodz': 160, 'Wroclaw': 160}
}

# 2. Heuristics from Diagram (b) [cite: 718-756]
heuristic = {
    'Glogow': 40, 'Leszno': 103, 'Poznan': 108, 'Wroclaw': 87, 'Opole': 90,
    'Czestochowa': 80, 'Katowice': 68, 'Krakow': 102, 'Kielce': 61, 'Radom': 91,
    'Lodz': 124, 'Warsaw': 95, 'Plock': 0, 'Wloclawek': 44, 'Bydgoszcz': 90,
    'Konin': 96, 'Kalisz': 107
}

def bfs(start, goal):
    queue = collections.deque([[start]])
    visited = set([start])
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

def dfs(start, goal):
    stack = [[start]]
    visited = set()
    while stack:
        path = stack.pop()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                stack.append(new_path)

def a_star(start, goal):
    # Priority Queue: (f_cost, g_cost, current_node, path)
    pq = [(heuristic[start], 0, start, [start])]
    visited = set()
    
    while pq:
        f, g, node, path = heapq.heappop(pq)
        
        if node == goal:
            return path
            
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor, weight in graph.get(node, {}).items():
            if neighbor not in visited:
                new_g = g + weight
                new_f = new_g + heuristic.get(neighbor, 1000)
                new_path = list(path)
                new_path.append(neighbor)
                heapq.heappush(pq, (new_f, new_g, neighbor, new_path))

def solve_task6():
    start = 'Glogow'
    goal = 'Plock'
    
    print(f"Pathfinding from {start} to {goal} [cite: 717]")
    print(f"BFS Path: {bfs(start, goal)}")
    print(f"DFS Path: {dfs(start, goal)}")
    print(f"A* Path: {a_star(start, goal)}")

if __name__ == "__main__":
    solve_task6()