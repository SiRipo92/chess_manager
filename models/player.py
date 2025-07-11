from datetime import datetime

class Player:
    """
    Représente un joueur d'échecs dans le système.

    Attributs :
        last_name (str) : Nom de famille du joueur.
        first_name (str) : Prénom du joueur.
        birth_date (str) : Date de naissance (format YYYY-MM-DD).
        national_id (str) : Identifiant national unique (ex : AB12345).
        total_points (float) : Nombre total de points cumulés.
        wins (float) : Nombre de victoires (1.0 point par victoire).
        losses (float) : Nombre de défaites (0.0 point).
        draws (float) : Nombre de matchs nuls (0.5 point).
        match_count (int) : Nombre total de matchs joués.
        tournaments_won (int) : Nombre total de tournois gagnés.
        date_enrolled (str) : Date d'inscription (format YYYY-MM-DD)
    """

    def __init__( self, last_name, first_name, birth_date, national_id ) -> None:
        self.last_name = last_name
        self.first_name = first_name
        self.birth_date = birth_date
        self.national_id = national_id

        # Statistiques initialisées à zéro
        self.total_points = 0.0
        self.wins = 0.0
        self.losses = 0.0
        self.draws = 0.0
        self.match_count = 0
        self.tournaments_won = 0
        self.enrollment_date = datetime.now().strftime("%Y-%m-%d")

    @property
    def age(self) -> int:
        """
        Calcule l'âge du joueur à partir de sa date de naissance.
        """
        birth = datetime.strptime(self.birth_date, "%Y-%m-%d")
        today = datetime.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


    def record_match(self, result: str) -> None:
        """
        Met à jour les statistiques du joueur après un match.
        Paramètre :
            result (str) : Résultat du match pour ce joueur ("win", "loss", "draw").
        """
        pass

    # def record_tournament_win()
    # def get_win_ratio()
    # def get_ranking_score()