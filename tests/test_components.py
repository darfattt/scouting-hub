"""
Test cases for UI Components.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
import pandas as pd

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.helpers import (
    get_percentile_color,
    calculate_per_90_stats,
    format_player_name,
    safe_divide,
    validate_data_columns,
    clean_numeric_data,
    get_position_category,
    filter_by_minutes,
    calculate_success_rate
)


class TestHelperFunctions:
    """Test cases for utility helper functions."""
    
    def test_get_percentile_color(self):
        """Test percentile color mapping."""
        assert get_percentile_color(90) == '#1a9641'  # Dark green
        assert get_percentile_color(70) == '#73c378'  # Light green
        assert get_percentile_color(50) == '#f9d057'  # Yellow
        assert get_percentile_color(30) == '#fc8d59'  # Orange
        assert get_percentile_color(10) == '#d73027'  # Red
    
    def test_calculate_per_90_stats(self):
        """Test per 90 minutes calculation."""
        assert calculate_per_90_stats(10, 90) == 10.0
        assert calculate_per_90_stats(5, 45) == 10.0
        assert calculate_per_90_stats(10, 0) == 0.0
    
    def test_format_player_name(self):
        """Test player name formatting."""
        assert format_player_name("john doe") == "John Doe"
        assert format_player_name("  JANE SMITH  ") == "Jane Smith"
        assert format_player_name("") == "Unknown Player"
        assert format_player_name(None) == "Unknown Player"
    
    def test_safe_divide(self):
        """Test safe division function."""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=1.0) == 1.0
    
    def test_validate_data_columns(self):
        """Test DataFrame column validation."""
        df = pd.DataFrame({
            'name': ['A', 'B'],
            'goals': [1, 2],
            'assists': [0, 1]
        })
        
        assert validate_data_columns(df, ['name', 'goals']) == True
        assert validate_data_columns(df, ['name', 'missing_col']) == False
    
    def test_clean_numeric_data(self):
        """Test numeric data cleaning."""
        assert clean_numeric_data(10) == 10.0
        assert clean_numeric_data("10.5") == 10.5
        assert clean_numeric_data("10,5") == 105.0  # Comma removed
        assert clean_numeric_data("10%") == 10.0    # Percent removed
        assert clean_numeric_data(None) == 0.0
        assert clean_numeric_data("invalid") == 0.0
    
    def test_get_position_category(self):
        """Test position categorization."""
        assert get_position_category("GK") == "Goalkeeper"
        assert get_position_category("CB") == "Defender"
        assert get_position_category("CM") == "Midfielder"
        assert get_position_category("CF") == "Forward"
        assert get_position_category("UNKNOWN") == "Unknown"
        assert get_position_category("") == "Unknown"
    
    def test_filter_by_minutes(self):
        """Test minutes filtering."""
        data = {
            'Player A': {'minutes': 100, 'goals': 5},
            'Player B': {'minutes': 50, 'goals': 2},
            'Player C': {'minutes': 120, 'goals': 8}
        }
        
        filtered = filter_by_minutes(data, min_minutes=90)
        assert len(filtered) == 2
        assert 'Player A' in filtered
        assert 'Player C' in filtered
        assert 'Player B' not in filtered
    
    def test_calculate_success_rate(self):
        """Test success rate calculation."""
        assert calculate_success_rate(8, 10) == 80.0
        assert calculate_success_rate(0, 10) == 0.0
        assert calculate_success_rate(10, 0) == 0.0


class TestComponentIntegration:
    """Test cases for component integration."""
    
    @patch('streamlit.selectbox')
    @patch('streamlit.slider')
    def test_component_rendering(self, mock_slider, mock_selectbox):
        """Test component rendering with mocked Streamlit."""
        # Mock Streamlit components
        mock_selectbox.return_value = "Test Option"
        mock_slider.return_value = 90
        
        # Test would involve importing and testing actual components
        # This is a placeholder for component integration tests
        pass


if __name__ == "__main__":
    pytest.main([__file__])
