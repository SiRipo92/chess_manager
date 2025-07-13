import unittest
from unittest.mock import patch
from chess_manager.views.player_views import (
    prompt_new_player,
    confirm_player_added,
    display_error_message,
    display_all_players,
    prompt_sort_or_filter,
    prompt_id_filter,
    prompt_player_id_for_stats,
    display_player_stats
)
from chess_manager.models.player import Player


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

    @patch("builtins.print")
    def test_display_all_players_empty(self, mock_print):
        display_all_players([])
        mock_print.assert_called_with("Aucun joueur enregistré.")

    @patch("builtins.print")
    def test_display_all_players_list(self, mock_print):
        player = Player("Durand", "Alice", "1995-04-10", "AB12345")
        player.date_enrolled = "2023-01-01"
        display_all_players([player])
        self.assertTrue(any("DURAND" in call.args[0] for call in mock_print.call_args_list))

    @patch("builtins.input", return_value="2")
    def test_prompt_sort_or_filter(self, mock_input):
        result = prompt_sort_or_filter()
        self.assertEqual(result, "2")

    @patch("builtins.input", return_value="CD123")
    def test_prompt_id_filter(self, mock_input):
        result = prompt_id_filter()
        self.assertEqual(result, "CD123")

    @patch("builtins.input", return_value="AB12345")
    def test_prompt_player_id_for_stats(self, mock_input):
        result = prompt_player_id_for_stats()
        self.assertEqual(result, "AB12345")

    @patch("builtins.print")
    def test_display_player_stats(self, mock_print):
        display_player_stats("5 victoires, 2 défaites")
        mock_print.assert_called_with("\n📊 Statistiques du joueur :\n5 victoires, 2 défaites")


if __name__ == "__main__":
    unittest.main()
