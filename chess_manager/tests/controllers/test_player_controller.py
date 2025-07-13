import unittest
import os
from chess_manager.controllers.player_controller import PlayerController


class TestPlayerController(unittest.TestCase):

    def setUp(self):
        """Initialise un contrôleur avec un faux chemin de fichier."""
        self.test_filepath = "chess_manager/tests/reports/test_players.json"
        self.controller = PlayerController(self.test_filepath)
        # Nettoie avant chaque test
        if os.path.exists(self.test_filepath):
            os.remove(self.test_filepath)

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


if __name__ == "__main__":
    unittest.main()
