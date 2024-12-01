import random
import math
from graphstructure import *
from tqdm import tqdm

# Liste qui contient les noeuds visi
visited_nodes = []

class Graph:
    def __init__(self):
        self.edges = {}
    
    def add_edge(self, from_node, to_node, distance):
        if from_node not in self.edges:
            self.edges[from_node] = {}
        self.edges[from_node][to_node] = {'distance': distance, 'pheromone': 1.0}  # initial pheromone level set to 1.0

    def get_nodes(self):
        return list(self.edges.keys())

def create_graph():
    graph = Graph()
    distances = {frozenset([a, b]): math.hypot(nodes_position[a][0] - nodes_position[b][0], nodes_position[a][1] - nodes_position[b][1]) for a, b in edges}
    for (i, j), d in distances.items():
        graph.add_edge(i, j, d)
        graph.add_edge(j, i, d)
    return graph

graph = create_graph()

class AntColonyOptimizer:
    def __init__(self, graph, alpha=1, beta=0.2, evaporation_rate=0.001, num_groups=3):
        self.graph = graph
        self.alpha = alpha  # influence of pheromone
        self.beta = beta    # influence of distance
        self.evaporation_rate = evaporation_rate
        self.num_groups = num_groups
        self.visited_nodes = set()  # Global list of visited nodes
    
    def choose_next_node(self, current_node, visited):
        neighbors = self.graph.edges[current_node]
        probabilities = []
        for node, data in neighbors.items():
            if node not in visited:  # Avoid revisiting nodes
                pheromone = (data['pheromone']) ** self.alpha
                heuristic = (1.0 / data['distance']) ** self.beta
                probabilities.append((node, pheromone * heuristic))

        if not probabilities: # No unvisited nodes in the neighbourhood : we decide among the visited nodesaccording to the proba
            for node, data in neighbors.items():
                pheromone = (data['pheromone']) ** self.alpha
                heuristic = (1.0 / data['distance']) ** self.beta
                probabilities.append((node, pheromone * heuristic))

        total = sum(prob[1] for prob in probabilities)
        probabilities = [(node, prob / total) for node, prob in probabilities]
        next_node = random.choices([prob[0] for prob in probabilities], weights=[prob[1] for prob in probabilities])[0]
        return next_node


    def simulate_ants(self, start_node, num_agents):
        path = [start_node]
        visited = set(path)

        paths = [[] for _ in range(num_agents)]
        current_nodes = [start_node for _ in range(num_agents)]

        while any(x != start_node for x in current_nodes) or len(visited) != len(self.graph.get_nodes()): # Continue until all nodes are by the ants
            for i in range(num_agents):
                if current_nodes[i] == start_node and len(visited) == len(self.graph.get_nodes()): # If all the nodes have been visited, when an agent reaches the start node he just waits that the other agents come back as well
                    continue
                next_node = self.choose_next_node(current_nodes[i], visited)
                if next_node is None:
                    break
                paths[i].append(next_node)
                if not next_node in visited:
                    visited.add(next_node)
                    self.visited_nodes.add(next_node)  # Update global visited nodes
                current_nodes[i] = next_node
        return paths

    def calculate_cost(self, all_paths):
        covered_nodes = set()
        distance_paths = []
        for paths in all_paths:
            distance = 0
            for path in paths:
                covered_nodes.update(path)
                distance += sum(graph.edges[path[i]][path[i+1]]['distance'] for i in range(len(path) - 1))
            distance_paths.append(distance)

        index_min = distance_paths.index(min(distance_paths))
        return index_min, min(distance_paths)

    def update_pheromones(self, all_paths):
        # Global pheromone update
        for from_node, neighbors in self.graph.edges.items():
            for to_node, data in neighbors.items():
                data['pheromone'] *= (1 - self.evaporation_rate)

        # Add pheromones based on paths
        for paths in all_paths:
            for path in paths:
                path_length = sum(self.graph.edges[path[i]][path[i+1]]['distance'] for i in range(len(path) - 1))
                pheromone_deposit = 1.0 / path_length
                for i in range(len(path) - 1):
                    self.graph.edges[path[i]][path[i+1]]['pheromone'] += pheromone_deposit
                    self.graph.edges[path[i+1]][path[i]]['pheromone'] += pheromone_deposit

def optimize_paths(graph, num_groups=3, num_ants = 50, max_iterations=100):
    aco = AntColonyOptimizer(graph, num_groups=num_groups)

    stable_iterations = 0
    stable_threshold = 50

    previous_cost = float('inf')

    for _ in tqdm(range(max_iterations), desc="Optimization"):
        all_paths = []
        aco.visited_nodes = set()  # Reset global visited nodes for this iteration

        for _ in range(num_ants):
            #start_node = random.choice(list(graph.get_nodes()))
            start_node = 0
            paths = aco.simulate_ants(start_node, num_groups)
            all_paths.append(paths)
        
        aco.update_pheromones(all_paths)
        index_best_way, current_cost = aco.calculate_cost(all_paths)

        # Check for stability
        if current_cost == previous_cost:
            stable_iterations += 1
        else:
            stable_iterations = 0
        previous_cost = current_cost

        if stable_iterations >= stable_threshold:
            print("Convergence atteinte après", _, "itérations.")
            break

    return all_paths[index_best_way]

# Exemple d'utilisation
final_paths = optimize_paths(graph)
for idx, path in enumerate(final_paths):
    print(f"Agent {idx + 1}: {path}")
