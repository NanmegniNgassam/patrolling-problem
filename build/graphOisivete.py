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

# Informations récupérées depuis graphstructure
adjacency_list = {i: [] for i in range(len(nodes_position))}
for a, b in edges:
    adjacency_list[a].append(b)
    adjacency_list[b].append(a)

# Dictionnaire pour stocker le temps de la dernière visite de chaque nœud
last_visited = {i: None for i in range(len(nodes_position))}  # Aucun nœud visité au départ


# Fonction de déplacement de l'agent avec chemin donné
def agent_process(agent_id, position_queue, chemin, last_visited_shared):
    agent_position = nodes_position[chemin[0]]
    agent_target_position = nodes_position[chemin[1]]
    agent_node_index = chemin[0]

    i = 1
    while True:
        x1, y1 = agent_position
        x2, y2 = agent_target_position
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si on est arrivé à un nœud
        if distance < agent_speed:
            agent_node_index = chemin[i]
            # Met à jour le temps de la dernière visite du nœud actuel dans le dictionnaire partagé
            last_visited_shared[agent_node_index] = time.time()

            next_node_index = chemin[i+1]
            agent_target_position = nodes_position[next_node_index]
            i += 1
        else:
            angle = math.atan2(dy, dx)
            agent_position = (x1 + agent_speed * math.cos(angle), y1 + agent_speed * math.sin(angle))

        position_queue.put(agent_position)
        time.sleep(1 / FPS)


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

    # Configuration de la police pour afficher les indices
    font_size = 12  # Taille de la police
    font = pygame.font.Font(None, font_size)  # Charger la police par défaut

    # Utiliser un dictionnaire partagé pour `last_visited`
    manager = multiprocessing.Manager()
    last_visited_shared = manager.dict({i: None for i in range(len(nodes_position))})

    # Création des files de communication et des processus pour chaque agent
    position_queues = []
    agents = []
    initial_node = nodes_position[1]
    initial_target_node = nodes_position[2]

    chemins = []
    chemins.append((7, 11, 8, 10, 12, 41, 43, 42, 40, 42, 26, 22, 24, 25, 23, 27, 21, 49, 45, 48, 44, 46, 47, 49, 21, 27, 39, 37, 36, 38, 20, 15, 17, 18, 16, 14, 19, 35, 33, 32, 34, 32, 5, 2, 0, 4, 1, 6, 3, 6, 28, 30, 31, 29, 28, 29, 13, 9, 7))
    chemins.append((20, 15, 18, 17, 16, 14, 19, 35, 33, 32, 34, 32, 5, 3, 4, 0, 2, 0, 1, 6, 28, 30, 31, 29, 13, 9, 7, 11, 8, 10, 12, 41, 43, 42, 40, 42, 26, 22, 25, 24, 23, 27, 21, 49, 45, 44, 46, 48, 47, 49, 21, 27, 39, 37, 36, 38, 20))
    chemins.append((46, 48, 47, 49, 45, 44, 3, 5, 32, 34, 35, 33, 35, 19, 14, 16, 17, 18, 15, 20, 38, 36, 37, 39, 27, 23, 25, 24, 22, 26, 21, 26, 42, 40, 41, 43, 41, 12, 10, 8, 11, 9, 7, 13, 
    29, 31, 30, 28, 6, 1, 4, 0, 2, 3, 44, 46))

    print(chemins)
    for i in range(num_agents):
        if num_agents != len(chemins):
            raise Exception(f"Problème : {len(chemins)} chemins pour {num_agents} agents.")
        position_queue = multiprocessing.Queue()
        position_queues.append(position_queue)
        agent = multiprocessing.Process(target=agent_process, args=(i, position_queue, chemins[i], last_visited_shared))
        agents.append(agent)
        agent.start()

    running = True
    agent_positions = [initial_node] * num_agents  # Position initiale de chaque agent

    while running:

        screen.fill((255, 255, 255))

        # Dessiner la carte
        for edge in edges:
            pygame.draw.line(screen, EDGE_COLOR, nodes_position[edge[0]], nodes_position[edge[1]], 2)

        # Dessiner les nœuds avec la couleur en fonction de leur oisiveté
        for i, node in enumerate(nodes_position):
            node_color = calculate_node_color(last_visited_shared[i])
            pygame.draw.circle(screen, node_color, node, NODE_RADIUS)

        # Dessiner les nœuds avec la couleur en fonction de leur oisiveté et afficher les indices
        for i, node in enumerate(nodes_position):
            node_color = calculate_node_color(last_visited_shared[i])
            pygame.draw.circle(screen, node_color, node, NODE_RADIUS)
            text_surface = font.render(str(i), True, (0, 0, 0))  # Texte en noir
            text_x = node[0] - text_surface.get_width() / 2
            text_y = node[1] - text_surface.get_height() / 2
            screen.blit(text_surface, (text_x, text_y))

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
