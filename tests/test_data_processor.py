"""
Test cases for DataProcessor class.
"""

import pytest
import pandas as pd
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.data_processor import DataProcessor


class TestDataProcessor:
    """Test cases for DataProcessor functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.processor = DataProcessor()
    
    def test_initialization(self):
        """Test DataProcessor initialization."""
        assert self.processor is not None
        assert hasattr(self.processor, 'player_data')
        assert hasattr(self.processor, 'goalkeeper_data')
        assert hasattr(self.processor, 'outfield_data')
    
    def test_detect_position_goalkeeper(self):
        """Test position detection for goalkeepers."""
        # Create sample goalkeeper data
        gk_data = pd.DataFrame({
            'Position': ['GK'],
            'Saves': [10],
            'Conceded goals': [2]
        })
        
        position = self.processor.detect_position(gk_data)
        assert position == 'GK'
    
    def test_detect_position_outfield(self):
        """Test position detection for outfield players."""
        # Create sample outfield data
        outfield_data = pd.DataFrame({
            'Position': ['CF'],
            'Goals': [5],
            'Assists': [3]
        })
        
        position = self.processor.detect_position(outfield_data)
        assert position == 'CF'
    
    def test_calculate_per_90_stats(self):
        """Test per 90 minutes calculation."""
        # Test with valid minutes
        result = self.processor.calculate_per_90_stats(10, 90)
        assert result == 10.0
        
        result = self.processor.calculate_per_90_stats(5, 45)
        assert result == 10.0
        
        # Test with zero minutes
        result = self.processor.calculate_per_90_stats(10, 0)
        assert result == 0.0
    
    def test_clean_numeric_value(self):
        """Test numeric value cleaning."""
        # Test valid numbers
        assert self.processor.clean_numeric_value(10) == 10.0
        assert self.processor.clean_numeric_value("10") == 10.0
        assert self.processor.clean_numeric_value("10.5") == 10.5
        
        # Test invalid values
        assert self.processor.clean_numeric_value(None) == 0.0
        assert self.processor.clean_numeric_value("") == 0.0
        assert self.processor.clean_numeric_value("invalid") == 0.0
    
    def test_calculate_success_rates(self):
        """Test success rate calculations."""
        # Test with valid data
        stats = {
            'passes': 100,
            'passes_accurate': 85,
            'shots': 10,
            'shots_on_target': 6
        }
        
        result = self.processor.calculate_success_rates(stats)
        
        assert 'pass_accuracy' in result
        assert result['pass_accuracy'] == 85.0
        assert 'shot_accuracy' in result
        assert result['shot_accuracy'] == 60.0
    
    def test_filter_by_date_range(self):
        """Test date range filtering."""
        # Create sample data with dates
        data = pd.DataFrame({
            'Date': ['2024-01-01', '2024-06-01', '2024-12-01'],
            'Player': ['A', 'B', 'C'],
            'Goals': [1, 2, 3]
        })
        
        # Convert date column
        data['Date'] = pd.to_datetime(data['Date'])
        
        # Filter data
        filtered = self.processor.filter_by_date_range(
            data, 
            start_date='2024-05-01', 
            end_date='2024-11-01'
        )
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['Player'] == 'B'
    
    def test_filter_by_competition(self):
        """Test competition filtering."""
        # Create sample data
        data = pd.DataFrame({
            'Competition': ['Liga 1', 'Liga 2', 'Liga 1'],
            'Player': ['A', 'B', 'C'],
            'Goals': [1, 2, 3]
        })
        
        # Filter by single competition
        filtered = self.processor.filter_by_competition(data, ['Liga 1'])
        assert len(filtered) == 2
        assert all(filtered['Competition'] == 'Liga 1')
        
        # Filter by multiple competitions
        filtered = self.processor.filter_by_competition(data, ['Liga 1', 'Liga 2'])
        assert len(filtered) == 3


if __name__ == "__main__":
    pytest.main([__file__])
