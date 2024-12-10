import pygame
import random
import math
import multiprocessing
import time
from collections import deque  # Pour BFS
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


# Fonction pour trouver le chemin le plus court (BFS)
def bfs_shortest_path(start, goal):
    queue = deque([[start]])  # File de chemins, initialisée avec le nœud de départ

    while queue:
        path = queue.popleft()  # Récupérer le premier chemin
        node = path[-1]  # Dernier nœud du chemin actuel

        if node == goal:  # Si le nœud cible est atteint
            return path

        for neighbor in adjacency_list[node]:
            new_path = list(path)
            new_path.append(neighbor)
            queue.append(new_path)

    return []  # Aucun chemin trouvé


# Fonction de déplacement de l'agent avec chemin donné
def agent_process_BFS(agent_id, position_queue, last_visited_shared, shared_list_next_node, lock):
    agent_position = nodes_position[0]
    agent_node_index = 0
    path = []  # Chemin que l'agent doit suivre
    path_index = 0

    while True:
        # Si l'agent a atteint sa cible ou n'a pas de chemin à suivre
        if not path or path_index >= len(path):
            # Choisir un nouveau nœud cible aléatoire
            target_node = random.randint(0, len(nodes_position) - 1)
            path = bfs_shortest_path(agent_node_index, target_node)
            path_index = 0

        # Déterminer le nœud cible actuel à suivre dans le chemin
        next_node_index = path[path_index]
        agent_target_position = nodes_position[next_node_index]

        x1, y1 = agent_position
        x2, y2 = agent_target_position
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si l'agent arrive au nœud cible actuel
        if distance < agent_speed:
            agent_node_index = next_node_index
            path_index += 1  # Passer au prochain nœud dans le chemin
            last_visited_shared[agent_node_index] = time.time()

        # Déplacer l'agent vers le nœud cible actuel
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
    initial_node = nodes_position[0]

    for i in range(num_agents):
        position_queue = multiprocessing.Queue()
        position_queues.append(position_queue)
        agent = multiprocessing.Process(target=agent_process_BFS, args=(i, position_queue, last_visited_shared, shared_list_next_node, lock))
        agents.append(agent)
        agent.start()

    running = True
    agent_positions = [initial_node] * num_agents  # Position initiale de chaque agent
    start_time = time.time()
    # Initialiser la variable pour accumuler l'oisiveté totale
    total_idleness = 0
    total_seconds = 0  # Compter le nombre de secondes écoulées

    while running:
        # Vérifier si 30 secondes sont écoulées
        elapsed_time = time.time() - start_time
        if elapsed_time >= 20:
            running = False

        # Calculer l'oisiveté moyenne pendant la simulation
        current_idleness = calculate_average_idleness(last_visited_shared)
        total_idleness += current_idleness  # Ajouter l'oisiveté du moment
        total_seconds += 1  # Incrémenter le nombre de secondes

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
        
        average_idleness = calculate_average_idleness(last_visited_shared)

        # Afficher l'oisiveté moyenne
        idle_text = f"Oisiveté moyenne : {average_idleness:.2f}"
        idle_surface = font.render(idle_text, True, (0, 0, 0))  # Texte en noir
        screen.blit(idle_surface, (10, 10))  # Affiche le texte en haut à gauche

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
        # À la fin de la simulation, afficher l'oisiveté moyenne finale
    final_average_idleness = total_idleness / total_seconds if total_seconds > 0 else 0
    screen.fill((255, 255, 255))

    # Afficher l'oisiveté moyenne finale au centre de l'écran
    idle_text = f"Oisiveté moyenne : {final_average_idleness:.2f}"
    idle_surface = font.render(idle_text, True, (0, 0, 0))  # Texte en noir
    screen.blit(idle_surface, (WIDTH // 2 - idle_surface.get_width() // 2, HEIGHT // 2 - idle_surface.get_height() // 2))

    # Dessiner un bouton "Quitter" en bas de l'écran
    quit_button_rect = pygame.Rect(WIDTH - 100, HEIGHT - 40, 80, 30)
    pygame.draw.rect(screen, (0, 0, 255), quit_button_rect)  # Bouton bleu
    quit_text = font.render("Quitter", True, (255, 255, 255))
    screen.blit(quit_text, (WIDTH - 95, HEIGHT - 30))

    pygame.display.flip()

    # Attendre que l'utilisateur clique sur "Quitter"
    waiting_for_quit = True
    while waiting_for_quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_for_quit = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quit_button_rect.collidepoint(event.pos):
                    waiting_for_quit = False


    # Terminer et rejoindre chaque processus
    for agent in agents:
        agent.terminate()
        agent.join()

    pygame.quit()
