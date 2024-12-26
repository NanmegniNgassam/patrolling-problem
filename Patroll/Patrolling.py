
import pygame
import multiprocessing
import time
from graphstructure import *  # Assurez-vous que nodes et edges sont définis dans graphstructure
from collections import deque  # Pour BFS
from display import *
from algos.algorandom import *
from algos.algoruntime import *
from algos.algochemin import *
import pygame


if __name__ == '__main__':
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
    chemins = []
    chemins.append((0, 2, 5, 3, 4, 1, 6, 28, 30, 31, 29, 13, 9, 11, 7, 8, 10, 12, 41, 43, 42, 40, 42, 26, 21, 22, 24, 25, 23, 27, 39, 37, 36, 38, 20, 15, 19, 14, 18, 17, 
    16, 18, 15, 19, 35, 33, 32, 34, 35, 33, 32, 34, 32, 5, 3, 44, 46, 48, 47, 49, 45, 49, 45, 49, 45, 48, 44, 3, 6, 1, 6, 1, 3, 6, 3, 1, 4, 0))
    chemins.append((0, 7, 8, 9, 20, 19, 26, 33, 34, 27, 35, 38, 39, 43, 45, 46, 48, 47, 44, 39, 40, 41, 37, 31, 29, 23, 18, 15, 12, 11, 4, 5, 6, 13, 16, 24, 25, 32, 42, 49, 41, 
    36, 22, 28, 30, 28, 22, 21, 17, 10, 14, 17, 9, 3, 2, 1, 0))
    chemins.append((0, 1, 2, 3, 10, 17, 21, 22, 28, 30, 29, 31, 36, 37, 41, 49, 42, 32, 25, 24, 16, 13, 6, 5, 4, 11, 12, 15, 18, 23, 18, 14, 10, 9, 20, 27, 35, 38, 34, 39, 43, 45, 46, 40, 46, 48, 47, 44, 33, 26, 19, 7, 8, 1, 8, 7, 0))



    # Initialisation de pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Agent - Graph Simulation")
    clock = pygame.time.Clock()
    font_size = 12  # Taille de la police
    FONT = pygame.font.Font(None, font_size)  # Charger la police par défaut

    algorithm = display_menu(screen,FONT)

    for i in range(num_agents):
        position_queue = multiprocessing.Queue()
        position_queues.append(position_queue)
        if algorithm == "Random":
            agent = multiprocessing.Process(target=agent_process_BFS, args=(i, position_queue, last_visited_shared, shared_list_next_node, lock))
        elif algorithm == "Runtime":
            agent = multiprocessing.Process(target=agent_process, args=(i, position_queue, last_visited_shared, shared_list_next_node, lock,agent_positions,shared_list_chemins,node_locked,stop_simulation))
        elif algorithm == "Chemin":
            agent = multiprocessing.Process(target=agent_process_chemins, args=(i, position_queue, chemins[i], last_visited_shared))
        agents.append(agent)
        agent.start()
    running = True
    start_time = time.time()
    total_idleness = 0
    total_seconds = 0

    idleness_data = []
    
    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 40:
            running = False
            stop_simulation.value = True
        display_graph(screen, FONT,nodes_position, edges, last_visited_shared,num_agents,position_queues,agent_positions)
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        clock.tick(FPS)

        # Calculer l'oisiveté moyenne pendant la simulation
        current_idleness = calculate_average_idleness(last_visited_shared)
        idleness_data.append(current_idleness)
        total_idleness += current_idleness  # Ajouter l'oisiveté du moment
        total_seconds += 1  # Incrémenter le nombre de secondes
    
    final_average_idleness = total_idleness / total_seconds if total_seconds > 0 else 0
    end_simulation(screen, FONT, final_average_idleness,agents,idleness_data)
