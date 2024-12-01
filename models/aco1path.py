import random
import math
from graphstructure import *
from tqdm import tqdm

class Graph:
    def __init__(self):
        self.edges = {}
    
    def add_edge(self, from_node, to_node, distance):
        if from_node not in self.edges:
            self.edges[from_node] = {}
        self.edges[from_node][to_node] = {'distance': distance, 'pheromone': 1.0}  # Initial pheromone level set to 1.0

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
    def __init__(self, graph, alpha=1, beta=2, evaporation_rate=0.1):
        self.graph = graph
        self.alpha = alpha  # Influence of pheromone
        self.beta = beta    # Influence of distance
        self.evaporation_rate = evaporation_rate

    def choose_next_node(self, current_node, visited_nodes):
        neighbors = self.graph.edges[current_node]
        probabilities = []
        for node, data in neighbors.items():
            if node not in visited_nodes: # Avoid revisiting nodes
                pheromone = (data['pheromone']) ** self.alpha
                distance = (1.0 / data['distance']) ** self.beta
                probabilities.append((node, pheromone * distance))

        if not probabilities:  # No unvisited nodes in the neighbourhood : we decide among the visited nodesaccording to the proba
            for node, data in neighbors.items():
                pheromone = (data['pheromone']) ** self.alpha
                distance = (1.0 / data['distance']) ** self.beta
                probabilities.append((node, pheromone * distance))

        total = sum(prob[1] for prob in probabilities)
        probabilities = [(node, prob / total) for node, prob in probabilities]
        next_node = random.choices(
            [prob[0] for prob in probabilities], 
            weights=[prob[1] for prob in probabilities]
        )[0]
        return next_node

    def simulate_ant(self, start_node):
        path = [start_node]
        visited_nodes = set(path)
        current_node = start_node

        while current_node != start_node or len(visited_nodes) != len(self.graph.get_nodes()):
            next_node = self.choose_next_node(current_node, visited_nodes)
            if next_node is None:  # No valid moves
                return None  # Invalid path
            path.append(next_node)
            if not next_node in visited_nodes:
                visited_nodes.add(next_node)
            current_node = next_node

        return path

    def update_pheromones(self, paths):
        # Reduce pheromones on all edges
        for from_node, neighbors in self.graph.edges.items():
            for to_node, data in neighbors.items():
                data['pheromone'] *= (1 - self.evaporation_rate)

        # Add pheromones based on paths
        for path in paths:
            path_length = sum(self.graph.edges[path[i]][path[i+1]]['distance'] for i in range(len(path) - 1))
            pheromone_deposit = 1.0 / path_length
            for i in range(len(path) - 1):
                self.graph.edges[path[i]][path[i+1]]['pheromone'] += pheromone_deposit
                self.graph.edges[path[i+1]][path[i]]['pheromone'] += pheromone_deposit

def optimize_path(graph, num_iterations=10, num_ants=50):
    aco = AntColonyOptimizer(graph, alpha=1, beta=2, evaporation_rate=0.1)
    
    best_path = None
    best_path_length = float('inf')  # Initialiser avec un très grand nombre

    for _ in tqdm(range(num_iterations), desc="Optimizing"):
        valid_paths = []

        # Simuler le déplacement des fourmis
        for _ in range(num_ants):
            #start_node = random.choice(list(graph.get_nodes()))
            start_node = 0
            path = aco.simulate_ant(start_node)

            # Vérifier si le chemin est valide
            if path and len(set(path[:-1])) == len(graph.get_nodes()) and path[0] == path[-1]:
                valid_paths.append(path)

        # Mettre à jour les phéromones uniquement pour les chemins valides
        if valid_paths:
            aco.update_pheromones(valid_paths)

            # Trouver le meilleur chemin dans cette itération
            for path in valid_paths:
                path_length = sum(graph.edges[path[i]][path[i+1]]['distance'] for i in range(len(path) - 1))
                if path_length < best_path_length:
                    best_path = path
                    best_path_length = path_length

    return best_path, best_path_length

# Lancement de l'optimisation
result, result_length = optimize_path(graph, num_iterations=30, num_ants=50)

if result:
    print("Best path found:", result)
    print("Path length:", result_length)
else:
    print("No valid path was found after all iterations.")
