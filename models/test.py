def remove_element_by_index(lst, index):
    try:
        # Supprime l'élément à l'indice spécifié et le renvoie
        lst.pop(index)
    except IndexError:
        # Gère le cas où l'indice est en dehors de la plage de la liste
        return "IndexError: L'indice spécifié est en dehors de la plage."

# Exemple d'utilisation
my_list = [10, 20, 30, 40, 3]
remove_element_by_index(my_list, 3)
print("Liste après suppression :", my_list)
