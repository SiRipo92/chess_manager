def display_main_menu() -> str:
    """
    Main Menu Display
    """
    print("\n---- Menu principal ----")
    print("1. Ajouter un joueur ")
    print("2. Voir la liste des joueurs ")
    print("3. Filtrer / Trier les joueurs ")
    print("4. Quitter ")
    return input("Choix : ")


def display_filter_sort_menu() -> str:
    """
    Menu option for sorting/filtering players
    """
    print("\n-- Filtrage ou tri des joueurs --")
    print("1. Trier par nom (A-Z)")
    print("2. Filtrer par identifiant")
    return input("Votre choix : ")
