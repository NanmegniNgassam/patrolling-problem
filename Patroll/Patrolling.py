
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
    chemins.append((0, 4, 2, 5, 32, 34, 35, 33, 35, 19, 15, 18, 14, 16, 17, 20, 38, 36, 37, 39, 27, 23, 25, 24, 22, 26, 21, 26, 42, 40, 41, 43, 41, 12, 10, 8, 7, 11, 9, 13, 29, 31, 30, 28, 6, 1, 3, 44, 48, 47, 49, 45, 44, 46, 44, 3, 1, 0))
    chemins.append((0, 4, 1, 6, 28, 30, 31, 29, 13, 7, 8, 10, 11, 9, 12, 41, 43, 42, 40, 42, 26, 21, 25, 22, 24, 23, 27, 39, 37, 36, 38, 20, 17, 18, 16, 14, 19, 15, 19, 35, 33, 32, 34, 32, 5, 3, 44, 46, 48, 45, 49, 47, 46, 44, 3, 5, 2, 0))
    chemins.append((0, 4, 3, 6, 1, 6, 28, 30, 31, 29, 13, 7, 11, 8, 10, 12, 9, 12, 41, 43, 42, 40, 42, 26, 21, 49, 45, 48, 46, 44, 46, 47, 49, 21, 22, 24, 22, 25, 23, 27, 
    39, 37, 36, 38, 20, 17, 18, 16, 14, 19, 15, 19, 35, 33, 32, 34, 32, 5, 2, 0))

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
            agent = multiprocessing.Process(target=agent_process_astar, args=(i, position_queue, last_visited_shared, shared_list_next_node, lock))
        elif algorithm == "Runtime":
            agent = multiprocessing.Process(target=agent_process, args=(i, position_queue, last_visited_shared, shared_list_next_node, lock,agent_positions,shared_list_chemins,node_locked,stop_simulation))
        elif algorithm == "Chemin":
            agent = multiprocessing.Process(target=agent_process_chemins, args=(i, position_queue, chemins[i], last_visited_shared))
        agents.append(agent)    
        agent.start()

    running = True
    start_time = time.time()
    total_idleness = 0
    total_took = 0
    idleness_data = []
    
    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 30:
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
        total_took += 1  # Incrémenter le nombre de prise d'info
    
    final_average_idleness = total_idleness / total_took if total_took > 0 else 0
    end_simulation(screen, FONT, final_average_idleness,agents,idleness_data)
