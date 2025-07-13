import unittest
import os
import json
import tempfile
from datetime import datetime
from chess_manager.models.player import Player

class TestPlayer(unittest.TestCase):
    """Unit tests for the Player model."""

    def setUp(self):
        """Set up a sample Player object before each test."""
        self.player = Player("Doe", "John", "1990-01-01", "AB12345")

    def test_player_initialization(self):
        """Test that a Player is initialized with correct attributes."""
        self.assertEqual(self.player.last_name, "Doe")
        self.assertEqual(self.player.first_name, "John")
        self.assertEqual(self.player.birthdate, "1990-01-01")
        self.assertEqual(self.player.national_id, "AB12345")

        # Check date_enrolled is today
        today_str = datetime.today().strftime("%Y-%m-%d")
        self.assertEqual(self.player.date_enrolled, today_str)

    def test_player_age_property(self):
        """Test that the age property calculates the correct age."""
        expected_age = datetime.today().year - 1990 - (
            (datetime.today().month, datetime.today().day) < (1, 1)
        )
        self.assertEqual(self.player.age, expected_age)

    def test_to_dict(self):
        """Test conversion of Player object to dictionary."""
        player_dict = self.player.to_dict()
        self.assertEqual(player_dict["last_name"], "Doe")
        self.assertEqual(player_dict["first_name"], "John")
        self.assertEqual(player_dict["birthdate"], "1990-01-01")
        self.assertEqual(player_dict["national_id"], "AB12345")
        self.assertEqual(player_dict["date_enrolled"], self.player.date_enrolled)

    def test_from_dict(self):
        """Test reconstruction of Player object from dictionary."""
        data = {
            "last_name": "Smith",
            "first_name": "Alice",
            "birthdate": "1995-05-15",
            "national_id": "XY98765",
            "date_enrolled": "2024-01-01"
        }
        new_player = Player.from_dict(data)
        self.assertEqual(new_player.last_name, "Smith")
        self.assertEqual(new_player.first_name, "Alice")
        self.assertEqual(new_player.birthdate, "1995-05-15")
        self.assertEqual(new_player.national_id, "XY98765")
        self.assertEqual(new_player.date_enrolled, "2024-01-01")

    def test_save_and_load_player(self):
        """Test saving a player to JSON and loading it back."""
        # Use a temporary file to avoid writing to real filesystem
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            temp_path = tmp.name

        try:
            # Save this player to file
            self.player.save_to_file(temp_path)

            # Now load all players from that same file
            players = Player.load_all_players(temp_path)

            self.assertEqual(len(players), 1)
            loaded_player = players[0]
            self.assertEqual(loaded_player.last_name, self.player.last_name)
            self.assertEqual(loaded_player.first_name, self.player.first_name)
            self.assertEqual(loaded_player.birthdate, self.player.birthdate)
            self.assertEqual(loaded_player.national_id, self.player.national_id)
            self.assertEqual(loaded_player.date_enrolled, self.player.date_enrolled)
        finally:
            os.remove(temp_path)  # clean up

    def test_load_all_players_missing_file(self):
        """Test loading players from a nonexistent file returns an empty list."""
        fake_path = "nonexistent_players.json"
        with self.assertRaises(FileNotFoundError):
            Player.load_all_players(fake_path)

if __name__ == "__main__":
    unittest.main()
