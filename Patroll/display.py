import pygame
import time
from graphstructure import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pygame
import numpy as np

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

RANDOM_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 - 60,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
RUNTIME_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 + 20,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
CHEMIN_BUTTON = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    (HEIGHT - BUTTON_HEIGHT) // 2 + 100,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)


# Dimensions de la fenêtre
min_x = min(node[0] for node in nodes_position)
max_x = max(node[0] for node in nodes_position)
min_y = min(node[1] for node in nodes_position)
max_y = max(node[1] for node in nodes_position)

# Dimensions de la carte
map_width = max_x - min_x
map_height = max_y - min_y

# Calculer un facteur de mise à l'échelle pour que la carte prenne presque toute la fenêtre
scale_factor = min(WIDTH / map_width, HEIGHT / map_height) * 0.9  # Le *0.9 rend la carte un peu plus petite

# Nouvelle taille de la carte après mise à l'échelle
scaled_map_width = map_width * scale_factor
scaled_map_height = map_height * scale_factor

# Calculer le centre de la carte (en coordonnées locales)
center_x = min_x + map_width / 2
center_y = min_y + map_height / 2

# Calculer le centre de la carte après mise à l'échelle (en pixels)
center_x_scaled = center_x * scale_factor
center_y_scaled = center_y * scale_factor

# Offsets pour centrer la carte dans la fenêtre
offset_x = WIDTH / 2 - center_x_scaled
offset_y = HEIGHT / 2 - center_y_scaled


# Appliquer les offsets et la mise à l'échelle
nodes_position = [(min_x + (x - min_x) * scale_factor + offset_x, 
                   min_y + (y - min_y) * scale_factor + offset_y) 
                  for x, y in nodes_position]

def display_menu(screen,font):
    screen.fill(WHITE)
    num_agents = 1
    
    background = pygame.image.load("Patroll\image0.jpg")  # Remplace par le chemin de ton image
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))

    font_title = pygame.font.Font(None, 50)
    font_button = pygame.font.Font(None, 40)
    # Dessiner le titre centré
    title = font_title.render("Choisissez un algorithme :", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH // 2, 50))
    screen.blit(title, title_rect)

    # Dessiner les boutons
    pygame.draw.rect(screen, LIGHT_BLUE, RANDOM_BUTTON)
    pygame.draw.rect(screen, LIGHT_BLUE, RUNTIME_BUTTON)
    pygame.draw.rect(screen, LIGHT_BLUE, CHEMIN_BUTTON)


    random_text = font_button.render("Random", True, BLACK)
    runtime_text = font_button.render("Runtime", True, BLACK)
    chemin_text = font_button.render("Chemin", True, BLACK)

    # Centrer le texte sur les boutons
    screen.blit(
        random_text,
        random_text.get_rect(center=RANDOM_BUTTON.center),
    )
    screen.blit(
        runtime_text,
        runtime_text.get_rect(center=RUNTIME_BUTTON.center),
    )
    screen.blit(
        chemin_text,
        chemin_text.get_rect(center=CHEMIN_BUTTON.center),
    )
    pygame.display.flip()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if RANDOM_BUTTON.collidepoint(mouse_pos):
                    return "Random"
                elif RUNTIME_BUTTON.collidepoint(mouse_pos):
                    return "Runtime"
                elif CHEMIN_BUTTON.collidepoint(mouse_pos):
                    return "Chemin"


def calculate_node_color(last_visit_time):
    if last_visit_time is None:
        # Nœud jamais visité, il reste rouge
        return IDLE_COLOR

    elapsed_time = time.time() - last_visit_time
    # Interpole entre vert et rouge en fonction du temps depuis la dernière visite
    red_intensity = min(255, int(255 * elapsed_time / 20))  # 20 secondes pour atteindre le rouge complet
    green_intensity = max(0, 255 - red_intensity)
    return (red_intensity, green_intensity, 0)

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


