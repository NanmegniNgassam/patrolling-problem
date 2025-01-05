from tqdm import tqdm
import numpy as np
import networkx as nx
from algos.genetic import aco_parameters_with_genetic


# ALGORITHME ACO
def initialize_pheromones(num_cities, tau_0=1.0):
    """Initialise la matrice de phéromones."""
    return np.full((num_cities, num_cities), tau_0)

def calculate_visibility(distance_matrix):
    """Calcule la matrice de visibilité (1 / distance)."""
    with np.errstate(divide='ignore'):
        visibility = 1 / distance_matrix
        visibility[distance_matrix == 0] = 0
    return visibility

def select_next_city(current_city, allowed_cities, pheromones, visibility, alpha, beta, graph):
    """Sélectionne la prochaine ville en fonction des probabilités."""
    probs = []
    allowed_cities_accessible = []
    for city in allowed_cities:
        if graph.has_edge(current_city, city):
            prob = (pheromones[current_city, city] ** alpha) * (visibility[current_city, city] ** beta)
            probs.append(prob)
            allowed_cities_accessible.append(city)
    if len(probs)==0:
        for city in allowed_cities:
            prob = (pheromones[current_city, city] ** alpha) * (visibility[current_city, city] ** beta)
            probs.append(prob)
            allowed_cities_accessible.append(city)

    probs = np.array(probs) / sum(probs)  # Normalisation
    return np.random.choice(allowed_cities_accessible, p=probs)

def construct_solution(num_cities, distance_matrix, pheromones, visibility, alpha, beta, start_node, graph,num_agents):
    """Construit un chemin pour une fourmi en partant du nœud spécifié."""
    solution = [[start_node] for _ in range(num_agents)]
    allowed_cities = [c for c in range(num_cities)]
    #for _ in range(num_cities - 1):
    while len(allowed_cities)>1:
        for agent in range(num_agents):
            if len(allowed_cities) >1:
                current_city = solution[agent][-1]

                nodes_visites = list(set(element for sous_liste in solution for element in sous_liste))
                allowed_cities = [c for c in range(num_cities) if c not in nodes_visites]

                next_city = select_next_city(current_city, allowed_cities, pheromones, visibility, alpha, beta, graph)
                solution[agent].append(next_city)
    for chemin_individuel in solution:
        chemin_individuel.append(start_node) # Retour au nœud de départ
    return solution 

def update_pheromones(pheromones, solutions, distances, rho, Q,num_agents):
    """Met à jour la matrice de phéromones."""
    pheromones *= (1 - rho)  # Évaporation
    for solution in solutions:

        path_length = sum(distances[solution[j][i], solution[j][i + 1]]
                  for j in range(num_agents)  # Pour chaque agent
                  for i in range(len(solution[j]) - 1))  # Pour chaque étape du chemin de l'agent, jusqu'à l'avant-dernière
        
        for j in range(len(solution) - 1):
            for i in range(len(solution[j]) - 1):
                pheromones[solution[j][i], solution[j][i + 1]] += Q / path_length
    return pheromones

def aco_tsp(distance_matrix, start_node, graph, num_agents, num_ants=100, num_iterations=100, alpha=1.0, beta=2.0, rho=0.5, Q=100):
    """Algorithme principal ACO pour le TSP."""
    num_cities = distance_matrix.shape[0]
    pheromones = initialize_pheromones(num_cities)
    visibility = calculate_visibility(distance_matrix)
    best_solution = None
    best_length = float('inf')

    for _ in tqdm(range(num_iterations), desc="Optimizing"):
        solutions = []
        for _ in range(num_ants):
            solution = construct_solution(num_cities, distance_matrix, pheromones, visibility, alpha, beta, start_node, graph,num_agents)
            solutions.append(solution)

        for solution in solutions:
            
            path_length = sum(distance_matrix[solution[j][i], solution[j][i + 1]]
                  for j in range(num_agents)  # Pour chaque agent
                  for i in range(len(solution[j]) - 1))  # Pour chaque étape du chemin de l'agent, jusqu'à l'avant-dernière
            
            if path_length < best_length:
                best_solution, best_length = solution, path_length

        pheromones = update_pheromones(pheromones, solutions, distance_matrix, rho, Q,num_agents)

    return best_solution, best_length


start_node = 0

# CORRECTION CHEMIN
def validate_path(graph, path):
    for i in range(len(path) - 1):
        if not graph.has_edge(path[i], path[i + 1]):
            return False
    return True


def correct_path(graph, path):
    corrected_path = []
    for i in range(len(path) - 1):
        if graph.has_edge(path[i], path[i + 1]):
            corrected_path.append(path[i])
        else:
            # Trouver le chemin le plus court entre path[i] et path[i + 1]
            shortest_subpath = nx.shortest_path(graph, source=path[i], target=path[i + 1])
            corrected_path.extend(shortest_subpath[:-1])  # Ajouter le chemin sans dupliquer le nœud cible
    corrected_path.append(path[-1])  # Ajouter le dernier nœud
    return corrected_path

# Renvoie les chemin de l'algo génétique
def generate_path_with_genetic(nodes_position, edges, num_agents):
    all_path = []
    nodes, graph, distance_matrix = aco_parameters_with_genetic(nodes_position, edges, num_agents)
    for node in nodes :
        path, best_lenth=aco_tsp(distance_matrix, node, graph, 1)
        path = path[0]
        is_valid = validate_path(graph, path)
        if not is_valid:
            path = correct_path(graph, path)
        all_path.append(path)
        print(f"path: {path}")
    return all_path

# Fonction : Calculer les poids des arêtes
def calculate_edge_weights(nodes_position, edges):
    weighted_edges = []
    for u, v in edges:
        x_u, y_u = nodes_position[u]
        x_v, y_v = nodes_position[v]
        weight = np.sqrt((x_u - x_v) ** 2 + (y_u - y_v) ** 2)
        weighted_edges.append((u, v, weight))
    return weighted_edges


# Construire un graphe pondéré
def build_weighted_graph(nodes_position, edges):
    weighted_edges = calculate_edge_weights(nodes_position, edges)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(nodes_position)))
    for u, v, weight in weighted_edges:
        graph.add_edge(u, v, weight=weight)
    return graph

# Fonction : Créer la matrice des distances pondérées
def compute_weighted_distance_matrix(graph):
    n = len(graph.nodes)
    distance_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                distance_matrix[i, j] = 0
            else:
                try:
                    distance_matrix[i, j] = nx.shortest_path_length(graph, source=i, target=j, weight="weight")
                except nx.NetworkXNoPath:
                    distance_matrix[i, j] = np.inf
    return distance_matrix

# Renvoie le chemin de l'ACO commencant au noeud 0
def generate_path(num_agents,nodes_position, edges):
    graph = build_weighted_graph(nodes_position, edges)
    distance_matrix = compute_weighted_distance_matrix(graph)
    
    path, best_lenth=aco_tsp(distance_matrix, 0, graph,num_agents)
    for i in range(len(path)):
        is_valid = validate_path(graph, path[i])
        if not is_valid:
            path[i] = correct_path(graph, path[i])
    print(f"Chemin trouvé : {path}")

    return path


