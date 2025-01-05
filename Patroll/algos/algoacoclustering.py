import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
from algos.algoaco import correct_path, validate_path, aco_tsp
import time

start_node_aco = 0  # Exemple : définir le nœud de départ comme le nœud 0

# Fonction : Calculer les poids des arêtes
def calculate_edge_weights(nodes_position, edges):
    weighted_edges = []
    #print("nodes_position :", nodes_position)
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

# Fonction : Calculer les poids des arêtes
def calculate_edge_weights_sub(nodes_position, edges):
    weighted_edges = []
    for u, v in edges:
        x_u, y_u = nodes_position[u]
        x_v, y_v = nodes_position[v]
        weight = np.sqrt((x_u - x_v) ** 2 + (y_u - y_v) ** 2)
        weighted_edges.append((u, v, weight))
    return weighted_edges

# Construire un graphe pondéré
def build_weighted_subgraph(nodes_position, edges):
    weighted_edges = calculate_edge_weights_sub(nodes_position, edges)
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

# Fonction pour calculer le poids total des clusters
def compute_cluster_weights(graph, clusters, n_clusters):
    cluster_weights = [0] * n_clusters
    for u, v, weight in graph.edges(data="weight"):
        if clusters[u] == clusters[v]:  # Si les deux nœuds appartiennent au même cluster
            cluster_id = clusters[u]
            cluster_weights[cluster_id] += weight
    return cluster_weights

# Fonction : Exécuter K-Means jusqu'à respecter la contrainte de poids
def balanced_weighted_kmeans(distance_matrix, graph, n_clusters, tolerance=0.05, max_iterations=1000):
    best_clusters = None
    best_weights = None
    best_difference = float('inf')  # Initialise la meilleure différence

    for iteration in range(max_iterations):
        kmeans = KMeans(n_clusters=n_clusters, random_state=iteration)
        clusters = kmeans.fit_predict(distance_matrix)
        cluster_weights = compute_cluster_weights(graph, clusters, n_clusters)

        # Vérification de la connexité des clusters
        all_connected = True
        for cluster_id in range(n_clusters):
            cluster_nodes = [i for i, label in enumerate(clusters) if label == cluster_id]
            subgraph = graph.subgraph(cluster_nodes)
            if not nx.is_connected(subgraph):
                all_connected = False
                break  # Sortir si un cluster n'est pas connexe

        if not all_connected:
            continue  # Relancer K-Means avec une nouvelle initialisation

        # Calculer la différence relative entre le plus grand et le plus petit poids
        max_weight = max(cluster_weights)
        min_weight = min(cluster_weights)
        difference = (max_weight - min_weight) / max_weight

        # Mettre à jour la meilleure solution si elle est meilleure
        if difference < best_difference:
            best_difference = difference
            best_clusters = clusters
            best_weights = cluster_weights

        # Arrêter si la contrainte est respectée
        if difference <= tolerance:
            return clusters, cluster_weights

    return best_clusters, best_weights

# Fonction pour calculer les barycentres pondérés des clusters
def compute_cluster_barycenters(graph, clusters, nodes_position, n_clusters):
    barycenters = []
    for cluster_id in range(n_clusters):
        nodes_in_cluster = [i for i, label in enumerate(clusters) if label == cluster_id]
        weighted_sum_x = weighted_sum_y = total_weight = 0

        for u in nodes_in_cluster:
            for v in nodes_in_cluster:
                try:
                    weight = 1 / (nx.shortest_path_length(graph, source=u, target=v, weight="weight") + 1e-6)
                    weighted_sum_x += nodes_position[v][0] * weight
                    weighted_sum_y += nodes_position[v][1] * weight
                    total_weight += weight
                except nx.NetworkXNoPath:
                    continue

        if total_weight > 0:
            barycenters.append((weighted_sum_x / total_weight, weighted_sum_y / total_weight))
        else:
            barycenters.append(nodes_position[nodes_in_cluster[0]])
    return barycenters

# Fonction pour trouver le nœud le plus proche d'un barycentre
def find_nearest_nodes_to_barycenters(barycenters, clusters, nodes_position, n_clusters):
    nearest_nodes = []
    for cluster_id in range(n_clusters):
        nodes_in_cluster = [i for i, label in enumerate(clusters) if label == cluster_id]
        barycenter = barycenters[cluster_id]

        min_distance = float('inf')
        nearest_node = None
        for node in nodes_in_cluster:
            distance = np.sqrt((nodes_position[node][0] - barycenter[0]) ** 2 +
                               (nodes_position[node][1] - barycenter[1]) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_node = node
        nearest_nodes.append(nearest_node)
    return nearest_nodes

# Fonction d'affichage des clusters
def generate_clusters(graph, nodes_position, n_clusters, tolerance=0.05):
    distance_matrix = compute_weighted_distance_matrix(graph)
    clusters, cluster_weights = balanced_weighted_kmeans(distance_matrix, graph, n_clusters, tolerance)
    barycenters = compute_cluster_barycenters(graph, clusters, nodes_position, n_clusters)
    nearest_nodes = find_nearest_nodes_to_barycenters(barycenters, clusters, nodes_position, n_clusters)


    return clusters, cluster_weights, barycenters, nearest_nodes


# Fonction : Extrait les nœuds et arêtes d'un cluster
def extract_cluster_nodes_and_edges(graph, nodes_position, clusters, cluster_id):
    nodes_in_cluster = [nodes_position[i] for i, label in enumerate(clusters) if label == cluster_id]
    edges_in_cluster = [
        (u, v) for u, v in graph.edges(data=False)
        if clusters[u] == cluster_id and clusters[v] == cluster_id
    ]
    edges_in_cluster_with_weight = [
        (u, v, graph[u][v]['weight']) for u, v in graph.edges(data=False)
        if clusters[u] == cluster_id and clusters[v] == cluster_id
    ]
    return nodes_in_cluster, edges_in_cluster

def compute_cluster_distance_matrix(graph, clusters, cluster_id):
    # Extraire les nœuds appartenant au cluster
    nodes_in_cluster = [i for i, label in enumerate(clusters) if label == cluster_id]

    # Construire un sous-graphe pour le cluster
    subgraph = graph.subgraph(nodes_in_cluster).copy()

    # Créer une matrice des distances initialisée avec np.inf
    n_nodes = len(nodes_in_cluster)
    distance_matrix = np.full((n_nodes, n_nodes), np.inf)

    # Remplir la matrice des distances pour les nœuds du sous-graphe
    for i, source in enumerate(nodes_in_cluster):
        for j, target in enumerate(nodes_in_cluster):
            if source == target:
                distance_matrix[i, j] = 0  # La distance d'un nœud à lui-même est toujours 0
            else:
                try:
                    distance = nx.shortest_path_length(subgraph, source=source, target=target, weight="weight")
                    distance_matrix[i, j] = distance
                except nx.NetworkXNoPath:
                    continue  # Si aucun chemin n'existe, garder np.inf

    return distance_matrix

def extract_nodes(clusters, cluster_id):
    nodes_in_cluster = [i for i, label in enumerate(clusters) if label == cluster_id]
    return nodes_in_cluster

def remove_consecutive_duplicates(path):
    if not path:
        return []
    cleaned_path = [path[0]]
    for node in path[1:]:
        if node != cleaned_path[-1]:
            cleaned_path.append(node)
    return cleaned_path

def create_node_mappings(nodes_in_cluster):
    """
    Crée une correspondance entre les indices originaux des nœuds et de nouveaux indices consécutifs.

    Args:
        nodes_in_cluster (list): Liste des indices originaux des nœuds dans le cluster.

    Returns:
        tuple: Deux dictionnaires :
            - original_to_reduced : Mappe les indices originaux vers les indices réduits.
            - reduced_to_original : Mappe les indices réduits vers les indices originaux.
    """
    # Création des dictionnaires de correspondance
    original_to_reduced = {node: i for i, node in enumerate(nodes_in_cluster)}
    #print("Original to Reduced Mapping:", original_to_reduced)
    reduced_to_original = {i: node for i, node in enumerate(nodes_in_cluster)}
    #print("Reduced to Original Mapping:", reduced_to_original)
    return original_to_reduced, reduced_to_original


def rearrange_matrix_by_mapping(matrix, original_to_reduced):
    """
    Réarrange une matrice en échangeant les indices selon le dictionnaire de mapping.

    Args:
        matrix (numpy.ndarray): La matrice originale.
        original_to_reduced (dict): Dictionnaire qui mappe les indices originaux vers les indices réduits.

    Returns:
        numpy.ndarray: Une nouvelle matrice réarrangée.
    """
    # Nombre de nœuds dans le cluster
    n_nodes = len(original_to_reduced)

    # Créer une matrice vide pour le résultat
    rearranged_matrix = np.zeros((n_nodes, n_nodes))

    # Réorganiser les indices en fonction du mapping
    for original_i, reduced_i in original_to_reduced.items():
        for original_j, reduced_j in original_to_reduced.items():
            rearranged_matrix[reduced_i, reduced_j] = matrix[original_i, original_j]

    return rearranged_matrix

def rearrange_edges_by_mapping(edges, original_to_reduced):
    """
    Réarrange les indices des arêtes en remplaçant les indices globaux par les indices locaux.

    Args:
        edges (list of tuples): Liste des arêtes sous forme (u, v).
        original_to_reduced (dict): Dictionnaire qui mappe les indices originaux vers les indices réduits.

    Returns:
        list of tuples: Liste des arêtes avec les indices locaux.
    """
    # Liste des nouvelles arêtes avec les indices locaux
    rearranged_edges = []

    # Réarranger les indices des arêtes
    for u, v in edges:
        if u in original_to_reduced and v in original_to_reduced:
            # Remplacer les indices globaux par les indices locaux
            new_u = original_to_reduced[u]
            new_v = original_to_reduced[v]
            rearranged_edges.append((new_u, new_v))

    return rearranged_edges


def map_path_to_original(path, reduced_to_original):
    """
    Transforme un chemin utilisant des indices réduits en un chemin avec les indices originaux.

    Args:
        path (list): Liste des indices réduits représentant le chemin.
        reduced_to_original (dict): Dictionnaire qui mappe les indices réduits aux indices originaux.

    Returns:
        list: Chemin avec les indices d'origine.
    """
    # Convertir chaque indice réduit en indice original en utilisant le dictionnaire
    original_path = [reduced_to_original[reduced_index] for reduced_index in path]
    return original_path

def get_local_node_id(global_node_id, original_to_reduced):
    """
    Retourne l'ID local (réduit) d'un nœud global à partir d'un dictionnaire de mapping.

    Args:
        global_node_id (int): L'ID global du nœud.
        original_to_reduced (dict): Le dictionnaire qui mappe les IDs globaux vers les IDs locaux.

    Returns:
        int: L'ID local du nœud.

    Raises:
        ValueError: Si le nœud global n'existe pas dans le dictionnaire.
    """
    if global_node_id in original_to_reduced:
        return original_to_reduced[global_node_id]
    else:
        raise ValueError(f"Le nœud global {global_node_id} n'existe pas dans le dictionnaire original_to_reduced.")

def find_nearest_node_in_cluster_to_global_node_0(graph, cluster_id, clusters):
    """
    Trouve l'ID global du nœud du cluster spécifié qui est le plus proche du nœud global avec l'ID 0.

    Args:
        graph (networkx.Graph): Le graphe global pondéré.
        cluster_id (int): L'ID du cluster pour lequel trouver le nœud le plus proche.
        clusters (list): Liste des clusters assignés à chaque nœud.

    Returns:
        int: ID global du nœud dans le cluster spécifié le plus proche du nœud 0.
    """
    # Étape 1 : Identifier les nœuds dans le cluster spécifié
    nodes_in_cluster = [i for i, label in enumerate(clusters) if label == cluster_id]

    # Étape 2 : Trouver le nœud du cluster le plus proche du nœud 0
    min_distance = float('inf')
    nearest_node = None

    for node in nodes_in_cluster:
        try:
            distance = nx.shortest_path_length(graph, source=0, target=node, weight="weight")
            if distance < min_distance:
                min_distance = distance
                nearest_node = node
        except nx.NetworkXNoPath:
            continue  # Ignorer les nœuds sans chemin vers le nœud 0
    
    #print("Noeud le plus proche:", nearest_node)

    return nearest_node





# Renvoie le chemin de l'ACO 
def generate_path_cluster_multibase(num_agents, nodes_position, edges):

    graph = build_weighted_graph(nodes_position, edges)
    clusters, cluster_weights, barycenters, nearest_nodes = generate_clusters(
        graph, nodes_position, num_agents, tolerance=0.25
    )

    all_paths = []
    for cluster_id in range(num_agents):
        # Étape 1 : Calculer le chemin initial vers le barycentre
        end = nearest_nodes[cluster_id]
               
        nodes_in_cluster, edges_in_cluster = extract_cluster_nodes_and_edges(graph, nodes_position, clusters, cluster_id)
        nodes_in_cluster_id= extract_nodes(clusters, cluster_id)
        original_to_reduced, reduced_to_original = create_node_mappings(nodes_in_cluster_id)

        start_local= get_local_node_id(end, original_to_reduced)


        rearranged_edges = rearrange_edges_by_mapping(edges_in_cluster, original_to_reduced)
        subgraph = build_weighted_subgraph(nodes_in_cluster, rearranged_edges)

        distance_matrix_cluster = compute_weighted_distance_matrix(subgraph)

        # Étape 3 : Exécuter l'ACO
        path, best_length = aco_tsp(distance_matrix_cluster,start_local, subgraph, 1)
        for i in range(len(path)):
            is_valid = validate_path(subgraph, path[i])
            if not is_valid:
                path[i] = correct_path(subgraph, path[i])

        original_path = [reduced_to_original[reduced_index] for reduced_index in path[0]]

        chemin_complet = original_path
        all_paths.append(chemin_complet)


    return all_paths

def generate_path_cluster_monobase(num_agents, nodes_position, edges, loop_number=5):

    graph = build_weighted_graph(nodes_position, edges)
    clusters, cluster_weights, barycenters, nearest_nodes = generate_clusters(
        graph, nodes_position, num_agents, tolerance=0.25
    )
    all_paths = []
    for cluster_id in range(num_agents):
        
        nearest_node_to_zero = find_nearest_node_in_cluster_to_global_node_0(graph, cluster_id, clusters)
        chemin_agent_vers_cluster = nx.shortest_path(graph, source=0, target= nearest_node_to_zero, weight="weight")
        chemin_agent_vers_zero = nx.shortest_path(graph, source=nearest_node_to_zero, target= 0, weight="weight")

        nodes_in_cluster, edges_in_cluster = extract_cluster_nodes_and_edges(graph, nodes_position, clusters, cluster_id)
        nodes_in_cluster_id= extract_nodes(clusters, cluster_id)
        original_to_reduced, reduced_to_original = create_node_mappings(nodes_in_cluster_id)

        start_local= get_local_node_id(nearest_node_to_zero, original_to_reduced)


        rearranged_edges = rearrange_edges_by_mapping(edges_in_cluster, original_to_reduced)
        subgraph = build_weighted_subgraph(nodes_in_cluster, rearranged_edges)

        distance_matrix_cluster = compute_weighted_distance_matrix(subgraph)

        start_time = time.time()
        
        path, best_length = aco_tsp(distance_matrix_cluster,start_local, subgraph, 1)
        for i in range(len(path)):
            is_valid = validate_path(subgraph, path[i])
            if not is_valid:
                path[i] = correct_path(subgraph, path[i])
        original_path = [reduced_to_original[reduced_index] for reduced_index in path[0]]
        
        repeated_paths = original_path * loop_number


        chemin_complet = chemin_agent_vers_cluster + repeated_paths + chemin_agent_vers_zero
        all_paths.append(chemin_complet)

    return all_paths