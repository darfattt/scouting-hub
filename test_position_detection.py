#!/usr/bin/env python3
"""
Test Position Detection
Quick test to see if the position detection is working correctly.
"""

import pandas as pd
import os

def test_position_detection():
    """Test position detection with actual data files."""
    print("Testing position detection with actual data...")
    
    # Test with Alex Martins (forward)
    forward_file = "data/stats/Player stats Alex Martins.csv"
    if os.path.exists(forward_file):
        print(f"\nTesting forward file: {forward_file}")
        df = pd.read_csv(forward_file)
        print(f"Columns: {list(df.columns)}")
        print(f"Positions: {df['Position'].unique()}")
        
        # Test forward detection
        forward_codes = ['CF', 'RWF', 'LWF', 'LAMF', 'RAMF', 'AMF', 'SS', 'LW', 'RW']
        has_forwards = any(any(code in pos for code in forward_codes) for pos in df['Position'].fillna(''))
        print(f"Forward detected: {has_forwards}")
    
    # Test with goalkeeper file
    gk_file = "data/stats/PERSIB - Teja Paku Alam (Stats).csv"
    if os.path.exists(gk_file):
        print(f"\nTesting goalkeeper file: {gk_file}")
        df = pd.read_csv(gk_file)
        print(f"Columns: {list(df.columns)}")
        
        # Check for goalkeeper columns
        goalkeeper_columns = ['Saves', 'Conceded goals', 'Shots against']
        is_goalkeeper_data = all(col in df.columns for col in goalkeeper_columns)
        print(f"Goalkeeper detected: {is_goalkeeper_data}")
    
    # Test OutfieldDataProcessor
    print(f"\nTesting OutfieldDataProcessor...")
    try:
        from data_processor import OutfieldDataProcessor
        
        # Test forward processor
        forward_processor = OutfieldDataProcessor(position_filter="CF|RWF|LWF|LAMF|RAMF|AMF|SS|LW|RW")
        forward_data = forward_processor.load_data()
        print(f"Forward processor loaded: {len(forward_data) if forward_data is not None else 0} rows")
        
        if forward_data is not None and not forward_data.empty:
            print(f"Forward players found: {forward_data['Player'].unique()}")
            
            # Process the data
            forward_processor.process_data()
            print(f"Forward players processed: {len(forward_processor.player_data)}")
        
    except Exception as e:
        print(f"Error testing OutfieldDataProcessor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_position_detection()
