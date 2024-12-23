
import pygame
import random
import math
import multiprocessing
import time
from graphstructure import *  # Assurez-vous que nodes et edges sont définis dans graphstructure
from collections import deque  # Pour BFS

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
adjacency_list = {i: [] for i in range(len(nodes_position)+1)}
for a, b in edges:
    adjacency_list[a].append(b)
    adjacency_list[b].append(a)

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


def shortest_path(graph, start, end):
    import heapq
    queue = [(0, start, [])]  # (distance, current_node, path)
    visited = set()
    
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]
        
        if node == end:
            return path
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                heapq.heappush(queue, (cost + 1, neighbor, path))
    
    return []  # Aucun chemin trouvé


# Fonction de déplacement de l'agent avec chemin donné
def agent_process(agent_id, position_queue, last_visited_shared, shared_list_next_node, lock,agent_positions,shared_list_chemins,node_locked,stop_simulation):
    
    agent_position = nodes_position[0]  # Position initiale
    agent_target_position = nodes_position[1]  # Première cible
    agent_node_index = 0
    next_node_index = 0
    while not stop_simulation.value:
        x1, y1 = agent_position
        x2, y2 = agent_target_position
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        # Si l'agent atteint un nœud
        if distance < agent_speed:
            # Déverrouillage du nœud une fois que l'agent l'a traversé
            if node_locked[agent_node_index]:
                node_locked[agent_node_index] = False

            agent_node_index = next_node_index
            last_visited_shared[agent_node_index] = time.time()  # Mise à jour du temps de visite

            # Décision cognitive : vérifier si on doit aller vers un nœud éloigné avec grande oisiveté
            if not shared_list_chemins[agent_id]:  # Si l'agent n'a pas encore de chemin à suivre
                if random.random() < 0.02: 
                    with lock:
                        # Calculer le nœud avec la plus grande oisiveté
                        max_idleness_node = max(
                            range(len(nodes_position)),
                            key=lambda x: (time.time() - last_visited_shared[x])
                            if last_visited_shared[x] is not None else float('inf')
                        )
                        max_idleness_value = (time.time() - last_visited_shared[max_idleness_node]
                                            if last_visited_shared[max_idleness_node] is not None else float('inf'))


                    # Si le nœud est verrouillé, chercher le suivant avec la plus grande oisiveté
                    if node_locked[max_idleness_node]:
                        with lock:
                            sorted_nodes_by_idleness = sorted(
                                range(len(nodes_position)),
                                key=lambda x: (time.time() - last_visited_shared[x])
                                if last_visited_shared[x] is not None else float('inf'),
                                reverse=True
                            )
                        for node in sorted_nodes_by_idleness:
                                if not node_locked[node]:
                                    max_idleness_node = node
                                    break
                        max_idleness_value = (time.time() - last_visited_shared[max_idleness_node]
                                                if last_visited_shared[max_idleness_node] is not None else float('inf'))


                    # 
                    if max_idleness_value > 10:
                        print("Je prends une décision cognitive, Signé agent", agent_id)
                        print("Nœud avec la plus grande oisiveté :", max_idleness_node, "Oisiveté :", max_idleness_value)

                        # Verrouiller le nœud
                        node_locked[max_idleness_node] = True

                        # Trouver l'agent le plus proche de max_idleness_node
                        closest_agent_id = agent_id
                        my_x, my_y = agent_position
                        closest_distance = math.hypot(nodes_position[max_idleness_node][0] - my_x,
                                                    nodes_position[max_idleness_node][1] - my_y)
                        #print("distance,", closest_distance)
                        for other_agent_id in range(num_agents):
                            if other_agent_id != agent_id:
                                other_agent_position = agent_positions[other_agent_id]
                                other_x, other_y = other_agent_position
                                distance_to_max_node = math.hypot(nodes_position[max_idleness_node][0] - other_x,
                                                                nodes_position[max_idleness_node][1] - other_y)
                                if distance_to_max_node < closest_distance:
                                    closest_distance = distance_to_max_node
                                    closest_agent_id = other_agent_id
                        #print("agent plus proche", closest_agent_id)
                        #print("distance,", closest_distance)

                        # Si un agent est plus proche
                        if closest_agent_id != agent_id:
                            if not shared_list_chemins[closest_agent_id]:
                                with lock:
                                    print(f"Agent {agent_id} transfère le chemin à l'agent {closest_agent_id}")
                                    transferttt = shortest_path(adjacency_list, shared_list_next_node[closest_agent_id], max_idleness_node)
                                    print("chemin que je transfere",transferttt)
                                    shared_list_chemins[closest_agent_id] = transferttt
                            else:
                                print("jsuis deja occupé akhy")
                        else:
                            # Calculer le chemin le plus court vers ce nœud
                            monchemin = shortest_path(adjacency_list, agent_node_index, max_idleness_node)
                            print(" Je garde. Voici mon chemin ", monchemin)
                            with lock:
                                shared_list_chemins[agent_id] = monchemin

            if shared_list_chemins[agent_id]:
                # Suivre le chemin calculé
                shared_list_chemins_local = list(shared_list_chemins[agent_id]) # Crée une copie locale
                next_node_index = shared_list_chemins_local[0]
                shared_list_chemins_local.pop(0)
                if not shared_list_chemins_local:
                    shared_list_chemins_local = None
                shared_list_chemins[agent_id] = shared_list_chemins_local  # Réécrit dans le ListProxy
            else:
                # Logique normale : choisir parmi les voisins
                voisins = adjacency_list[agent_node_index]
                random.shuffle(voisins)
                next_node_index = min(
                    voisins,
                    key=lambda x: last_visited_shared[x] if last_visited_shared[x] is not None else -float('inf')
                )
                with lock:
                    if next_node_index in shared_list_next_node and len(voisins) > 1:
                        voisins.remove(next_node_index)
                        next_node_index = min(
                            voisins,
                            key=lambda x: last_visited_shared[x] if last_visited_shared[x] is not None else -float('inf')
                        )

            # Mise à jour de la nouvelle cible
            with lock:
                    shared_list_next_node[agent_id] = next_node_index

            agent_target_position = nodes_position[next_node_index]
            print(f"AGENT {agent_id}, Je suis actuellement au noeud {agent_node_index}, Mon chemin pour y aller : {shared_list_next_node[agent_id]}")

        else:
            # Mouvement vers la cible
            angle = math.atan2(dy, dx)
            agent_position = (x1 + agent_speed * math.cos(angle), y1 + agent_speed * math.sin(angle))

        # Envoyer la position actuelle au processus principal
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
    shared_list_chemins = manager.list([None] * num_agents)
    lock = multiprocessing.Lock()  # Lock to avoid concurrent writes

    # Création des files de communication et des processus pour chaque agent
    position_queues = []
    agents = []
    initial_node = nodes_position[1]
    initial_target_node = nodes_position[2]
    agent_positions = manager.list([initial_node] * num_agents)
    node_locked = manager.dict({i: False for i in range(len(nodes_position))})
    stop_simulation = manager.Value('b', False)  # 'b' pour booléen

    for i in range(num_agents):
        position_queue = multiprocessing.Queue()
        position_queues.append(position_queue)
        agent = multiprocessing.Process(target=agent_process, args=(i, position_queue, last_visited_shared, shared_list_next_node, lock,agent_positions,shared_list_chemins,node_locked,stop_simulation))
        agents.append(agent)
        agent.start()

    running = True
    start_time = time.time()
    total_idleness = 0
    total_seconds = 0  # Compter le nombre de secondes écoulées
    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
            running = False
            stop_simulation.value = True
            print(node_locked)
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