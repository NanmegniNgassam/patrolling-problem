

import pygame
import random
import math
import multiprocessing
import time
from graphstructure import *  # Assurez-vous que nodes et edges sont définis dans graphstructure
import heapq

def euclidean_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def a_star_algorithm(start, goal):
    # Construire le graphe
    graph = {i: [] for i in range(len(nodes_position))}
    for edge in edges:
        graph[edge[0]].append(edge[1])
        graph[edge[1]].append(edge[0])
    
    # Initialisation des ensembles ouverts et fermés
    open_set = []
    heapq.heappush(open_set, (0, start))  # (f_score, node)
    came_from = {}  # Pour suivre le chemin
    g_score = {node: float('inf') for node in range(len(nodes_position))}
    g_score[start] = 0
    f_score = {node: float('inf') for node in range(len(nodes_position))}
    f_score[start] = euclidean_distance(nodes_position[start], nodes_position[goal])
    
    while open_set:
        # Récupérer le nœud avec le plus petit f_score
        _, current = heapq.heappop(open_set)
        
        # Vérifier si on a atteint l'objectif
        if current == goal:
            path = []
            total_distance = g_score[current]  # La distance totale est le g_score du goal
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()  # Retourner le chemin dans le bon ordre
            return path, total_distance
        
        # Explorer les voisins
        for neighbor in graph[current]:
            tentative_g_score = g_score[current] + euclidean_distance(nodes_position[current], nodes_position[neighbor])
            
            if tentative_g_score < g_score[neighbor]:
                # Mettre à jour le chemin vers ce voisin
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + euclidean_distance(nodes_position[neighbor], nodes_position[goal])
                
                # Ajouter le voisin à l'open set s'il n'y est pas déjà
                if all(neighbor != item[1] for item in open_set):
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return None, None  # Si aucun chemin n'est trouvé

# Configuration de la fenêtre
WIDTH, HEIGHT = 750, 520
NODE_RADIUS = 10
AGENT_RADIUS = 5
IDLE_COLOR = (255, 0, 0)  # Rouge pour les nœuds inactifs
VISITED_COLOR = (0, 255, 0)  # Vert pour les nœuds récemment visités
EDGE_COLOR = (200, 200, 200)
#AGENT_COLOR = (255, 0, 0)  # Couleur de l'agent
AGENT_COLORS = [
    (0, 0, 255),   # Bleu pour l'agent 0
    (255, 0, 0),   # Rouge pour l'agent 1
    (0, 255, 0)    # Vert pour l'agent 2
]
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
#last_visited = {i: None for i in range(len(nodes_position))}  # Aucun nœud visité au départ


def get_ith_smallest_key(dict_values, i):
    from itertools import groupby
    from operator import itemgetter

    # Transformer les None en une valeur très petite (-float('inf'))
    sorted_items = sorted(dict_values.items(), key=lambda x: x[1] if x[1] is not None else -float('inf'))

    # Grouper les éléments par valeur
    grouped = [list(group) for key, group in groupby(sorted_items, key=itemgetter(1))]

    # Vérifier si l'indice i est dans la plage valide
    if 0 < i <= len(grouped):
        # Retourner toutes les clés associées à la i-ème plus petite valeur (égale)
        return [item[0] for item in grouped[i-1]]
    else:
        return None  # Retourner None si i est en dehors des limites valides


# Fonction de déplacement de l'agent avec chemin donné
def agent_process(agent_id, position_queue, last_visited_shared, shared_list_node_target, shared_list_chemins, lock):
    agent_position = nodes_position[0]
    agent_target_position = nodes_position[1]
    agent_node_index = 0

    last_visited_shared[agent_node_index] = time.time()

    i = 1
    next_node_index = 1
    while True:
        x1, y1 = agent_position
        x2, y2 = agent_target_position
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si on est arrivé à un nœud
        if distance < agent_speed:

            agent_node_index = next_node_index
            with lock:
                # Met à jour le temps de la dernière visite du nœud actuel dans le dictionnaire partagé
                last_visited_shared[agent_node_index] = time.time()

            if not shared_list_chemins[agent_id]:

                # La liste des noeuds qui ont la pire oisiveté
                target_indexes = []
                with lock :
                    target_indexes = get_ith_smallest_key(last_visited_shared, 1)
                    test = get_ith_smallest_key(last_visited_shared, 2)



                # La liste des chemins les plus courts vers ces noeuds
                longueur_chemins = []
                for noeud in target_indexes:
                    _, distance = a_star_algorithm(agent_node_index, noeud)
                    longueur_chemins.append(distance)
                # smallest_indices = sorted(range(len(longueur_chemins)), key=lambda i: longueur_chemins[i])[:5]
                # plus_petit_chemin_indice = random.choice(smallest_indices)
                # target_index = target_indexes[plus_petit_chemin_indice]
                plus_petit_chemin_indice = longueur_chemins.index(min(longueur_chemins))
                target_index = target_indexes[plus_petit_chemin_indice]

                if target_index in shared_list_node_target:

                    target_index = None
                    longueur_chemins[plus_petit_chemin_indice] = float('inf')

                    i=2
                    while not target_index:

                        while not all(x == float('inf') for x in longueur_chemins) and target_index is None:
                            # Choisir un autre noeud cible
                            longueur_chemins[plus_petit_chemin_indice] = float('inf')
                            smallest_indices = sorted(range(len(longueur_chemins)), key=lambda i: longueur_chemins[i])[:5]
                            plus_petit_chemin_indice = random.choice(smallest_indices)
                            target_index = target_indexes[plus_petit_chemin_indice]
                            # plus_petit_chemin_indice = longueur_chemins.index(min(longueur_chemins))
                            # target_index = target_indexes[plus_petit_chemin_indice]
                            if target_index in shared_list_node_target:
                                target_index = None

                        if not target_index:
                            target_indexes = get_ith_smallest_key(last_visited_shared, i)
                            # La liste des chemins les plus courts vers ces noeuds
                            longueur_chemins = []
                            for noeud in target_indexes:
                                _, distance = a_star_algorithm(agent_node_index, noeud)
                                longueur_chemins.append(distance)
                            # smallest_indices = sorted(range(len(longueur_chemins)), key=lambda i: longueur_chemins[i])[:5]
                            # plus_petit_chemin_indice = random.choice(smallest_indices)
                            # target_index = target_indexes[plus_petit_chemin_indice]
                            plus_petit_chemin_indice = longueur_chemins.index(min(longueur_chemins))
                            target_index = target_indexes[plus_petit_chemin_indice]
                            if target_index in shared_list_node_target:
                                target_index = None
                            i+=1

                    # Ensure only one process updates the list at a time
                    shared_list_node_target[agent_id] = next_node_index

                with lock:
                    chemin, _ = a_star_algorithm(agent_node_index, target_index)
                    chemin.pop(0)
                    shared_list_chemins[agent_id] = chemin
                    next_node_index = chemin[0]
                    
            else:
                with lock:
                    # Copie locale de la liste
                    chemin_temp = list(shared_list_chemins[agent_id])
                    # Modification de la copie locale
                    next_node_index = chemin_temp[0]
                    chemin_temp.pop(0)
                    # Reassigner si la liste est vide
                    if not chemin_temp:
                        chemin_temp = None
                    # Remettre la liste modifiée dans la liste partagée
                    shared_list_chemins[agent_id] = chemin_temp
                            
            with lock:
                # Ensure only one process updates the list at a time
                shared_list_node_target[agent_id] = target_index

            agent_target_position = nodes_position[next_node_index]
            i += 1

            print(f"AGENT {agent_id}, Je suis actuellement au noeud {agent_node_index}, Mon node target : {target_index}, Mon chemin pour y aller : {shared_list_chemins[agent_id]}")
            #time.sleep(300)  
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
    shared_list_node_target = manager.list([0] * num_agents)  # Shared list initialized to [0, 0, 0]
    shared_list_chemins = manager.list([None] * num_agents)  # Shared list initialized to [None, None, None]

    lock = multiprocessing.Lock()  # Lock to avoid concurrent writes

    # Création des files de communication et des processus pour chaque agent
    position_queues = []
    agents = []
    initial_node = nodes_position[1]
    initial_target_node = nodes_position[2]

    for i in range(num_agents):
        position_queue = multiprocessing.Queue()
        position_queues.append(position_queue)
        agent = multiprocessing.Process(target=agent_process, args=(i, position_queue, last_visited_shared, shared_list_node_target, shared_list_chemins, lock))
        agents.append(agent)
        agent.start()
    
    running = True
    agent_positions = [initial_node] * num_agents  # Position initiale de chaque agent
    start_time = time.time()
    total_idleness = 0
    total_seconds = 0  # Compter le nombre de secondes écoulées
    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
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

            # Utiliser l'ID de l'agent pour obtenir la couleur
            agent_color = AGENT_COLORS[i]
            pygame.draw.circle(screen, agent_color, (int(agent_positions[i][0]), int(agent_positions[i][1])), AGENT_RADIUS)
            #pygame.draw.circle(screen, AGENT_COLOR, (int(agent_positions[i][0]), int(agent_positions[i][1])), AGENT_RADIUS)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(FPS)
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
