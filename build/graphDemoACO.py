import pygame
import random
import math
import multiprocessing
import time
from graphstructure import *  # Assurez-vous que nodes et edges sont définis dans graphstructure

# Configuration de la fenêtre
WIDTH, HEIGHT = 750, 520
NODE_RADIUS = 10
AGENT_RADIUS = 5
IDLE_COLOR = (255, 0, 0)  # Rouge pour les nœuds inactifs
VISITED_COLOR = (0, 255, 0)  # Vert pour les nœuds récemment visités
EDGE_COLOR = (200, 200, 200)
AGENT_COLOR = (255, 0, 0)  # Couleur de l'agent
FPS = 30
PROXIMITY_THRESHOLD = 10  # Distance de tolérance pour considérer qu’un agent est sur un nœud

# Agent setup
agent_speed = 5
num_agents = 3

# Phéromones setup
initial_pheromone = 1.0
evaporation_rate = 0.001  # Taux d'évaporation des phéromones

# Informations récupérées depuis graphstructure
adjacency_list = {i: [] for i in range(len(nodes_position))}
for a, b in edges:
    adjacency_list[a].append(b)
    adjacency_list[b].append(a)

# Initialiser les phéromones sur chaque arête
pheromones = {(min(a, b), max(a, b)): initial_pheromone for a, b in edges}

# Dictionnaire pour stocker le temps de la dernière visite de chaque nœud
last_visited = {i: None for i in range(len(nodes_position))}  # Aucun nœud visité au départ

# Fonction d'évaporation des phéromones, avec modification directe de pheromones_shared
def evaporate_pheromones(pheromones_shared):
    for edge in pheromones_shared.keys():
        # Applique l'évaporation et met à jour directement la valeur dans le dictionnaire partagé
        pheromones_shared[edge] = max(0, pheromones_shared[edge] * (1 - evaporation_rate))


# Fonction pour trouver l'index du nœud le plus proche si à proximité
def get_nearest_node_index(position):
    for i, node in enumerate(nodes_position):
        if math.hypot(position[0] - node[0], position[1] - node[1]) < PROXIMITY_THRESHOLD:
            return i
    return None

# Fonction de déplacement de l'agent avec choix de chemin influencé par les phéromones
def agent_process(agent_id, position_queue, start_position, start_target, last_visited_shared, pheromones_shared):
    agent_position = start_position
    agent_target = start_target
    agent_node_index = nodes_position.index(start_position)
    previous_node_index = None

    while True:
        x1, y1 = agent_position
        x2, y2 = agent_target
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si on est arrivé à un nœud
        if distance < agent_speed:
            previous_node_index = agent_node_index
            agent_node_index = nodes_position.index(agent_target)
            # Met à jour le temps de la dernière visite du nœud actuel dans le dictionnaire partagé
            last_visited_shared[agent_node_index] = time.time()

            # Augmenter la phéromone sur l’arête empruntée
            if previous_node_index is not None:
                edge = (min(previous_node_index, agent_node_index), max(previous_node_index, agent_node_index))
                if edge in pheromones_shared:
                    pheromones_shared[edge] += 1  # Augmentation de la phéromone

            # Choisir le prochain nœud en fonction des phéromones, en excluant le nœud précédent
            next_node_index = select_next_node(agent_node_index, previous_node_index, pheromones_shared)
            agent_target = nodes_position[next_node_index]
        else:
            angle = math.atan2(dy, dx)
            agent_position = (x1 + agent_speed * math.cos(angle), y1 + agent_speed * math.sin(angle))

        position_queue.put(agent_position)
        time.sleep(1 / FPS)

# Fonction pour choisir le prochain nœud en fonction des phéromones, en privilégiant les chemins avec moins de phéromones
def select_next_node(current_node_index, previous_node_index, pheromones_shared):
    # Exclure le nœud précédent des voisins pour éviter les allers-retours
    neighbors = [n for n in adjacency_list[current_node_index] if n != previous_node_index]
    
    # Calcul des probabilités en fonction de l'inverse des phéromones (plus de phéromones -> moins de chance d'être choisi)
    probabilities = []
    total_inverse_pheromone = 0
    for neighbor in neighbors:
        edge = (min(current_node_index, neighbor), max(current_node_index, neighbor))
        pheromone_level = pheromones_shared[edge]
        # Utiliser l'inverse des phéromones pour favoriser les chemins avec moins de phéromones
        inverse_pheromone_level = 1 / (pheromone_level + 1e-6)  # Ajout d'une petite valeur pour éviter la division par zéro
        probabilities.append(inverse_pheromone_level)
        total_inverse_pheromone += inverse_pheromone_level

    # Normaliser pour obtenir des probabilités
    if total_inverse_pheromone == 0:
        # Si toutes les phéromones sont à zéro, choisir aléatoirement
        return random.choice(neighbors)
    
    probabilities = [p / total_inverse_pheromone for p in probabilities]
    return random.choices(neighbors, weights=probabilities, k=1)[0]



# Fonction pour calculer la couleur d'un nœud en fonction du temps écoulé depuis la dernière visite
def calculate_node_color(last_visit_time):
    if last_visit_time is None:
        # Nœud jamais visité, il reste rouge
        return IDLE_COLOR
    
    elapsed_time = time.time() - last_visit_time
    # Interpole entre vert et rouge en fonction du temps depuis la dernière visite
    red_intensity = min(255, int(255 * elapsed_time / 20))  # 20 secondes pour atteindre le rouge complet
    green_intensity = max(0, 255 - red_intensity)
    return (red_intensity, green_intensity, 0)

if __name__ == '__main__':
    # Initialisation de pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Agent - Graph Simulation")
    clock = pygame.time.Clock()

    # Utiliser un dictionnaire partagé pour `last_visited` et `pheromones`
    manager = multiprocessing.Manager()
    last_visited_shared = manager.dict({i: None for i in range(len(nodes_position))})
    pheromones_shared = manager.dict(pheromones)  # Dictionnaire partagé pour les phéromones

    # Création des files de communication et des processus pour chaque agent
    position_queues = []
    agents = []
    initial_node = nodes_position[0]
    initial_target_node = nodes_position[1]

    for i in range(num_agents):
        position_queue = multiprocessing.Queue()
        position_queues.append(position_queue)
        agent = multiprocessing.Process(target=agent_process, args=(i, position_queue, initial_node, initial_target_node, last_visited_shared, pheromones_shared))
        agents.append(agent)
        agent.start()

    running = True
    agent_positions = [initial_node] * num_agents  # Position initiale de chaque agent

    while running:

        screen.fill((255, 255, 255))

        # Appliquer l'évaporation des phéromones
        evaporate_pheromones(pheromones_shared)

        # Dessiner la carte avec des lignes plus épaisses pour les arêtes avec plus de phéromones
        for edge, pheromone in pheromones_shared.items():
            node1, node2 = nodes_position[edge[0]], nodes_position[edge[1]]
            thickness = max(1, int(2 + pheromone * 2))  # Épaisseur de la ligne selon le niveau de phéromones
            pygame.draw.line(screen, EDGE_COLOR, node1, node2, thickness)

        # Dessiner les nœuds avec la couleur en fonction de leur oisiveté
        for i, node in enumerate(nodes_position):
            node_color = calculate_node_color(last_visited_shared[i])
            pygame.draw.circle(screen, node_color, node, NODE_RADIUS)

        # Récupérer et dessiner chaque agent
        for i in range(num_agents):
            if not position_queues[i].empty():
                agent_positions[i] = position_queues[i].get()

            pygame.draw.circle(screen, AGENT_COLOR, (int(agent_positions[i][0]), int(agent_positions[i][1])), AGENT_RADIUS)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(FPS)

    # Terminer et rejoindre chaque processus
    for agent in agents:
        agent.terminate()
        agent.join()

    pygame.quit()
