import unittest
import os
from chess_manager.controllers.player_controller import PlayerController


class TestPlayerController(unittest.TestCase):

    def setUp(self):
        """Initialise un contrôleur avec un faux chemin de fichier."""
        """Initialise un contrôleur avec un faux chemin de fichier."""
        self.test_filepath = "chess_manager/tests/reports/test_players.json"
        self.controller = PlayerController(self.test_filepath)

        if os.path.exists(self.test_filepath):
            os.remove(self.test_filepath)

        # ✅ Create test data
        from chess_manager.models.player import Player
        self.players = [
            Player("Durand", "Alice", "1990-05-12", "AB12345"),
            Player("Bernard", "Jean", "1988-03-20", "CD67890"),
            Player("Albert", "Claire", "1995-11-03", "EF54321"),
        ]

    def tearDown(self):
        """Nettoie le fichier de test après les tests."""
        if os.path.exists(self.test_filepath):
            os.remove(self.test_filepath)

    def test_valid_id_format(self):
        """Teste des ID valides et invalides."""
        self.assertTrue(self.controller._is_valid_id("AB12345"))
        self.assertFalse(self.controller._is_valid_id("123AB45"))
        self.assertFalse(self.controller._is_valid_id("A123456"))

    def test_add_player_success(self):
        """Teste l’ajout d’un joueur avec un ID unique valide."""
        result = self.controller.add_player("Doe", "Jane", "1990-05-01", "AB12345")
        self.assertTrue(result)
        players = self.controller.load_all_players()
        self.assertEqual(len(players), 1)
        self.assertEqual(players[0].last_name, "Doe")

    def test_add_player_duplicate_id(self):
        """Teste l’échec d’ajout si l’ID existe déjà."""
        self.controller.add_player("Doe", "Jane", "1990-05-01", "AB12345")
        result = self.controller.add_player("Smith", "John", "1992-06-02", "AB12345")
        self.assertFalse(result)

    def test_add_player_invalid_id(self):
        """Teste l’échec d’ajout si l’ID est mal formaté."""
        result = self.controller.add_player("Lee", "Sara", "1989-07-04", "BAD_ID")
        self.assertFalse(result)

    def test_sort_players_by_name(self):
        """Test sorting players by last name and first name in alphabetical order."""
        sorted_players = self.controller.sort_players_by_name(self.players)
        sorted_names = [(p.last_name, p.first_name) for p in sorted_players]
        self.assertEqual(sorted_names, [
            ("Albert", "Claire"),
            ("Bernard", "Jean"),
            ("Durand", "Alice"),
        ])

    def test_filter_players_by_id_partial_match(self):
        """Test filtering players by a partial match in the national ID."""
        filtered = self.controller.filter_players_by_id(self.players, "CD")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].national_id, "CD67890")

    def test_filter_players_by_id_case_insensitive(self):
        """Test filtering players by ID in a case-insensitive manner."""
        filtered = self.controller.filter_players_by_id(self.players, "cd")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].national_id, "CD67890")

    def test_filter_players_by_id_no_match(self):
        """Test that filtering by a non-matching ID returns an empty list."""
        filtered = self.controller.filter_players_by_id(self.players, "ZZ")
        self.assertEqual(filtered, [])

    if __name__ == "__main__":
        unittest.main()
