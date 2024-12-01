# L'algo récatif doit régler le probleme que quand un agent va d'un noeud a un autre un autre ne peux pas le suivre sinon
# ils se suivent rapidement psk le next node a pas encore était actualisé l'idleness
# TODO a faire j'ai rien fait

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
def agent_process(agent_id, position_queue, last_visited_shared, shared_list_next_node, lock):
    agent_position = nodes_position[0]
    agent_target_position = nodes_position[1]
    agent_node_index = 0

    i = 1
    next_node_index = 0
    while True:
        x1, y1 = agent_position
        x2, y2 = agent_target_position
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si on est arrivé à un nœud
        if distance < agent_speed:
            agent_node_index = next_node_index
            # Met à jour le temps de la dernière visite du nœud actuel dans le dictionnaire partagé
            last_visited_shared[agent_node_index] = time.time()

            voisins = adjacency_list[agent_node_index]
            random.shuffle(voisins)
            next_node_index = min(voisins, key=lambda x: last_visited_shared[x] if last_visited_shared[x] is not None else -float('inf'))
            
            with lock:
                if next_node_index in shared_list_next_node:
                    # Choisir un autre chemin
                    # Si pas d'autres chemins, ok on peut prendre le même chemin
                    if len(voisins) > 1:
                        voisins.remove(next_node_index)
                    random.shuffle(voisins)
                    next_node_index = min(voisins, key=lambda x: last_visited_shared[x] if last_visited_shared[x] is not None else -float('inf'))

            with lock:  # Ensure only one process updates the list at a time
                shared_list_next_node[agent_id] = next_node_index

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

    # Create a shared list with three elements
    shared_list_next_node = manager.list([0] * num_agents)  # Shared list initialized to [0, 0, 0]
    lock = multiprocessing.Lock()  # Lock to avoid concurrent writes

    # Création des files de communication et des processus pour chaque agent
    position_queues = []
    agents = []
    initial_node = nodes_position[1]
    initial_target_node = nodes_position[2]

    for i in range(num_agents):
        position_queue = multiprocessing.Queue()
        position_queues.append(position_queue)
        agent = multiprocessing.Process(target=agent_process, args=(i, position_queue, last_visited_shared, shared_list_next_node, lock))
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
