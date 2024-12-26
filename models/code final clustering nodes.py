from graphstructure import nodes_position, edges
import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


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


# Fonction pour calculer le poids total des clusters
def compute_cluster_weights(graph, clusters, n_clusters):
    cluster_weights = [0] * n_clusters
    for u, v, weight in graph.edges(data="weight"):
        if clusters[u] == clusters[v]:  # Si les deux nœuds appartiennent au même cluster
            cluster_id = clusters[u]
            cluster_weights[cluster_id] += weight
    return cluster_weights


# Fonction : Exécuter K-Means jusqu'à respecter la contrainte de poids
def balanced_weighted_kmeans(distance_matrix, graph, n_clusters, tolerance=0.25, max_iterations=1000):
    best_clusters = None
    best_weights = None
    best_difference = float('inf')  # Initialise la meilleure différence

    for iteration in range(max_iterations):
        kmeans = KMeans(n_clusters=n_clusters, random_state=iteration)
        clusters = kmeans.fit_predict(distance_matrix)
        cluster_weights = compute_cluster_weights(graph, clusters, n_clusters)

        # Calculer la différence relative entre le plus grand et le plus petit poids
        max_weight = max(cluster_weights)
        min_weight = min(cluster_weights)
        difference = (max_weight - min_weight) / max_weight

        print(
            f"Iteration {iteration + 1}: Max weight = {max_weight:.2f}, Min weight = {min_weight:.2f}, Difference = {difference:.2%}")

        # Mettre à jour la meilleure solution si elle est meilleure
        if difference < best_difference:
            best_difference = difference
            best_clusters = clusters
            best_weights = cluster_weights

        # Arrêter si la contrainte est respectée
        if difference <= tolerance:
            print("Contrainte respectée : différence de poids < 25 %")
            return clusters, cluster_weights

    print("Max iterations atteintes, meilleure solution approximative utilisée.")
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


# Visualisation
def visualize_clusters_with_barycenters(graph, clusters, nodes_position, n_clusters, barycenters, nearest_nodes):
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
    plt.figure(figsize=(12, 8))
    pos = {i: coord for i, coord in enumerate(nodes_position)}

    for cluster_id in range(n_clusters):
        nodes_in_cluster = [i for i, label in enumerate(clusters) if label == cluster_id]
        nx.draw(graph, pos, nodelist=nodes_in_cluster, node_color=colors[cluster_id % len(colors)], node_size=500)
        plt.scatter(*barycenters[cluster_id], color=colors[cluster_id % len(colors)], marker='x', s=300, linewidths=3)
        plt.scatter(*nodes_position[nearest_nodes[cluster_id]], color='white', edgecolor='black', s=600, linewidths=3)

    plt.title("Clustering avec barycentres pondérés et nœuds proches")
    plt.show()


# Programme principal
if __name__ == "__main__":
    # Construire le graphe pondéré
    graph = build_weighted_graph(nodes_position, edges)
    n_clusters = 2

    # Créer la matrice des distances pondérées
    distance_matrix = compute_weighted_distance_matrix(graph)

    # Exécuter le K-Means équilibré avec contrainte de poids
    clusters, cluster_weights = balanced_weighted_kmeans(distance_matrix, graph, n_clusters, tolerance=0.25)

    # Calculer les barycentres pondérés
    barycenters = compute_cluster_barycenters(graph, clusters, nodes_position, n_clusters)

    # Trouver les nœuds les plus proches des barycentres
    nearest_nodes = find_nearest_nodes_to_barycenters(barycenters, clusters, nodes_position, n_clusters)

    # Afficher les poids des clusters avec leurs couleurs
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan']
    print("\nPoids des clusters par couleur :")
    for i, weight in enumerate(cluster_weights):
        print(f"Cluster {colors[i % len(colors)]} : {weight:.2f}")

    # Visualiser les clusters avec barycentres et nœuds proches
    visualize_clusters_with_barycenters(graph, clusters, nodes_position, n_clusters, barycenters, nearest_nodes)
