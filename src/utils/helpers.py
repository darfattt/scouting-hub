"""
Helper utilities for the football scouting application.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any


def get_percentile_color(percentile: float) -> str:
    """
    Get color based on percentile value.
    
    Args:
        percentile: Percentile value (0-100)
        
    Returns:
        Hex color code
    """
    if percentile >= 80:
        return '#1a9641'  # Dark green
    elif percentile >= 60:
        return '#73c378'  # Light green
    elif percentile >= 40:
        return '#f9d057'  # Yellow
    elif percentile >= 20:
        return '#fc8d59'  # Orange
    else:
        return '#d73027'  # Red


def calculate_per_90_stats(value: float, minutes: float) -> float:
    """
    Calculate per 90 minutes statistics.
    
    Args:
        value: Raw statistic value
        minutes: Minutes played
        
    Returns:
        Per 90 minutes value
    """
    if minutes <= 0:
        return 0.0
    return (value / minutes) * 90


def format_player_name(name: str) -> str:
    """
    Format player name for display.
    
    Args:
        name: Raw player name
        
    Returns:
        Formatted player name
    """
    if not name:
        return "Unknown Player"
    
    # Remove extra spaces and capitalize properly
    return ' '.join(word.capitalize() for word in name.strip().split())


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return if division by zero
        
    Returns:
        Division result or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator


def validate_data_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate that DataFrame contains required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if all required columns exist
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0


def clean_numeric_data(value: Any) -> float:
    """
    Clean and convert value to numeric, handling various edge cases.
    
    Args:
        value: Value to clean and convert
        
    Returns:
        Cleaned numeric value
    """
    if pd.isna(value) or value is None:
        return 0.0
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove common non-numeric characters
        cleaned = value.strip().replace(',', '').replace('%', '')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    return 0.0


def get_position_category(position: str) -> str:
    """
    Categorize player position into main groups.
    
    Args:
        position: Player position code
        
    Returns:
        Position category (GK, Defender, Midfielder, Forward)
    """
    if not position:
        return "Unknown"
    
    position = position.upper().strip()
    
    if position in ['GK']:
        return "Goalkeeper"
    elif position in ['CB', 'LB', 'RB', 'LWB', 'RWB', 'SW']:
        return "Defender"
    elif position in ['CM', 'CDM', 'CAM', 'LM', 'RM', 'LWM', 'RWM']:
        return "Midfielder"
    elif position in ['CF', 'LWF', 'RWF', 'ST', 'LF', 'RF']:
        return "Forward"
    else:
        return "Unknown"


def filter_by_minutes(data: Dict[str, Dict], min_minutes: int = 90) -> Dict[str, Dict]:
    """
    Filter player data by minimum minutes played.
    
    Args:
        data: Player data dictionary
        min_minutes: Minimum minutes threshold
        
    Returns:
        Filtered player data
    """
    return {
        player: stats for player, stats in data.items()
        if stats.get('minutes', 0) >= min_minutes
    }


def calculate_success_rate(successful: float, total: float) -> float:
    """
    Calculate success rate percentage.
    
    Args:
        successful: Number of successful attempts
        total: Total number of attempts
        
    Returns:
        Success rate as percentage (0-100)
    """
    return safe_divide(successful, total, 0.0) * 100
