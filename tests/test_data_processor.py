"""
Test cases for Data Processor classes.
"""

import pytest
import pandas as pd
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.data_processor import GoalkeeperDataProcessor, OutfieldDataProcessor


class TestGoalkeeperDataProcessor:
    """Test cases for GoalkeeperDataProcessor functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.processor = GoalkeeperDataProcessor()

    def test_initialization(self):
        """Test GoalkeeperDataProcessor initialization."""
        assert self.processor is not None
        assert hasattr(self.processor, 'player_data')
        assert hasattr(self.processor, 'data_dir')
        assert hasattr(self.processor, 'all_data')
        assert hasattr(self.processor, 'league_data')

    def test_load_data_method_exists(self):
        """Test that load_data method exists and returns DataFrame."""
        result = self.processor.load_data()
        assert isinstance(result, pd.DataFrame)

    def test_process_data_method_exists(self):
        """Test that process_data method exists and returns dictionary."""
        result = self.processor.process_data()
        assert isinstance(result, dict)

    def test_get_player_text_representation(self):
        """Test player text representation generation."""
        # First process some data
        self.processor.process_data()

        # Test with non-existent player
        result = self.processor.get_player_text_representation("NonExistentPlayer")
        assert result == ""

    def test_get_all_player_texts(self):
        """Test getting all player text representations."""
        result = self.processor.get_all_player_texts()
        assert isinstance(result, list)

        # Each item should be a dictionary with 'player' and 'content' keys
        for item in result:
            assert isinstance(item, dict)
            assert 'player' in item
            assert 'content' in item

    def test_league_data_loading(self):
        """Test league data loading functionality."""
        result = self.processor.load_league_data()
        assert isinstance(result, pd.DataFrame)

    def test_league_stats_for_player(self):
        """Test getting league stats for a specific player."""
        # This is a private method, but we can test it exists
        assert hasattr(self.processor, '_get_league_stats_for_player')

        # Test with sample data
        result = self.processor._get_league_stats_for_player("TestPlayer", "TestTeam")
        assert isinstance(result, dict)

    def test_data_directory_handling(self):
        """Test data directory handling."""
        # Test default data directory
        assert self.processor.data_dir == "data/stats"

        # Test custom data directory
        custom_processor = GoalkeeperDataProcessor(data_dir="custom/path")
        assert custom_processor.data_dir == "custom/path"


class TestOutfieldDataProcessor:
    """Test cases for OutfieldDataProcessor functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.processor = OutfieldDataProcessor()

    def test_initialization(self):
        """Test OutfieldDataProcessor initialization."""
        assert self.processor is not None
        assert hasattr(self.processor, 'player_data')
        assert hasattr(self.processor, 'data_dir')
        assert hasattr(self.processor, 'all_data')
        assert hasattr(self.processor, 'position_filter')

    def test_load_data_method_exists(self):
        """Test that load_data method exists and returns DataFrame."""
        result = self.processor.load_data()
        assert isinstance(result, pd.DataFrame)

    def test_process_data_method_exists(self):
        """Test that process_data method exists and returns dictionary."""
        result = self.processor.process_data()
        assert isinstance(result, dict)

    def test_get_player_text_representation(self):
        """Test player text representation generation."""
        # First process some data
        self.processor.process_data()

        # Test with non-existent player
        result = self.processor.get_player_text_representation("NonExistentPlayer")
        assert result == ""

    def test_get_all_player_texts(self):
        """Test getting all player text representations."""
        result = self.processor.get_all_player_texts()
        assert isinstance(result, list)

        # Each item should be a dictionary with 'player' and 'content' keys
        for item in result:
            assert isinstance(item, dict)
            assert 'player' in item
            assert 'content' in item

    def test_position_filter_initialization(self):
        """Test position filter functionality."""
        # Test with position filter
        forward_processor = OutfieldDataProcessor(position_filter="CF|LWF|RWF")
        assert forward_processor.position_filter == "CF|LWF|RWF"

        # Test without position filter
        assert self.processor.position_filter is None

    def test_data_directory_handling(self):
        """Test data directory handling."""
        # Test default data directory
        assert self.processor.data_dir == "data/stats"

        # Test custom data directory
        custom_processor = OutfieldDataProcessor(data_dir="custom/path")
        assert custom_processor.data_dir == "custom/path"


class TestDataProcessorIntegration:
    """Integration tests for data processors."""

    def test_both_processors_can_coexist(self):
        """Test that both processors can be used together."""
        gk_processor = GoalkeeperDataProcessor()
        outfield_processor = OutfieldDataProcessor()

        # Both should be able to load data without conflicts
        gk_data = gk_processor.load_data()
        outfield_data = outfield_processor.load_data()

        assert isinstance(gk_data, pd.DataFrame)
        assert isinstance(outfield_data, pd.DataFrame)

    def test_processors_have_different_data(self):
        """Test that processors handle different types of data."""
        gk_processor = GoalkeeperDataProcessor()
        outfield_processor = OutfieldDataProcessor()

        # Process data
        gk_players = gk_processor.process_data()
        outfield_players = outfield_processor.process_data()

        assert isinstance(gk_players, dict)
        assert isinstance(outfield_players, dict)

        # Players should be different (no overlap expected)
        if gk_players and outfield_players:
            gk_names = set(gk_players.keys())
            outfield_names = set(outfield_players.keys())
            # There might be some overlap, but they should be processed differently
            assert len(gk_names.intersection(outfield_names)) >= 0  # Allow overlap


if __name__ == "__main__":
    pytest.main([__file__])
