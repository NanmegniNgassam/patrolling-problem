import pygame
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pygame
import numpy as np
from config import maps
from algos.algoaco import generate_path
from algos.algoacoclustering import generate_path_cluster_monobase, generate_path_cluster_multibase

# Constantes utilisées pour l'affichage
WIDTH, HEIGHT = 750, 520
NODE_RADIUS = 10
EDGE_COLOR = (200, 200, 200)
IDLE_COLOR = (255, 0, 0)  # Rouge pour les nœuds inactifs
AGENT_COLOR = (255, 0, 0)  # Couleur de l'agent
AGENT_RADIUS = 5
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (100, 149, 237)

RANDOM_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 - 20,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
RUNTIME_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 + 60,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
CHEMIN_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 + 140,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
MULTIBASE_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 - 100,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)

# Boutons pour le choix du nombre d'agents (au milieu à droite)
button_width, button_height = 40, 40
center_right_x = WIDTH - 150  # Décalage du bord droit
center_y_button = HEIGHT // 2

MINUS_BUTTON = pygame.Rect(center_right_x - button_width - 20, center_y_button - 25, button_width, button_height)
PLUS_BUTTON = pygame.Rect(center_right_x + 20, center_y_button - 25, button_width, button_height)

MINUS_BUTTON_LOOP = pygame.Rect(center_right_x - button_width - 20, center_y_button - 10, button_width, button_height)
PLUS_BUTTON_LOOP = pygame.Rect(center_right_x + 20, center_y_button - 10, button_width, button_height)


def scaling_nodes_position(nodes_position):
# Calculer les dimensions de la carte d'origine
    min_x = min(node[0] for node in nodes_position)
    max_x = max(node[0] for node in nodes_position)
    min_y = min(node[1] for node in nodes_position)
    max_y = max(node[1] for node in nodes_position)

    map_width = max_x - min_x
    map_height = max_y - min_y

    # Calculer le facteur d'échelle pour ajuster la carte à la fenêtre
    scale_factor = min(WIDTH / map_width, HEIGHT / map_height) * 0.9  # Ajustement à 90% pour éviter le dépassement

    # Calculer les offsets pour centrer la carte après mise à l'échelle
    offset_x = (WIDTH - map_width * scale_factor) / 2
    offset_y = (HEIGHT - map_height * scale_factor) / 2

    # Appliquer les offsets et la mise à l'échelle aux positions des nœuds
    nodes_position = [
        ((x - min_x) * scale_factor + offset_x,
        (y - min_y) * scale_factor + offset_y)
        for x, y in nodes_position
    ]
    return nodes_position

def display_menu(screen):
    # Nombre d'agents (initialement 3)
    num_agents = 3
    num_loop = 5

    # Charger l'image de fond
    try:
        #background = pygame.image.load("patrolling-problem\\Patroll\\image1.jpg")
        background = pygame.image.load("image1.jpg")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image : {e}")

    # Définir les polices
    font_title = pygame.font.Font(None, 50)
    font_button = pygame.font.Font(None, 40)
    font_label = pygame.font.Font(None, 35)
    font_dropdown = pygame.font.Font(None, 30)
    font_waiting = pygame.font.Font(None, 50)

    # Options des cartes
    listmap = list(maps.keys())
    dropdown_open = False
    selected_map_index = 0
    # Options pour la météo
    weather_options = ["Soleil", "Pluie"]
    selected_weather_index = 0

    running = True
    chemins = None  # Variable pour stocker les chemins générés
    while running:
        # Effacer l'écran et afficher l'arrière-plan
        screen.fill(WHITE)
        screen.blit(background, (0, 0))

        # Titre
        title = font_title.render("Choisissez une carte et un algorithme :", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title, title_rect)

        # Boutons pour les algorithmes
        pygame.draw.rect(screen, LIGHT_BLUE, RANDOM_BUTTON)
        pygame.draw.rect(screen, LIGHT_BLUE, RUNTIME_BUTTON)
        pygame.draw.rect(screen, LIGHT_BLUE, CHEMIN_BUTTON)
        pygame.draw.rect(screen, LIGHT_BLUE, MULTIBASE_BUTTON)

        # Texte des boutons pour les algorithmes
        random_text = font_button.render("Random", True, BLACK)
        runtime_text = font_button.render("Runtime", True, BLACK)
        chemin_text = font_button.render("Multi-ACO", True, BLACK)
        multibase_text = font_button.render("Multibase", True, BLACK)

        # Positionnement du texte pour les algorithmes
        screen.blit(random_text, random_text.get_rect(center=RANDOM_BUTTON.center))
        screen.blit(runtime_text, runtime_text.get_rect(center=RUNTIME_BUTTON.center))
        screen.blit(chemin_text, chemin_text.get_rect(center=CHEMIN_BUTTON.center))
        screen.blit(multibase_text, multibase_text.get_rect(center=MULTIBASE_BUTTON.center))

        # Section choix du nombre d'agents (ajustée vers le haut)
        label_text = font_label.render("Nombre d'agents", True, BLACK)
        label_rect = label_text.get_rect(center=(150, HEIGHT // 2 - 30))  # Remonté de 5 pixels
        screen.blit(label_text, label_rect)

        agents_text = font_label.render(f"{num_agents}", True, BLACK)
        agents_rect = agents_text.get_rect(center=(150, HEIGHT // 2 + 5))  # Inchangé
        screen.blit(agents_text, agents_rect)

        # Section choix du nombre d'agents (ajustée vers le haut)
        label_text_loops = font_label.render("Nombre de patrouille", True, BLACK)
        label_rect_loops = label_text_loops.get_rect(center=(150, HEIGHT // 2 - 140))  # Remonté pour être bien au-dessus
        screen.blit(label_text_loops, label_rect_loops)

        loops_text = font_label.render(f"{num_loop}", True, BLACK)
        loops_rect = loops_text.get_rect(center=(150, HEIGHT // 2 - 100))  # Position pour aligner avec les boutons
        screen.blit(loops_text, loops_rect)

        # Boutons + et - (remontés de 10 pixels)
        minus_button_rect = pygame.Rect(90, HEIGHT // 2 - 15, 40, 40)  # Bouton "-" ajusté
        plus_button_rect = pygame.Rect(170, HEIGHT // 2 - 15, 40, 40)  # Bouton "+" ajusté

        # Boutons + et - (remontés de 10 pixels)
        minus_button_loop = pygame.Rect(90, HEIGHT // 2 - 120, 40, 40)  # Bouton "-" ajusté
        plus_button_loop = pygame.Rect(170, HEIGHT // 2 - 120, 40, 40)  # Bouton "+" ajusté

        pygame.draw.rect(screen, DARK_BLUE, minus_button_rect)
        pygame.draw.rect(screen, DARK_BLUE, plus_button_rect)

        pygame.draw.rect(screen, DARK_BLUE, minus_button_loop)
        pygame.draw.rect(screen, DARK_BLUE, plus_button_loop)

        # Texte des boutons
        minus_text = font_button.render("-", True, WHITE)
        plus_text = font_button.render("+", True, WHITE)

        screen.blit(minus_text, minus_text.get_rect(center=minus_button_rect.center))
        screen.blit(plus_text, plus_text.get_rect(center=plus_button_rect.center))

        screen.blit(minus_text, minus_text.get_rect(center=minus_button_loop.center))
        screen.blit(plus_text, plus_text.get_rect(center=plus_button_loop.center))
        # Menu déroulant map (placé à droite)
        dropdown_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 45, 200, 40)  # Nouvelle position à droite
        pygame.draw.rect(screen, LIGHT_BLUE, dropdown_rect)
        selected_map_text = font_dropdown.render(listmap[selected_map_index], True, BLACK)
        screen.blit(selected_map_text, selected_map_text.get_rect(center=dropdown_rect.center))

        # Menu déroulant pour la météo
        weather_rect = pygame.Rect(WIDTH - 700, HEIGHT // 2 + 115, 200, 40)
        pygame.draw.rect(screen, LIGHT_BLUE, weather_rect)
        selected_weather_text = font_dropdown.render(weather_options[selected_weather_index], True, BLACK)
        screen.blit(selected_weather_text, selected_weather_text.get_rect(center=weather_rect.center))

        if dropdown_open:
            for i, map_name in enumerate(listmap):
                option_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 45 + i * 40, 200, 40)  # Alignement des options à droite
                pygame.draw.rect(screen, DARK_BLUE if i == selected_map_index else LIGHT_BLUE, option_rect)
                option_text = font_dropdown.render(map_name, True, BLACK)
                screen.blit(option_text, option_text.get_rect(center=option_rect.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None, None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if weather_rect.collidepoint(mouse_pos):
                    selected_weather_index = (selected_weather_index + 1) % len(weather_options)

                if dropdown_rect.collidepoint(mouse_pos):
                    dropdown_open = not dropdown_open
                elif dropdown_open:
                    for i, map_name in enumerate(listmap):
                        option_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 45 + i * 40, 200, 40)
                        if option_rect.collidepoint(mouse_pos):
                            selected_map_index = i
                            dropdown_open = False
                            break

                elif RANDOM_BUTTON.collidepoint(mouse_pos):
                    return listmap[selected_map_index], "Random", num_agents, None, weather_options[selected_weather_index]
                elif RUNTIME_BUTTON.collidepoint(mouse_pos):
                    return listmap[selected_map_index], "Runtime", num_agents, None, weather_options[selected_weather_index]
                elif CHEMIN_BUTTON.collidepoint(mouse_pos):
                    # Afficher un écran d'attente
                    screen.fill(WHITE)
                    waiting_text = font_waiting.render("Génération des chemins, veuillez patienter...", True, BLACK)
                    waiting_rect = waiting_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(waiting_text, waiting_rect)
                    pygame.display.flip()

                    # Générer les chemins
                    nodes_position = scaling_nodes_position(maps[listmap[selected_map_index]]["nodes"])
                    edges = maps[listmap[selected_map_index]]["edges"]
                    if num_agents ==1:
                        chemins = generate_path(num_agents, nodes_position, edges)
                    else:
                        chemins = generate_path_cluster_monobase(num_agents,nodes_position,edges,num_loop)
                        print("Les agents vont effectuer ce nombre de rond avant de rentrer à la caserne:", num_loop)

                    return listmap[selected_map_index], "ACO", num_agents, chemins, weather_options[selected_weather_index]
                
                elif MULTIBASE_BUTTON.collidepoint(mouse_pos):
                    # Afficher un écran d'attente
                    screen.fill(WHITE)
                    waiting_text = font_waiting.render("Génération des chemins, veuillez patienter...", True, BLACK)
                    waiting_rect = waiting_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(waiting_text, waiting_rect)
                    pygame.display.flip()

                    # Générer les chemins
                    nodes_position = scaling_nodes_position(maps[listmap[selected_map_index]]["nodes"])
                    edges = maps[listmap[selected_map_index]]["edges"]
                    chemins = generate_path_cluster_multibase(num_agents,nodes_position,edges)

                    return listmap[selected_map_index], "Multibase", num_agents, chemins, weather_options[selected_weather_index]

                elif minus_button_rect.collidepoint(mouse_pos) and num_agents > 1:
                    num_agents -= 1
                elif plus_button_rect.collidepoint(mouse_pos) and num_agents < 5:
                    num_agents += 1
                elif minus_button_loop.collidepoint(mouse_pos) and num_loop > 2:
                    num_loop -= 1
                elif plus_button_loop.collidepoint(mouse_pos) and num_loop < 10:
                    num_loop += 1



def display_graph(screen, FONT, nodes_position, edges, last_visited_shared,num_agents,position_queues,agent_positions):
    
    screen.fill((255, 255, 255))

    # Dessiner les arêtes
    for edge in edges:
        pygame.draw.line(screen, EDGE_COLOR, nodes_position[edge[0]], nodes_position[edge[1]], 2)

    # Dessiner les nœuds et leurs indices
    for i, node in enumerate(nodes_position):
        node_color = calculate_node_color(last_visited_shared[i])
        pygame.draw.circle(screen, node_color, node, NODE_RADIUS)

        # Dessiner l'indice du nœud
        text_surface = FONT.render(str(i), True, (0, 0, 0))  # Texte en noir
        text_x = node[0] - text_surface.get_width() / 2
        text_y = node[1] - text_surface.get_height() / 2
        screen.blit(text_surface, (text_x, text_y))
    
    average_idleness = calculate_average_idleness(last_visited_shared)
    # Afficher l'oisiveté moyenne
    idle_text = f"Oisiveté moyenne : {average_idleness:.2f}"
    idle_surface = FONT.render(idle_text, True, (0, 0, 0))  # Texte en noir
    screen.blit(idle_surface, (10, 10))  # Affiche le texte en haut à gauche
    #Récupérer et dessiner chaque agent
    for i in range(num_agents):
        if not position_queues[i].empty():
            agent_positions[i] = position_queues[i].get()

        pygame.draw.circle(screen, AGENT_COLOR, (int(agent_positions[i][0]), int(agent_positions[i][1])), AGENT_RADIUS)



def display_graph_on_pygame(screen, idleness_data):

    # Dimensions du graphique
    graph_width = int(WIDTH * 0.75) 
    graph_height = int(HEIGHT * 0.75)  

    # Créer le graphique Matplotlib
    fig, ax = plt.subplots(figsize=(graph_width / 100, graph_height / 100))  # Taille en pouces (DPI = 100)
    time_axis = [i / 30 for i in range(len(idleness_data))]  # Axe des temps en secondes
    ax.plot(time_axis, idleness_data, label="Idleness over time", color="blue")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Average Idleness")
    ax.set_title("Average Idleness vs. Time")
    ax.set_xlim(0, 40)
    ax.legend()
    ax.grid()

    # Convertir le graphique en surface pour Pygame
    canvas = FigureCanvas(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = np.frombuffer(renderer.buffer_rgba(), dtype=np.uint8)
    width, height = fig.get_size_inches() * fig.get_dpi()
    surface = pygame.image.frombuffer(raw_data, (int(width), int(height)), "RGBA")

    # Calculer les positions pour centrer le graphique, avec un décalage vers le haut
    x_pos = (WIDTH - graph_width) // 2
    y_pos = (HEIGHT - graph_height) // 2 + 0 # Décalage ajusté pour monter le graphique

    # Afficher le graphique dans Pygame
    screen.blit(surface, (x_pos, y_pos))  # Position centrée
    plt.close(fig)  # Fermer la figure pour libérer des ressources


def end_simulation(screen, FONT, final_average_idleness, agents, idleness_data):
    """
    Affiche la fin de la simulation avec le graphique et l'oisiveté moyenne.
    :param screen: Surface Pygame
    :param FONT: Police pour le texte
    :param final_average_idleness: Oisiveté moyenne finale
    :param agents: Liste des processus des agents
    :param idleness_data: Données d'oisiveté
    """
    screen.fill((255, 255, 255))  # Fond blanc

    # Police agrandie pour "Oisiveté moyenne"
    large_font = pygame.font.Font(None, 40)  # Taille ajustée

    # Afficher "Oisiveté moyenne" en haut, au milieu
    idle_text = f"Oisiveté moyenne : {final_average_idleness:.2f}"
    idle_surface = large_font.render(idle_text, True, (0, 0, 0))  # Texte en noir
    screen.blit(idle_surface, (WIDTH // 2 - idle_surface.get_width() // 2, 10))  # Position en haut au milieu

    # Dessiner un bouton "Quitter" en bas de l'écran
    quit_button_rect = pygame.Rect(WIDTH - 100, HEIGHT - 40, 80, 30)
    pygame.draw.rect(screen, (0, 0, 255), quit_button_rect)  # Bouton bleu
    quit_text = FONT.render("Quitter", True, (255, 255, 255))
    screen.blit(quit_text, (WIDTH - 95, HEIGHT - 30))

    # Afficher le graphique d'oisiveté
    display_graph_on_pygame(screen, idleness_data)

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

def calculate_node_color(last_visit_time):
    if last_visit_time is None:
        # Nœud jamais visité, il reste rouge
        return IDLE_COLOR

    elapsed_time = time.time() - last_visit_time
    # Interpole entre vert et rouge en fonction du temps depuis la dernière visite
    red_intensity = min(255, int(255 * elapsed_time / 20))  # 20 secondes pour atteindre le rouge complet
    green_intensity = max(0, 255 - red_intensity)
    return (red_intensity, green_intensity, 0)

def calculate_average_idleness(last_visited):
    total_idleness = 0
    node_count = 0

    current_time = time.time()

    for node, last_visit_time in last_visited.items():
        if last_visit_time is not None:
            total_idleness += current_time - last_visit_time
        else:
            # Si un nœud n'a jamais été visité, on peut définir une valeur par défaut (par exemple, 0 ou un grand nombre)
            total_idleness += 20  # Exemple : Oisiveté maximale par défaut
        node_count += 1

    return total_idleness / node_count if node_count > 0 else 0