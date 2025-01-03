import matplotlib.pyplot as plt
#from graphstructure import *
import networkx as nx
import numpy as np
import random

#num_agents = 3

# Paramètres de l'algorithme génétique
POPULATION_SIZE = 100  # Taille de la population
#N = len(nodes_position)  # Taille des individus
N = 0  # Taille des individus
#NB_AGENT = num_agents  # Nombre de cases avec valeur 1
GENERATIONS = 10  # Nombre de générations
MUTATION_RATE = 0.1  # Probabilité de mutation

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



# Génération aléatoire d'un individu
def generate_individual(nodes_position, num_agents):
    N = len(nodes_position)
    individual = [0] * N
    positions = random.sample(range(N), num_agents)
    for pos in positions:
        individual[pos] = 1
    return individual

# Initialisation de la population
def initialize_population(nodes_position, num_agents):
    return [generate_individual(nodes_position, num_agents) for _ in range(POPULATION_SIZE)]

# Fonction de fitness (somme des positions des agents)
def fitness(individual, distance_matrix, nodes_position):
    N = len(nodes_position)
    fitness = 0
    agents = []
    distances = []
    for i in range(N):
        if individual[i] == 1:
            agents.append(i)
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            distances.append(distance_matrix[agents[i]][agents[j]])
    fitness = min(distances)

    return fitness

# Selection par roulette
def selection(population, distance_matrix, nodes_position):
    fitness_values = [fitness(ind, distance_matrix, nodes_position) for ind in population]
    total_fitness = sum(fitness_values)
    pick = random.uniform(0, total_fitness)
    current = 0
    for ind, fit in zip(population, fitness_values):
        current += fit
        if current > pick:
            return ind

# Croisement entre deux parents
def crossover(parent1, parent2, nodes_position, num_agents):
    N = len(nodes_position)
    crossover_point = random.randint(1, N - 1)
    child = parent1[:crossover_point] + parent2[crossover_point:]

    # Assurer NB_AGENT agents après croisement
    while sum(child) > num_agents:
        child[random.choice([i for i, v in enumerate(child) if v == 1])] = 0
    while sum(child) < num_agents:
        child[random.choice([i for i, v in enumerate(child) if v == 0])] = 1

    return child

# Mutation d'un individu
def mutate(individual, nodes_position):
    N = len(nodes_position)
    if random.random() < MUTATION_RATE:
        idx1, idx2 = random.sample(range(N), 2)
        individual[idx1], individual[idx2] = individual[idx2], individual[idx1]

# Algorithme génétique principal
def genetic_algorithm(distance_matrix, nodes_position, num_agents):
    population = initialize_population(nodes_position, num_agents)

    for generation in range(GENERATIONS):
        new_population = []

        for _ in range(POPULATION_SIZE):
            parent1 = selection(population, distance_matrix, nodes_position)
            parent2 = selection(population, distance_matrix, nodes_position)
            child = crossover(parent1, parent2, nodes_position, num_agents)
            mutate(child, nodes_position)
            new_population.append(child)

        # Combiner parents et enfants, et sélectionner les meilleurs
        combined_population = population + new_population
        population = []
        for _ in range(POPULATION_SIZE):
            selected = selection(combined_population, distance_matrix, nodes_position)
            population.append(selected)
            combined_population.remove(selected)

        # Suivi de la meilleure solution de la génération
        best_individual = max(population, key=lambda individual: fitness(individual, distance_matrix, nodes_position))
        print(f"Génération {generation + 1}: Meilleure fitness = {fitness(best_individual, distance_matrix, nodes_position)}")

    return best_individual



# Exécution de l'algorithme
def aco_parameters_with_genetic(nodes_position, edges, num_agents):
    graph = build_weighted_graph(nodes_position, edges)
    distance_matrix = compute_weighted_distance_matrix(graph)
    best_solution = genetic_algorithm(distance_matrix, nodes_position, num_agents)
    print("Meilleure solution:", best_solution)
    print("Fitness de la meilleure solution:", fitness(best_solution, distance_matrix, nodes_position))
    
    nodes=[]
    for i in range(len(best_solution)):
        if best_solution[i] == 1:
            nodes.append(i)
            
    return nodes, graph, distance_matrix