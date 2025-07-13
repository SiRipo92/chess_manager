import unittest
from unittest.mock import patch
from chess_manager.views.player_views import (
    prompt_new_player,
    confirm_player_added,
    display_error_message
)


class TestPlayerViews(unittest.TestCase):

    @patch("builtins.input", side_effect=["Doe", "John", "1990-01-01", "AB12345"])
    def test_prompt_new_player(self, mock_input):
        """Teste que les champs saisis sont bien retournés."""
        result = prompt_new_player()
        self.assertEqual(result, ("Doe", "John", "1990-01-01", "AB12345"))

    @patch("builtins.print")
    def test_confirm_player_added(self, mock_print):
        """Teste le message de confirmation."""
        confirm_player_added()
        mock_print.assert_called_with("✅ Le joueur a bien été ajouté à la base de données.\n")

    @patch("builtins.print")
    def test_display_error_message(self, mock_print):
        """Teste l'affichage du message d’erreur."""
        display_error_message("ID invalide")
        mock_print.assert_called_with("❌ Erreur : ID invalide")


if __name__ == "__main__":
    unittest.main()
