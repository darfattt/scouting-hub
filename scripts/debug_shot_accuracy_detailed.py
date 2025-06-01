#!/usr/bin/env python3
"""
Detailed debugging script to find why shot accuracy is showing 0.
This script will trace the entire data flow from CSV to display.
"""

import os
import sys
import pandas as pd

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def debug_shot_accuracy_detailed():
    """Detailed debugging of shot accuracy calculation."""
    print("=" * 80)
    print("DETAILED SHOT ACCURACY DEBUGGING")
    print("=" * 80)
    
    # Step 1: Check raw CSV data
    print("\n🔍 STEP 1: CHECKING RAW CSV DATA")
    print("-" * 50)
    
    data_dir = "data/stats"
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    outfield_files = []
    for filename in csv_files:
        file_path = os.path.join(data_dir, filename)
        try:
            df = pd.read_csv(file_path)
            # Check if it's an outfield player (has 'Shots' column)
            if 'Shots' in df.columns:
                outfield_files.append(filename)
                print(f"✅ Outfield file: {filename}")
                
                # Check shot data
                total_shots = df['Shots'].sum()
                if 'Shots On Target' in df.columns:
                    total_shots_on_target = df['Shots On Target'].sum()
                elif 'Shots on target' in df.columns:
                    total_shots_on_target = df['Shots on target'].sum()
                else:
                    total_shots_on_target = 0
                    print(f"   ⚠️  No 'Shots On Target' column found!")
                
                print(f"   Total shots: {total_shots}")
                print(f"   Total shots on target: {total_shots_on_target}")
                
                if total_shots > 0:
                    accuracy = (total_shots_on_target / total_shots) * 100
                    print(f"   Raw accuracy: {accuracy:.1f}%")
                else:
                    print(f"   No shots recorded")
                print()
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
    
    print(f"Found {len(outfield_files)} outfield player files")
    
    # Step 2: Check data processor
    print("\n🔍 STEP 2: CHECKING DATA PROCESSOR")
    print("-" * 50)
    
    try:
        from core.data_processor import OutfieldDataProcessor
        
        processor = OutfieldDataProcessor()
        
        # Check the load_data method
        print("Loading data...")
        raw_data = processor.load_data()
        print(f"Raw data shape: {raw_data.shape}")
        print(f"Raw data columns: {list(raw_data.columns)}")
        
        # Check for shot columns
        shot_columns = [col for col in raw_data.columns if 'shot' in col.lower()]
        print(f"Shot-related columns: {shot_columns}")
        
        # Check actual shot data
        if 'Shots' in raw_data.columns:
            total_shots = raw_data['Shots'].sum()
            print(f"Total shots in raw data: {total_shots}")
        
        if 'Shots On Target' in raw_data.columns:
            total_shots_on_target = raw_data['Shots On Target'].sum()
            print(f"Total shots on target in raw data: {total_shots_on_target}")
        elif 'Shots on target' in raw_data.columns:
            total_shots_on_target = raw_data['Shots on target'].sum()
            print(f"Total shots on target in raw data: {total_shots_on_target}")
        
        # Process data
        print("\nProcessing data...")
        processed_data = processor.process_data()
        print(f"Processed {len(processed_data)} players")
        
        # Check processed shot accuracy
        for i, (player_name, stats) in enumerate(processed_data.items()):
            if i >= 3:  # Check first 3 players
                break
                
            print(f"\nPlayer {i+1}: {player_name}")
            print(f"  shots: {stats.get('shots', 'NOT_FOUND')}")
            print(f"  shots_on_target: {stats.get('shots_on_target', 'NOT_FOUND')}")
            print(f"  shot_accuracy: {stats.get('shot_accuracy', 'NOT_FOUND')}")
            
            # Check all keys containing 'shot'
            shot_keys = [key for key in stats.keys() if 'shot' in key.lower()]
            print(f"  All shot-related keys: {shot_keys}")
            
            # Manual calculation
            shots = stats.get('shots', 0)
            shots_on_target = stats.get('shots_on_target', 0)
            if shots > 0:
                manual_accuracy = (shots_on_target / shots) * 100
                print(f"  Manual calculation: {manual_accuracy:.1f}%")
            else:
                print(f"  Manual calculation: No shots")
        
    except Exception as e:
        print(f"❌ Error with data processor: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Check the exact process_data method
    print("\n🔍 STEP 3: CHECKING PROCESS_DATA METHOD")
    print("-" * 50)
    
    try:
        # Let's manually trace through the process_data method
        processor = OutfieldDataProcessor()
        all_data = processor.load_data()
        
        # Group by player
        grouped = all_data.groupby('Player')
        
        for i, (player_name, player_matches) in enumerate(grouped):
            if i >= 2:  # Check first 2 players
                break
                
            print(f"\nPlayer: {player_name}")
            print(f"Matches: {len(player_matches)}")
            
            # Check shot columns in this player's data
            if 'Shots' in player_matches.columns:
                shots_data = player_matches['Shots'].fillna(0)
                total_shots = shots_data.sum()
                print(f"  Shots column data: {shots_data.tolist()}")
                print(f"  Total shots: {total_shots}")
            else:
                print(f"  ❌ No 'Shots' column found!")
            
            if 'Shots On Target' in player_matches.columns:
                shots_on_target_data = player_matches['Shots On Target'].fillna(0)
                total_shots_on_target = shots_on_target_data.sum()
                print(f"  Shots On Target data: {shots_on_target_data.tolist()}")
                print(f"  Total shots on target: {total_shots_on_target}")
            elif 'Shots on target' in player_matches.columns:
                shots_on_target_data = player_matches['Shots on target'].fillna(0)
                total_shots_on_target = shots_on_target_data.sum()
                print(f"  Shots on target data: {shots_on_target_data.tolist()}")
                print(f"  Total shots on target: {total_shots_on_target}")
            else:
                print(f"  ❌ No 'Shots On Target' or 'Shots on target' column found!")
                total_shots_on_target = 0
            
            # Manual calculation
            if 'Shots' in player_matches.columns and total_shots > 0:
                accuracy = (total_shots_on_target / total_shots) * 100
                print(f"  Calculated accuracy: {accuracy:.1f}%")
            else:
                print(f"  Cannot calculate accuracy")
        
    except Exception as e:
        print(f"❌ Error in manual process_data check: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Check column names exactly
    print("\n🔍 STEP 4: CHECKING EXACT COLUMN NAMES")
    print("-" * 50)
    
    try:
        # Check the first outfield file for exact column names
        if outfield_files:
            first_file = os.path.join(data_dir, outfield_files[0])
            df = pd.read_csv(first_file)
            
            print(f"File: {outfield_files[0]}")
            print(f"All columns ({len(df.columns)}):")
            for i, col in enumerate(df.columns):
                print(f"  {i+1:2d}. '{col}'")
            
            # Look for variations of shots on target
            target_variations = [
                'Shots On Target',
                'Shots on target', 
                'Shots on Target',
                'shots on target',
                'ShotsOnTarget',
                'Shots_On_Target'
            ]
            
            print(f"\nChecking for shot target column variations:")
            for variation in target_variations:
                if variation in df.columns:
                    print(f"  ✅ Found: '{variation}'")
                else:
                    print(f"  ❌ Not found: '{variation}'")
        
    except Exception as e:
        print(f"❌ Error checking column names: {e}")

if __name__ == "__main__":
    debug_shot_accuracy_detailed()
